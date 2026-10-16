"""Course catalogue: storage, validation and the generated files.

data/courses.json is the single source of truth. publish() regenerates:
  site/courses.js                      read by the website and the event simulator
  site/course-guide.html               plain-HTML guide the SalesIQ bot is trained on
  bot/answer-hub-articles.md           SalesIQ Answer Hub articles
  kb/zia-agent-knowledge-base.md       upload to Zia Agents > Knowledge Base
  kb/zia-agent-instructions.md         paste into the Zia agent's instructions
  .github/workflows/simulate-event.yml course choices of the simulator workflow
"""

from __future__ import annotations

import html
import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from .store import StoreError, from_env  # noqa: F401  (StoreError re-exported for app.py)

ROOT = Path(os.environ.get("ACADEMY_ROOT", Path(__file__).resolve().parent.parent))
DATA = ROOT / "data"
COURSES_JSON = DATA / "courses.json"
ACADEMY_JSON = DATA / "academy.json"
AUDIT_LOG = DATA / "audit.log"
STORE = from_env(ROOT)  # local folder, or GitHub commits when GITHUB_TOKEN/GITHUB_REPO are set

LEVELS = ["Beginner", "Intermediate", "Advanced", "All levels"]
STATUSES = ["draft", "published", "retired"]
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEXT_FIELDS = {"title": 80, "duration": 30, "summary": 400, "audience": 400, "goal": 80}

_lock = threading.Lock()


class ValidationError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


# ---------------------------------------------------------------- storage

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_courses(fresh: bool = False) -> list[dict]:
    data = json.loads(STORE.read("data/courses.json", fresh=fresh))
    return sorted(data["courses"], key=lambda c: (c.get("order", 0), c["id"]))


def _courses_text(courses: list[dict]) -> str:
    return json.dumps({"courses": courses}, ensure_ascii=False, indent=2) + "\n"


def save_courses(courses: list[dict], message: str) -> None:
    STORE.write_files({"data/courses.json": _courses_text(courses)}, message)


def load_academy(fresh: bool = False) -> dict:
    return json.loads(STORE.read("data/academy.json", fresh=fresh))


def save_academy(info: dict, message: str) -> None:
    STORE.write_files({"data/academy.json": json.dumps(info, ensure_ascii=False, indent=2) + "\n"}, message)


