"""Regenerates every file derived from data/courses.json (same as Publish in the admin portal):
site/courses.js, site/course-guide.html, bot/answer-hub-articles.md, kb/zia-agent-*.md and
the course choices in .github/workflows/simulate-event.yml.

Run:  python tools/build_course_guide.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from admin import catalog  # noqa: E402

if __name__ == "__main__":
    result = catalog.publish("cli")
    for path, changed in result.items():
        print(f"{'updated  ' if changed else 'unchanged'} {path}")
