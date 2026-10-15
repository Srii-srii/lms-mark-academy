"""GitHub-mode storage, tested against an in-memory fake of the GitHub API (no network)."""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from admin.store import GitHubStore, StoreError  # noqa: E402


class FakeGitHub(GitHubStore):
    """Minimal git model: files at HEAD, a list of commits, and an optional injected race."""

    def __init__(self, files):
        super().__init__("o/r", "token")
        self.files = dict(files)
        self.commits = []
        self.race_once = False
        self.head = "c0"

    def _request(self, method, path, body=None, raw=False):
        if method == "GET" and "/contents/" in path:
            rel = path.split("/contents/")[1].split("?")[0]
            return self.files.get(rel)
        if method == "GET" and "/git/ref/heads/" in path:
            return {"object": {"sha": self.head}}
        if method == "GET" and "/git/commits/" in path:
            return {"tree": {"sha": "t-" + path.rsplit("/", 1)[1]}}
        if method == "POST" and path.endswith("/git/trees"):
            self._pending = {e["path"]: e["content"] for e in body["tree"]}
            return {"sha": "tree-new"}
        if method == "POST" and path.endswith("/git/commits"):
            self._pending_msg, self._parent = body["message"], body["parents"][0]
            return {"sha": f"c{len(self.commits) + 1}"}
        if method == "PATCH" and "/git/refs/heads/" in path:
            if self.race_once:
                self.race_once = False
                self.head = "someone-else"
                raise StoreError("not a fast-forward")
            assert self._parent == self.head
            self.files.update(self._pending)
            self.commits.append((self._pending_msg, sorted(self._pending)))
            self.head = body["sha"]
            return {}
        raise AssertionError(f"unexpected {method} {path}")


def test_one_commit_with_only_changed_files():
    gh = FakeGitHub({"a.txt": "same", "b.txt": "old"})
    result = gh.write_files({"a.txt": "same", "b.txt": "new", "c.txt": "created"}, "Publish")
    assert result == {"a.txt": False, "b.txt": True, "c.txt": True}
    assert gh.commits == [("Publish", ["b.txt", "c.txt"])]
    assert gh.read("b.txt") == "new"


def test_no_commit_when_nothing_changed():
    gh = FakeGitHub({"a.txt": "x"})
    assert gh.write_files({"a.txt": "x"}, "noop") == {"a.txt": False}
    assert gh.commits == []


def test_retries_once_when_branch_moved():
    gh = FakeGitHub({"a.txt": "x"})
    gh.race_once = True
    gh.write_files({"a.txt": "y"}, "edit")
    assert len(gh.commits) == 1 and gh.files["a.txt"] == "y"


def test_publish_in_github_mode_is_a_single_commit(monkeypatch, tmp_path):
    monkeypatch.setenv("ACADEMY_ROOT", str(tmp_path))
    import importlib
    from admin import catalog
    importlib.reload(catalog)
    files = {rel: (REPO / rel).read_text(encoding="utf-8") for rel in
             ["data/courses.json", "data/academy.json", ".github/workflows/simulate-event.yml"]}
    gh = FakeGitHub(files)
    monkeypatch.setattr(catalog, "STORE", gh)
    catalog.set_status("bls-201", "retired", "tester")      # commit 1: data only
    result = catalog.publish("tester")                        # commit 2: everything derived
    assert len(gh.commits) == 2
    msg, paths = gh.commits[1]
    assert msg == "Publish course catalogue (tester)"
    assert "site/courses.js" in paths and "kb/zia-agent-knowledge-base.md" in paths
    assert result["site/courses.js"] is True
    assert 'id: "bls-201"' not in gh.files["site/courses.js"].split("RETIRED_COURSES")[0]
    assert catalog.publish("tester")["site/courses.js"] is False   # idempotent: no new commit
    assert len(gh.commits) == 2
