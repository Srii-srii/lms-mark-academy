"""Learner-event simulator for the omnichannel POC.

Stands in for a learning platform (TrainerCentral later) by POSTing the
standard event payload to the Zoho Flow "core" webhooks. Python stdlib only.

Webhook URLs come from environment variables, never from the repo:
  ZOHO_FLOW_WEBHOOKS  JSON object {"<event>": "<webhook url>", ...}
  ZOHO_FLOW_WEBHOOK_URL  optional single URL used for any event not in the map

Examples:
  python simulator/send_event.py --event learner.signed_up --email you@example.com --dry-run
  python simulator/send_event.py --scenario full_journey --email you@example.com --delay 60
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

EVENTS = [
    "learner.signed_up",
    "cart.updated",
    "order.completed",
    "lesson.completed",
    "course.completed",
    "consent.updated",
    # Sent once per affected learner when a course is deleted/unpublished.
    "course.retired",
]

SCENARIOS = {
    # Lead -> enrolled -> learning -> completed: every journey stage once.
    "full_journey": ["learner.signed_up", "cart.updated", "order.completed",
                     "lesson.completed", "lesson.completed", "course.completed"],
    # Lead adds to cart and never buys: should trigger the abandoned-cart reminder.
    "abandoned_cart": ["learner.signed_up", "cart.updated"],
    # Abandoned cart, then purchase: should EXIT the abandoned-cart journey.
    "cart_then_purchase": ["learner.signed_up", "cart.updated", "order.completed"],
}

STAGE_BY_EVENT = {
    "learner.signed_up": "lead",
    "cart.updated": "lead",
    "order.completed": "enrolled",
    "lesson.completed": "active",
    "course.completed": "completed",
}

# Status-specific wording for course.retired, carried in the event so Zoho needs
# no branching: the email just shows the course_notice field.
RETIRED_NOTICE = {
    "enrolled": "You're enrolled in this course. Your access stays open for now, and our team will contact you about your options.",
    "active": "You're partway through this course. Your progress and access stay open for now, and our team will contact you about your options.",
    "in_cart": "This course was in your cart. We've removed it, so you won't be charged. You can browse our other courses anytime.",
}

COURSES_FILE = Path(__file__).resolve().parent.parent / "site" / "courses.js"


def load_courses() -> dict:
    # courses.js is `window.COURSES = [...]`; pull out id/title/price without a JS parser.
    import re
    text = COURSES_FILE.read_text(encoding="utf-8")
    courses = {}
    for block in re.findall(r"\{(.*?)\n  \}", text, flags=re.S):
        cid = re.search(r'id:\s*"([^"]+)"', block)
        title = re.search(r'title:\s*"([^"]+)"', block)
        price = re.search(r"price:\s*(\d+)", block)
        lessons = re.search(r"lessons:\s*(\d+)", block)
        if cid and title and price:
            courses[cid.group(1)] = {
                "title": title.group(1),
                "price": int(price.group(1)),
                "lessons": int(lessons.group(1)) if lessons else 10,
            }
    return courses


def bool_str(yes_no: str) -> str:
    return "true" if yes_no == "yes" else "false"


def build_payload(event: str, args, courses: dict, lesson_no: int) -> dict:
    """Flat key/value payload: easiest for Zoho Flow to map field by field."""
    course = courses.get(args.course) or next(iter(courses.values()))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    site = args.site_url.rstrip("/")
    learner_id = "demo-" + uuid.uuid5(uuid.NAMESPACE_DNS, args.email.lower()).hex[:10]
    payload = {
        "schema_version": "1.0",
        "event_id": str(uuid.uuid4()),
        "event": event,
        "occurred_at": now,
        "source": "demo-simulator",
        "lifecycle_stage": STAGE_BY_EVENT.get(event, ""),
        "learner_id": learner_id,
        "learner_first_name": args.first_name,
        "learner_last_name": args.last_name,
        "learner_email": args.email,
        "learner_phone": args.phone,
        # true/false strings: ZMA checkbox fields reject anything else.
        "consent_email_marketing": bool_str(args.consent_email),
        "consent_whatsapp": bool_str(args.consent_whatsapp),
        "consent_sms": bool_str(args.consent_sms),
        "consent_captured_at": now,
        "consent_source": "demo-site-signup",
        "course_id": args.course,
        "course_title": course["title"],
        "course_price": course["price"],
        "course_url": f"{site}/course.html?id={args.course}",
        "currency": "INR",
        "order_id": "",
        "order_amount": "",
        "lesson_number": "",
        "progress_percent": "",
        "course_status": "",
        "affected_status": "",
        "course_notice": "",
        "cart_status": "active" if event == "cart.updated" else "",
    }
    if event == "order.completed":
        payload["order_id"] = "ORD-" + uuid.uuid4().hex[:8].upper()
        payload["order_amount"] = course["price"]
    if event == "lesson.completed":
        payload["lesson_number"] = lesson_no
        payload["progress_percent"] = round(100 * lesson_no / course["lessons"])
    if event == "course.completed":
        payload["progress_percent"] = 100
    if event == "course.retired":
        payload["course_status"] = "retired"
        payload["affected_status"] = args.learner_status
        payload["course_notice"] = RETIRED_NOTICE[args.learner_status]
        payload["course_url"] = f"{site}/courses.html"  # the course page no longer exists
        if args.learner_status == "in_cart":
            payload["cart_status"] = "course-retired"
    return payload


def webhook_for(event: str) -> str:
    mapping = {}
    raw = os.environ.get("ZOHO_FLOW_WEBHOOKS", "").strip()
    if raw:
        try:
            mapping = json.loads(raw)
        except json.JSONDecodeError:
            sys.exit("ZOHO_FLOW_WEBHOOKS is not valid JSON")
    return mapping.get(event) or os.environ.get("ZOHO_FLOW_WEBHOOK_URL", "").strip()


def post(url: str, payload: dict) -> None:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                print(f"  -> HTTP {resp.status}")
                return
        except urllib.error.HTTPError as e:
            print(f"  -> HTTP {e.code}: {e.read()[:300]!r}")
        except urllib.error.URLError as e:
            print(f"  -> network error: {e.reason}")
        if attempt == 1:
            time.sleep(3)
    raise SystemExit("event delivery failed after retry")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--event", choices=EVENTS)
    g.add_argument("--scenario", choices=sorted(SCENARIOS))
    p.add_argument("--email", required=True)
    p.add_argument("--first-name", default="Test")
    p.add_argument("--last-name", default="Learner")
    p.add_argument("--phone", default="", help="E.164, e.g. +919876543210")
    p.add_argument("--learner-status", default="enrolled", choices=sorted(RETIRED_NOTICE),
                   help="course.retired only: how this learner relates to the retired course")
    p.add_argument("--course", default="ecg-101")
    p.add_argument("--consent-email", default="yes", choices=["yes", "no"])
    p.add_argument("--consent-whatsapp", default="no", choices=["yes", "no"])
    p.add_argument("--consent-sms", default="no", choices=["yes", "no"])
    p.add_argument("--site-url", default=os.environ.get("SITE_URL", "https://academy.lms-mark.website"))
    p.add_argument("--delay", type=int, default=30, help="seconds between scenario steps")
    p.add_argument("--dry-run", action="store_true", help="print payloads, send nothing")
    args = p.parse_args()

    courses = load_courses()
    if args.course not in courses:
        sys.exit(f"unknown course {args.course!r}; choose from {', '.join(courses)}")

    steps = [args.event] if args.event else SCENARIOS[args.scenario]
    lesson_no = 0
    for i, event in enumerate(steps):
        if event == "lesson.completed":
            lesson_no += 1
        payload = build_payload(event, args, courses, lesson_no)
        print(f"[{i + 1}/{len(steps)}] {event}  ({payload['event_id']})")
        if args.dry_run:
            print(json.dumps(payload, indent=2))
        else:
            url = webhook_for(event)
            if not url:
                sys.exit(f"no webhook configured for {event} (set ZOHO_FLOW_WEBHOOKS)")
            post(url, payload)
        if i < len(steps) - 1 and not args.dry_run:
            time.sleep(args.delay)


if __name__ == "__main__":
    main()
