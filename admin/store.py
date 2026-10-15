"""Where the catalogue files live.

LocalStore   reads and writes the repo folder on this machine (default, for local use).
GitHubStore  reads and commits through the GitHub API. Used when the portal is hosted
             (Render's disk is wiped on every restart), so every save is a commit on the
             branch and nothing is lost. Enabled by setting GITHUB_TOKEN and GITHUB_REPO.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


class StoreError(RuntimeError):
    pass


class LocalStore:
    kind = "local"

    def __init__(self, root: Path):
        self.root = root

    def read(self, rel: str, fresh: bool = False) -> str | None:
        p = self.root / rel
        return p.read_text(encoding="utf-8") if p.exists() else None

    def write_files(self, files: dict[str, str], message: str) -> dict[str, bool]:
        result = {}
        for rel, text in files.items():
            path = self.root / rel
            if path.exists() and path.read_text(encoding="utf-8") == text:
                result[rel] = False
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            os.replace(tmp, path)
            result[rel] = True
        return result


class GitHubStore:
    kind = "github"
    CACHE_SECONDS = 30

    def __init__(self, repo: str, token: str, branch: str = "main", api: str = "https://api.github.com"):
        self.repo, self.token, self.branch, self.api = repo, token, branch, api.rstrip("/")
        self._cache: dict[str, tuple[str | None, float]] = {}

    # -- HTTP
    def _request(self, method: str, path: str, body: dict | None = None, raw: bool = False):
        req = urllib.request.Request(
            f"{self.api}{path}", method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.raw+json" if raw else "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "lms-mark-academy-admin",
                **({"Content-Type": "application/json"} if body is not None else {}),
            })
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                return data.decode("utf-8") if raw else json.loads(data or b"null")
        except urllib.error.HTTPError as e:
            if e.code == 404 and method == "GET":
                return None
            detail = e.read().decode("utf-8", "replace")[:300]
            raise StoreError(f"GitHub {method} {path} failed ({e.code}): {detail}") from None
        except urllib.error.URLError as e:
            raise StoreError(f"GitHub unreachable: {e.reason}") from None

    # -- reads
    def read(self, rel: str, fresh: bool = False) -> str | None:
        hit = self._cache.get(rel)
        if hit and not fresh and time.time() - hit[1] < self.CACHE_SECONDS:
            return hit[0]
        text = self._request("GET", f"/repos/{self.repo}/contents/{rel}?ref={self.branch}", raw=True)
        self._cache[rel] = (text, time.time())
        return text

    # -- writes: all changed files in ONE commit
    def write_files(self, files: dict[str, str], message: str) -> dict[str, bool]:
        for attempt in range(2):
            current = {rel: self.read(rel, fresh=True) for rel in files}
            changed = {rel: text for rel, text in files.items() if current[rel] != text}
            if not changed:
                return {rel: False for rel in files}
            ref = self._request("GET", f"/repos/{self.repo}/git/ref/heads/{self.branch}")
            if not ref:
                raise StoreError(f"branch {self.branch} not found in {self.repo}")
            head = ref["object"]["sha"]
            base_tree = self._request("GET", f"/repos/{self.repo}/git/commits/{head}")["tree"]["sha"]
            tree = self._request("POST", f"/repos/{self.repo}/git/trees", {
                "base_tree": base_tree,
                "tree": [{"path": rel, "mode": "100644", "type": "blob", "content": text}
                         for rel, text in changed.items()],
            })["sha"]
            commit = self._request("POST", f"/repos/{self.repo}/git/commits",
                                   {"message": message, "tree": tree, "parents": [head]})["sha"]
            try:
                self._request("PATCH", f"/repos/{self.repo}/git/refs/heads/{self.branch}",
                              {"sha": commit, "force": False})
            except StoreError:
                if attempt == 0:
                    continue  # someone else pushed meanwhile: re-read and rebuild the commit once
                raise
            now = time.time()
            for rel, text in changed.items():
                self._cache[rel] = (text, now)
            self.last_commit = commit
            return {rel: rel in changed for rel in files}
        raise StoreError("could not commit after retry")


def from_env(root: Path):
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPO")
    if token and repo:
        return GitHubStore(repo, token, os.environ.get("GITHUB_BRANCH", "main"))
    return LocalStore(root)

