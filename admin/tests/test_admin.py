"""Tests for the admin portal. Run: python -m pytest admin/tests -q

Each test runs against a copy of the repo files in a temp folder (ACADEMY_ROOT),
so the real catalogue is never touched.
"""

import importlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
COPY = ["data/courses.json", "data/academy.json", ".github/workflows/simulate-event.yml",
        "simulator/send_event.py", "site/courses.js"]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    for rel in COPY:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / rel, tmp_path / rel)
    monkeypatch.setenv("ACADEMY_ROOT", str(tmp_path))
    monkeypatch.setenv("ADMIN_PASSWORD", "test-pass")
    monkeypatch.setenv("ADMIN_SECRET", "test-secret")
    sys.path.insert(0, str(REPO))
    from admin import catalog, app as app_mod
    importlib.reload(catalog)
    importlib.reload(app_mod)
    from fastapi.testclient import TestClient
    c = TestClient(app_mod.app)
    c.headers.update({"X-Requested-With": "admin-ui"})
    c.root = tmp_path
    return c


def login(c):
    r = c.post("/api/login", json={"username": "admin", "password": "test-pass"})
    assert r.status_code == 200


NEW = {
    "id": "ecg-201", "title": "Advanced ECG", "level": "Advanced", "goal": "Complex rhythms",
    "duration": "4 hours", "lessons": 8, "price": 2499, "summary": "Broad complex tachycardias and blocks.",
    "audience": "Clinicians who finished ECG Interpretation Essentials.",
    "outcomes": ["Differentiate VT from SVT", "Recognise heart blocks"],
    "tryInstead": [{"id": "ecg-101", "reason": "You are new to ECGs"}], "status": "draft",
}


def test_requires_login(client):
    assert client.get("/api/courses").status_code == 401
    assert client.post("/api/login", json={"username": "admin", "password": "nope"}).status_code == 401


def test_mutations_need_csrf_header(client):
    login(client)
    r = client.post("/api/courses", json=NEW, headers={"X-Requested-With": ""})
    assert r.status_code == 403


def test_create_validate_and_publish(client):
    login(client)
    bad = client.post("/api/courses", json={**NEW, "id": "Bad ID", "price": -5, "outcomes": []})
    assert bad.status_code == 422
    assert len(bad.json()["detail"]) >= 3

    assert client.post("/api/courses", json=NEW).status_code == 201
    assert client.post("/api/courses", json=NEW).status_code == 422  # duplicate id

    client.post("/api/publish")
    js = (client.root / "site/courses.js").read_text(encoding="utf-8")
    assert "ecg-201" not in js  # draft stays hidden

    client.post("/api/courses/ecg-201/status", json={"status": "published"})
    files = client.post("/api/publish").json()["files"]
    assert files["site/courses.js"] is True
    js = (client.root / "site/courses.js").read_text(encoding="utf-8")
    assert 'id: "ecg-201"' in js
    kb = (client.root / "kb/zia-agent-knowledge-base.md").read_text(encoding="utf-8")
    assert "## Course: Advanced ECG" in kb and "₹2,499" in kb
    wf = (client.root / ".github/workflows/simulate-event.yml").read_text(encoding="utf-8")
    assert re.search(r"options: \[[^\]]*ecg-201", wf)


def test_simulator_still_reads_generated_file(client):
    login(client)
    client.post("/api/courses", json={**NEW, "status": "published"})
    client.post("/api/courses/bls-201/status", json={"status": "retired"})
    client.post("/api/publish")
    out = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0,'simulator'); import send_event as s; c=s.load_courses();"
         "print(sorted(c)); print(c['ecg-201']['price'], c['bls-201']['title'])"],
        cwd=client.root, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "ecg-201" in out.stdout and "2499" in out.stdout
    assert "Basic Life Support Refresher" in out.stdout  # retired course still nameable


def test_retire_hides_course_and_its_recommendations(client):
    login(client)
    r = client.post("/api/courses/bls-201/status", json={"status": "retired"}).json()
    assert r["warnings"]  # ecg-101 and pharm-110 recommend it
    client.post("/api/publish")
    js = (client.root / "site/courses.js").read_text(encoding="utf-8")
    published = js.split("window.RETIRED_COURSES")[0]
    assert 'id: "bls-201"' not in published
    assert "bls-201|" not in published  # no dangling "try instead"
    guide = (client.root / "site/course-guide.html").read_text(encoding="utf-8")
    assert "Basic Life Support" not in guide


def test_ids_are_permanent_and_published_courses_cannot_be_deleted(client):
    login(client)
    r = client.put("/api/courses/ecg-101", json={**NEW, "id": "renamed", "title": "ECG Essentials 2", "tryInstead": []})
    assert r.status_code == 200 and r.json()["id"] == "ecg-101"
    client.post("/api/publish")
    client.post("/api/courses/ecg-101/status", json={"status": "draft"})
    assert client.delete("/api/courses/ecg-101").status_code == 422


def test_kb_has_no_invented_policies(client):
    login(client)
    client.post("/api/publish")
    kb = (client.root / "kb/zia-agent-knowledge-base.md").read_text(encoding="utf-8")
    assert "No refund or cancellation policy is published yet" in kb
    assert "Information not in this catalogue" in kb
