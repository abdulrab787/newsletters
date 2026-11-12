"""QA a rendered newsletter. Exit code 1 if any hard failure.

Usage: python tools/qa_check.py .tmp/<slug>/content.json
Checks: subject/preheader length, Gmail clip size, images exist + have alt,
every section has a source, links are well-formed, spam-trigger words, placeholder text.
"""
import json
import re
import sys
from pathlib import Path

SPAM_WORDS = ["free!!!", "act now", "100% free", "guaranteed", "click here", "winner", "no obligation"]


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(d["out_dir"])
    html_path = out / "newsletter.html"
    fails, warns = [], []

    if not html_path.exists():
        raise SystemExit("newsletter.html missing - run render_newsletter.py first")
    html = html_path.read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", html)

    if len(d.get("subject", "")) > 50:
        fails.append(f"subject is {len(d['subject'])} chars (max 50)")
    if len(d.get("preheader", "")) > 90:
        warns.append(f"preheader is {len(d['preheader'])} chars (aim <= 90)")
    if len(d.get("subject_options", [])) < 3:
        warns.append("fewer than 3 subject line options")

    kb = len(html.encode()) / 1024
    if kb > 102:
        fails.append(f"HTML is {kb:.0f} KB - Gmail clips above ~102 KB")

    images = [d["hero_image"]] if d.get("hero_image") else []
    images += [s["image"] for s in d.get("sections", []) if s.get("image")]
    for im in images:
        if not (out / "images" / im["file"]).exists():
            fails.append(f"missing image file: {im['file']}")
        if not im.get("alt", "").strip():
            fails.append(f"image {im['file']} has no alt text")

    if not d.get("sources"):
        fails.append("no sources listed")
    for src in d.get("sources", []):
        if not re.match(r"^https?://", src.get("url", "")):
            fails.append(f"bad source URL: {src.get('url')!r}")
    if d.get("cta") and not re.match(r"^https?://", d["cta"].get("url", "")):
        fails.append("CTA url is not http(s)")

    for w in SPAM_WORDS:
        if w in text.lower():
            warns.append(f"spam-trigger phrase: {w!r}")
    if re.search(r"TODO|lorem ipsum|\{\{|\}\}", html, re.I):
        fails.append("placeholder text left in HTML (TODO / lorem / {{ }})")
    if "Your Newsletter" in html:
        warns.append("brand still has default name - fill in workflows/brand_voice.md")

    words = len(re.sub(r"\s+", " ", text).split())
    print(f"size: {kb:.1f} KB | ~{words} words | ~{max(1, round(words / 220))} min read")
    for w in warns:
        print(f"WARN: {w}")
    for f in fails:
        print(f"FAIL: {f}")
    print("QA PASSED" if not fails else "QA FAILED")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