def audit(user: str, action: str, detail: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": _now(), "user": user, "action": action, **detail}, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- validation

def clean_course(raw: dict, existing: list[dict], creating: bool) -> dict:
    """Return a normalised course or raise ValidationError with every problem found."""
    errors: list[str] = []
    c: dict = {}
    cid = str(raw.get("id", "")).strip().lower()
    if not ID_RE.match(cid) or len(cid) > 40:
        errors.append("id: use lower-case letters, numbers and single hyphens, e.g. 'ecg-201' (max 40)")
    ids = {x["id"] for x in existing}
    if creating and cid in ids:
        errors.append(f"id: '{cid}' already exists")
    c["id"] = cid

    for field, limit in TEXT_FIELDS.items():
        val = " ".join(str(raw.get(field, "")).split())
        if not val:
            errors.append(f"{field}: required")
        elif len(val) > limit:
            errors.append(f"{field}: at most {limit} characters")
        if '"' in val and field == "title":
            errors.append("title: double quotes are not allowed (the event simulator can't read them)")
        c[field] = val

    level = raw.get("level")
    if level not in LEVELS:
        errors.append(f"level: one of {', '.join(LEVELS)}")
    c["level"] = level

    for field, lo, hi in (("price", 0, 1_000_000), ("lessons", 1, 500)):
        try:
            n = int(raw.get(field))
            if not lo <= n <= hi or str(n) != str(raw.get(field)).strip():
                raise ValueError
            c[field] = n
        except (TypeError, ValueError):
            errors.append(f"{field}: whole number between {lo} and {hi}")

    outcomes = [" ".join(str(o).split()) for o in raw.get("outcomes") or [] if str(o).strip()]
    if not 1 <= len(outcomes) <= 8:
        errors.append("outcomes: between 1 and 8 learning outcomes")
    c["outcomes"] = outcomes

    alts = []
    for t in raw.get("tryInstead") or []:
        tid = str(t.get("id", "")).strip()
        reason = " ".join(str(t.get("reason", "")).split()).rstrip(".")
        if not tid:
            continue
        if tid == cid:
            errors.append("tryInstead: a course can't recommend itself")
        elif tid not in ids:
            errors.append(f"tryInstead: unknown course '{tid}'")
        elif not reason:
            errors.append(f"tryInstead: give a reason for '{tid}'")
        alts.append({"id": tid, "reason": reason})
    if len(alts) > 3:
        errors.append("tryInstead: at most 3 alternatives")
    c["tryInstead"] = alts

    status = raw.get("status", "draft")
    if status not in STATUSES:
        errors.append(f"status: one of {', '.join(STATUSES)}")
    c["status"] = status

    if errors:
        raise ValidationError(errors)
    return c


def referenced_by(courses: list[dict], cid: str) -> list[str]:
    return [c["id"] for c in courses if any(t["id"] == cid for t in c.get("tryInstead", []))]


# ---------------------------------------------------------------- mutations

def create_course(raw: dict, user: str) -> dict:
    with _lock:
        courses = load_courses(fresh=True)
        c = clean_course(raw, courses, creating=True)
        c["order"] = max((x.get("order", 0) for x in courses), default=0) + 1
        c["created_at"] = c["updated_at"] = _now()
        courses.append(c)
        save_courses(courses, f"Admin: add course {c['id']} ({user})")
        audit(user, "create", {"id": c["id"], "status": c["status"]})
        return c


def update_course(cid: str, raw: dict, user: str) -> dict:
    with _lock:
        courses = load_courses(fresh=True)
        old = next((x for x in courses if x["id"] == cid), None)
        if old is None:
            raise KeyError(cid)
        raw = {**raw, "id": cid}  # ids are permanent: events and CRM records use them
        c = clean_course(raw, courses, creating=False)
        for keep in ("order", "created_at"):
            if keep in old:
                c[keep] = old[keep]
        c["updated_at"] = _now()
        courses[courses.index(old)] = c
        save_courses(courses, f"Admin: edit course {cid} ({user})")
        changed = sorted(k for k in c if k != "updated_at" and old.get(k) != c.get(k))
        audit(user, "update", {"id": cid, "fields": changed})
        return c


def set_status(cid: str, status: str, user: str) -> tuple[dict, list[str]]:
    if status not in STATUSES:
        raise ValidationError([f"status: one of {', '.join(STATUSES)}"])
    with _lock:
        courses = load_courses(fresh=True)
        c = next((x for x in courses if x["id"] == cid), None)
        if c is None:
            raise KeyError(cid)
        if c["status"] == "retired" and status == "draft":
            raise ValidationError(["a retired course can only be republished"])
        before = c["status"]
        c["status"], c["updated_at"] = status, _now()
        save_courses(courses, f"Admin: {cid} {before} -> {status} ({user})")
        audit(user, "status", {"id": cid, "from": before, "to": status})
        warnings = []
        if status != "published":
            refs = [r for r in referenced_by(courses, cid)
                    if next(x for x in courses if x["id"] == r)["status"] == "published"]
            if refs:
                warnings.append(f"{', '.join(refs)} recommend this course; that advice is hidden until you republish it or edit them")
        return c, warnings


def delete_course(cid: str, user: str) -> None:
    """Only drafts that were never published can be deleted; published courses are retired."""
    with _lock:
        courses = load_courses(fresh=True)
        c = next((x for x in courses if x["id"] == cid), None)
        if c is None:
            raise KeyError(cid)
        if c["status"] != "draft" or c.get("published_once"):
            raise ValidationError(["only unpublished drafts can be deleted; retire published courses instead"])
        refs = referenced_by(courses, cid)
        if refs:
            raise ValidationError([f"remove it from 'try instead' in {', '.join(refs)} first"])
        courses.remove(c)
        save_courses(courses, f"Admin: delete draft {cid} ({user})")
        audit(user, "delete", {"id": cid})


def reorder(ids: list[str], user: str) -> list[dict]:
    with _lock:
        courses = load_courses(fresh=True)
        if sorted(ids) != sorted(c["id"] for c in courses):
            raise ValidationError(["order must list every course id exactly once"])
        pos = {cid: i + 1 for i, cid in enumerate(ids)}
        for c in courses:
            c["order"] = pos[c["id"]]
        save_courses(courses, f"Admin: reorder courses ({user})")
        audit(user, "reorder", {"order": ids})
        return sorted(courses, key=lambda c: c["order"])


def update_academy(raw: dict, user: str) -> dict:
    with _lock:
        info = load_academy(fresh=True)
        for key in info:
            if key in raw:
                info[key] = " ".join(str(raw[key]).split())
        save_academy(info, f"Admin: edit academy info ({user})")
        audit(user, "academy", {"fields": sorted(k for k in raw if k in info)})
        return info


# ---------------------------------------------------------------- generated files

def _price(n: int) -> str:
    return "₹" + f"{n:,}"


def _js_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def _js_block(c: dict) -> str:
    # Keep this exact layout: simulator/send_event.py reads id/title/price/lessons
    # with regexes over "  {" ... "\n  }" blocks and unquoted keys.
    alts = [f'{t["id"]}|{t["reason"]}' for t in c["tryInstead"]]
    lines = [
        "  {",
        f"    id: {_js_str(c['id'])},",
        f"    title: {_js_str(c['title'])},",
        f"    level: {_js_str(c['level'])},",
        f"    duration: {_js_str(c['duration'])},",
        f"    price: {c['price']},",
        f"    lessons: {c['lessons']},",
        f"    summary: {_js_str(c['summary'])},",
        f"    outcomes: [{', '.join(_js_str(o) for o in c['outcomes'])}],",
        f"    audience: {_js_str(c['audience'])},",
        f"    goal: {_js_str(c['goal'])},",
        "    tryInstead: [",
        *[f"      {_js_str(a)}," for a in alts],
        "    ],",
        "  },",
    ]
    return "\n".join(lines)


def _visible(courses: list[dict]) -> list[dict]:
    """Published courses, with 'try instead' advice pointing only at published courses."""
    pub = [dict(c) for c in courses if c["status"] == "published"]
    ids = {c["id"] for c in pub}
    for c in pub:
        c["tryInstead"] = [t for t in c["tryInstead"] if t["id"] in ids]
    return pub


def render_courses_js(courses: list[dict]) -> str:
    pub = _visible(courses)
    retired = [c for c in courses if c["status"] == "retired"]
    return (
        "// GENERATED by admin/catalog.py from data/courses.json. Edit courses in the admin portal,\n"
        "// not here. Prices in INR. Ids must match what the event simulator sends.\n"
        "window.COURSES = [\n" + "\n".join(_js_block(c) for c in pub) + "\n];\n\n"
        "// Retired courses: hidden from the site, kept so course.retired events can name them.\n"
        "window.RETIRED_COURSES = [\n" + "\n".join(_js_block(c) for c in retired) + "\n];\n\n"
        'window.formatPrice = (n) => "₹" + n.toLocaleString("en-IN");\n'
    )


def render_course_guide(courses: list[dict], academy: dict) -> str:
    pub = _visible(courses)
    by_id = {c["id"]: c for c in pub}
    e = html.escape
    site = academy["site_url"]
    cards = []
    for c in pub:
        alts = "".join(
            f'<li><a href="#{e(t["id"])}">{e(by_id[t["id"]]["title"])}</a>: {e(t["reason"])}.</li>'
            for t in c["tryInstead"])
        cards.append(f"""
    <article class="panel guide-course" id="{e(c['id'])}">
      <h2>{e(c['title'])}</h2>
      <p class="meta">{e(c['level'])} · {e(c['duration'])} · {c['lessons']} lessons · {_price(c['price'])} · certificate included</p>
      <p><strong>Topic:</strong> {e(c['goal'])}</p>
      <p>{e(c['summary'])}</p>
      <p><strong>Who it's for:</strong> {e(c['audience'])}</p>
      <p><strong>You will learn:</strong> {e('; '.join(c['outcomes']))}.</p>""" + (f"""
      <p><strong>Not the right fit? Try instead:</strong></p>
      <ul>{alts}</ul>""" if alts else "") + f"""
      <p><a href="{e(site)}/course.html?id={e(c['id'])}">View course page</a></p>
    </article>""")
    picker = "".join(
        f"<li><strong>{e(c['goal'])}</strong>: {e(c['title'])} ({e(c['level'])}, {e(c['duration'])})</li>" for c in pub)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Course guide · {e(academy['name'])}</title>
  <meta name="description" content="Every {e(academy['name'])} course: who it's for, what you learn, price, and which course to try instead.">
  <link rel="stylesheet" href="styles.css?v=9">
  <script src="zoho-config.js?v=9"></script>
  <script src="courses.js?v=9"></script>
  <script src="app.js?v=9"></script>
</head>
<body data-page="guide">
  <header id="site-header"></header>
  <!-- GENERATED by admin/catalog.py from data/courses.json. Do not edit by hand. -->
  <main class="wrap prose">
    <h1>Course guide</h1>
    <p>Not sure where to start, or a course isn't quite right for you? Pick by what you want to get better at:</p>
    <ul>{picker}</ul>
    <p>{e(academy['course_format'])}</p>
    {''.join(cards)}
  </main>
  <footer id="site-footer"></footer>
</body>
</html>
"""


def render_answer_hub(courses: list[dict], academy: dict) -> str:
    pub = _visible(courses)
    by_id = {c["id"]: c for c in pub}
    site = academy["site_url"]
    cheapest = min(pub, key=lambda c: c["price"]) if pub else None
    chooser = (
        "## Which course should I choose?\n\n"
        f"**Title for Answer Hub:** Which {academy['name']} course should I choose?\n\n"
        "Choose by what you want to get better at:\n"
        + "".join(f"- {c['goal']}: {c['title']} ({c['level']}, {c['duration']}, {_price(c['price'])})\n" for c in pub)
        + (f"\nLowest price: {cheapest['title']} ({cheapest['duration']}, {_price(cheapest['price'])}). " if cheapest else "\n")
        + f"Full guide: {site}/course-guide.html\n"
    )
    articles = []
    for c in pub:
        alts = "".join(
            f"- {by_id[t['id']]['title']} ({by_id[t['id']]['duration']}, {_price(by_id[t['id']]['price'])}): {t['reason']}.\n"
            for t in c["tryInstead"])
        articles.append(
            f"## {c['title']}\n\n"
            f"**Title for Answer Hub:** {c['title']}: who it's for and what to try instead\n\n"
            f"{c['title']} is a course on {c['goal'][0].lower() + c['goal'][1:]} (level: {c['level']}). {c['summary']} "
            f"It takes {c['duration']} over {c['lessons']} lessons and costs {_price(c['price'])}, with a certificate on completion.\n\n"
            f"Who it's for: {c['audience']}\n\n"
            f"You will learn: {'; '.join(c['outcomes'])}.\n\n"
            + (f"If this course isn't useful for you, try:\n{alts}\n" if alts else "")
            + f"Course page: {site}/course.html?id={c['id']}\n")
    return ("# Answer Hub articles for the SalesIQ bot\n\nGENERATED from data/courses.json. Paste each section into "
            "SalesIQ → Answer Hub → Articles → Compose, using the title shown.\n\n" + chooser + "\n" + "\n".join(articles))


def academy_placeholder(what: str) -> str:
    return (f"No {what} is published yet. Do not describe one. Tell the learner the team will confirm it, "
            "and offer to connect them with a person.")


def render_zia_kb(courses: list[dict], academy: dict) -> str:
    """Knowledge base for Zia Agents (upload as Markdown; Zia accepts PDF, text and Markdown).

    Built for retrieval: one heading per course, each section self-contained (it repeats the
    course name, price and level), short paragraphs, no facts that are not in the catalogue.
    """
    pub = _visible(courses)
    by_id = {c["id"]: c for c in pub}
    name, site = academy["name"], academy["site_url"]
    out = [
        f"# {name}: course catalogue knowledge base",
        "",
        f"Source: the {name} course catalogue. "
        f"Prices are in Indian rupees (INR). {len(pub)} courses are open for enrolment.",
        "",
        f"## What courses does {name} offer? (complete list)",
        "",
        f"{name} offers exactly {len(pub)} courses. This is the complete list; no other courses exist:",
        "",
        *[f"{i}. {c['title']}: {c['level']}, {c['duration']}, {c['lessons']} lessons, {_price(c['price'])}. "
          f"Topic: {c['goal']}. Course page: {site}/course.html?id={c['id']}"
          for i, c in enumerate(pub, 1)],
        "",
        f"Never name, describe or price any course that is not in this list. If no course fits what the learner "
        f"wants, say so and suggest the closest of these {len(pub)} courses.",
        "",
        "Common questions this list answers: what courses do you have, suggest me a course, recommend a course, "
        "which course should I take, list all courses, course fees, course prices, cheapest course.",
        "",
        "## About the academy",
        "",
        f"{name}: {academy['tagline']}",
        "",
        f"Course format: {academy['course_format']}",
        "",
        f"Website: {site}. All courses: {site}/courses.html. Course guide: {site}/course-guide.html.",
        "",
        "## All courses at a glance",
        "",
        "| Course | Course ID | Topic | Level | Duration | Lessons | Price |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        *[f"| {c['title']} | {c['id']} | {c['goal']} | {c['level']} | {c['duration']} | {c['lessons']} | {_price(c['price'])} |" for c in pub],
        "",
    ]
    if pub:
        by_price = sorted(pub, key=lambda c: c["price"])
        out += [
            "## How to choose a course",
            "",
            "By what the learner wants to get better at:",
            "",
            *[f"- {c['goal']}: {c['title']} ({c['level']}, {_price(c['price'])})." for c in pub],
            "",
            "By level:",
            "",
            *[f"- {lvl}: " + ", ".join(c["title"] for c in pub if c["level"] == lvl) + "."
              for lvl in LEVELS if any(c["level"] == lvl for c in pub)],
            "",
            f"By price, lowest first: " + "; ".join(f"{c['title']} {_price(c['price'])}" for c in by_price) + ".",
            "",
            f"Lowest price: {by_price[0]['title']} at {_price(by_price[0]['price'])}. "
            f"Highest price: {by_price[-1]['title']} at {_price(by_price[-1]['price'])}.",
            "",
        ]
    for c in pub:
        out += [
            f"## Course: {c['title']}",
            "",
            f"- Course ID: {c['id']}",
            f"- Topic: {c['goal']}",
            f"- Level: {c['level']}",
            f"- Duration: {c['duration']} over {c['lessons']} lessons",
            f"- Price: {_price(c['price'])} (INR)",
            f"- Certificate: yes, on completion",
            f"- Course page: {site}/course.html?id={c['id']}",
            "",
            f"What it covers: {c['summary']}",
            "",
            f"Who {c['title']} is for: {c['audience']}",
            "",
            f"What learners learn in {c['title']}:",
            "",
            *[f"- {o}" for o in c["outcomes"]],
            "",
        ]
        if c["tryInstead"]:
            out += [f"If {c['title']} is not the right fit, suggest:", ""]
            out += [f"- {by_id[t['id']]['title']} ({by_id[t['id']]['level']}, {_price(by_id[t['id']]['price'])}) when {t['reason'][0].lower() + t['reason'][1:]}." for t in c["tryInstead"]]
            out += [""]
    out += [
        "## Enrolment, payment and support",
        "",
        f"How to enrol: {academy['how_to_enrol']}",
        "",
        f"How to get help: {academy['how_to_get_help']}",
        "",
        f"Refunds and cancellations: {academy['refund_policy'] or academy_placeholder('refund or cancellation policy')}",
        "",
        f"Discounts and coupons: {academy['discounts'] or academy_placeholder('discount or coupon offer')}",
        "",
        f"Privacy and marketing consent: see {academy['privacy_url']}. Learners choose email, WhatsApp and SMS updates "
        "separately and can unsubscribe at any time.",
        "",
        "## Information not in this catalogue",
        "",
        "Course start dates, live sessions, instructor names, prerequisites beyond the level shown, accreditation "
        "or CPD credits, and group or institutional pricing are not listed in this catalogue. If asked, say the "
        "information isn't published and offer to connect the learner with the team.",
        "",
    ]
    return "\n".join(out)


def render_zia_instructions(courses: list[dict], academy: dict) -> str:
    name = academy["name"]
    return f"""# Instructions for the {name} course advisor agent

Paste this into the agent's Instructions in Zia Agent Studio. Attach "{name}: course catalogue knowledge base"
(kb/zia-agent-knowledge-base.md) as the agent's knowledge base.

## Role
You help visitors and learners of {name} find the right clinical-skills course, and answer questions about
courses, prices, levels, duration, certificates and enrolment.

## Rules
1. Answer only from the knowledge base. Quote prices exactly as written, in rupees (₹).
2. If something is not in the knowledge base (start dates, refunds, discounts, accreditation, instructors),
   say it isn't published and offer to connect the learner with a person. Never guess.
3. To recommend a course, ask what they want to get better at and their experience level if you don't know,
   then suggest one course, with its price and course page link. Mention one alternative from
   "If ... is not the right fit" when it helps.
4. You are not a clinician. Don't give medical, diagnostic or treatment advice, even if asked about a patient.
   Point them to the relevant course instead, or to a qualified professional.
5. Don't ask for or repeat health information, payment card details or passwords.
6. Keep answers short: two to four sentences, or a short list when comparing courses.
7. If the learner asks to unsubscribe, delete their data, or complains, hand over to a person.
"""


def update_workflow_choices(courses: list[dict]) -> str | None:
    """Course choices in the simulator workflow: published and retired ids."""
    text = STORE.read(".github/workflows/simulate-event.yml")
    if text is None:
        return None
    ids = [c["id"] for c in courses if c["status"] in ("published", "retired")]
    block = re.compile(r"(\n      course:\n(?:        .*\n)*?        default: )(\S+)(\n(?:        .*\n)*?        options: \[)[^\]]*(\])")
    m = block.search(text)
    if not m or not ids:
        return text
    default = m.group(2) if m.group(2) in ids else ids[0]
    return text[:m.start()] + m.group(1) + default + m.group(3) + ", ".join(ids) + m.group(4) + text[m.end():]


def publish(user: str) -> dict:
    """Regenerate every derived file (one commit in GitHub mode). Returns {path: changed?}."""
    with _lock:
        courses = load_courses(fresh=True)
        academy = load_academy(fresh=True)
        if not any(c["status"] == "published" for c in courses):
            raise ValidationError(["publish at least one course first; the site would be empty"])
        for c in courses:
            if c["status"] == "published":
                c["published_once"] = True
        files = {
            "site/courses.js": render_courses_js(courses),
            "site/course-guide.html": render_course_guide(courses, academy),
            "bot/answer-hub-articles.md": render_answer_hub(courses, academy),
            "kb/zia-agent-knowledge-base.md": render_zia_kb(courses, academy),
            "kb/zia-agent-instructions.md": render_zia_instructions(courses, academy),
        }
        wf = update_workflow_choices(courses)
        if wf is not None:
            files[".github/workflows/simulate-event.yml"] = wf
        written = STORE.write_files({**files, "data/courses.json": _courses_text(courses)},
                                    f"Publish course catalogue ({user})")
        result = {rel: written[rel] for rel in files}
        audit(user, "publish", {"changed": [k for k, v in result.items() if v]})
        return result
