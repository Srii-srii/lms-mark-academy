"""LMS-Mark Academy admin portal (FastAPI).

Run locally:
  pip install -r admin/requirements.txt
  set ADMIN_PASSWORD=<choose one>          (PowerShell: $env:ADMIN_PASSWORD="...")
  python -m uvicorn admin.app:app --host 127.0.0.1 --port 8800
Then open http://127.0.0.1:8800

The public site stays static on GitHub Pages. "Publish" regenerates the site and bot files
from data/courses.json; "Push to GitHub" (only when ALLOW_GIT_PUSH=1) commits those files
and pushes, which redeploys the site.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import subprocess
import time

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import catalog

STATIC = catalog.Path(__file__).resolve().parent / "static"
SESSION_HOURS = 8
COOKIE = "academy_admin"

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SECRET = os.environ.get("ADMIN_SECRET") or secrets.token_hex(32)  # restart = everyone logs in again
ALLOW_GIT_PUSH = os.environ.get("ALLOW_GIT_PUSH") == "1"
GENERATED = ["data/courses.json", "data/academy.json", "site/courses.js", "site/course-guide.html",
             "bot/answer-hub-articles.md", "kb/zia-agent-knowledge-base.md", "kb/zia-agent-instructions.md",
             ".github/workflows/simulate-event.yml"]

if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = secrets.token_urlsafe(12)
    print(f"\n  ADMIN_PASSWORD not set. One-time password for this run: {ADMIN_PASSWORD}\n")

app = FastAPI(title="LMS-Mark Academy admin", docs_url=None, redoc_url=None)


# ---------------------------------------------------------------- auth

def _sign(payload: str) -> str:
    return hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def _make_token(user: str) -> str:
    payload = f"{user}|{int(time.time()) + SESSION_HOURS * 3600}"
    return f"{payload}|{_sign(payload)}"


def current_user(request: Request) -> str:
    token = request.cookies.get(COOKIE, "")
    try:
        user, exp, sig = token.split("|")
    except ValueError:
        raise HTTPException(401, "Please sign in")
    if not hmac.compare_digest(sig, _sign(f"{user}|{exp}")) or int(exp) < time.time():
        raise HTTPException(401, "Session expired, please sign in again")
    # Same-site cookie plus a custom header blocks cross-site form posts (CSRF)
    if request.method != "GET" and request.headers.get("x-requested-with") != "admin-ui":
        raise HTTPException(403, "Missing request header")
    return user


class Login(BaseModel):
    username: str
    password: str


@app.post("/api/login")
def login(body: Login, response: Response):
    ok = hmac.compare_digest(body.username, ADMIN_USER) & hmac.compare_digest(body.password, ADMIN_PASSWORD)
    if not ok:
        time.sleep(1)  # slows down password guessing
        raise HTTPException(401, "Wrong username or password")
    response.set_cookie(COOKIE, _make_token(body.username), httponly=True, samesite="strict",
                        secure=os.environ.get("COOKIE_SECURE") == "1", max_age=SESSION_HOURS * 3600)
    catalog.audit(body.username, "login", {})
    return {"user": body.username}


@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE)
    return {"ok": True}


@app.get("/api/me")
def me(user: str = Depends(current_user)):
    return {"user": user, "allow_git_push": ALLOW_GIT_PUSH, "levels": catalog.LEVELS, "statuses": catalog.STATUSES}


# ---------------------------------------------------------------- errors

@app.exception_handler(catalog.ValidationError)
def _validation(_: Request, exc: catalog.ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors})


@app.exception_handler(KeyError)
def _missing(_: Request, exc: KeyError):
    return JSONResponse(status_code=404, content={"detail": [f"no course '{exc.args[0]}'"]})


# ---------------------------------------------------------------- courses

@app.get("/api/courses")
def list_courses(user: str = Depends(current_user)):
    return catalog.load_courses()


@app.post("/api/courses", status_code=201)
def create(body: dict, user: str = Depends(current_user)):
    return catalog.create_course(body, user)


@app.put("/api/courses/{cid}")
def update(cid: str, body: dict, user: str = Depends(current_user)):
    return catalog.update_course(cid, body, user)


class StatusChange(BaseModel):
    status: str


@app.post("/api/courses/{cid}/status")
def change_status(cid: str, body: StatusChange, user: str = Depends(current_user)):
    course, warnings = catalog.set_status(cid, body.status, user)
    return {"course": course, "warnings": warnings}


@app.delete("/api/courses/{cid}")
def delete(cid: str, user: str = Depends(current_user)):
    catalog.delete_course(cid, user)
    return {"ok": True}


class Order(BaseModel):
    ids: list[str]


@app.post("/api/courses/reorder")
def reorder(body: Order, user: str = Depends(current_user)):
    return catalog.reorder(body.ids, user)


# ---------------------------------------------------------------- academy info

@app.get("/api/academy")
def get_academy(user: str = Depends(current_user)):
    return catalog.load_academy()


@app.put("/api/academy")
def put_academy(body: dict, user: str = Depends(current_user)):
    return catalog.update_academy(body, user)


# ---------------------------------------------------------------- publish & git

@app.post("/api/publish")
def publish(user: str = Depends(current_user)):
    return {"files": catalog.publish(user)}


@app.get("/api/kb")
def kb_file(user: str = Depends(current_user)):
    path = catalog.ROOT / "kb" / "zia-agent-knowledge-base.md"
    if not path.exists():
        raise HTTPException(404, "Publish first to generate the knowledge base")
    return FileResponse(path, media_type="text/markdown", filename="lms-mark-academy-knowledge-base.md")


@app.get("/api/audit")
def audit_log(user: str = Depends(current_user), limit: int = 50):
    if not catalog.AUDIT_LOG.exists():
        return []
    lines = catalog.AUDIT_LOG.read_text(encoding="utf-8").splitlines()[-limit:]
    return [catalog.json.loads(x) for x in reversed(lines)]


def _git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=catalog.ROOT, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise HTTPException(500, f"git {args[0]} failed: {out.stderr.strip()[:300]}")
    return out.stdout


@app.get("/api/git/status")
def git_status(user: str = Depends(current_user)):
    lines = _git("status", "--porcelain", "--", *GENERATED).splitlines()
    return {"changed": [ln[3:] for ln in lines], "allow_push": ALLOW_GIT_PUSH}


class Push(BaseModel):
    message: str


@app.post("/api/git/push")
def git_push(body: Push, user: str = Depends(current_user)):
    if not ALLOW_GIT_PUSH:
        raise HTTPException(403, "Pushing is off. Start the server with ALLOW_GIT_PUSH=1 to enable it.")
    msg = " ".join(body.message.split())[:120] or "Update course catalogue"
    if not _git("status", "--porcelain", "--", *GENERATED).strip():
        return {"pushed": False, "reason": "nothing to push"}
    _git("add", "--", *GENERATED)
    _git("commit", "-m", f"{msg}\n\nPublished from the admin portal by {user}.")
    _git("push")
    catalog.audit(user, "git_push", {"message": msg})
    return {"pushed": True}


# ---------------------------------------------------------------- UI

app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
