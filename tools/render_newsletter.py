"""Render an email-safe (table-based, inline-CSS) newsletter from a content JSON.

Usage: python tools/render_newsletter.py .tmp/<slug>/content.json

content.json:
{
  "out_dir": ".tmp/<slug>",
  "image_base_url": "images/",            # use public URLs for real sends
  "subject": "...", "subject_options": ["...", "...", "..."], "preheader": "...",
  "issue_label": "Issue #3 · 7 Oct 2026",
  "headline": "...", "dek": "...", "hero_image": {"file": "hero.png", "alt": "..."},
  "tldr": ["...", "...", "..."],
  "sections": [{"heading": "...", "paragraphs": ["..."],
                "image": {"file": "growth.png", "alt": "..."}, "callout": "optional"}],
  "stats": [{"value": "42%", "label": "..."}],
  "cta": {"heading": "...", "text": "...", "button_label": "...", "url": "https://..."},
  "sources": [{"label": "...", "url": "https://...", "date": "2026-05"}]
}
Writes newsletter.html and newsletter.txt into out_dir.
"""
import json
import re
import sys
from pathlib import Path

from jinja2 import Environment, select_autoescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import load_brand  # noqa: E402

TEMPLATE = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{{ subject }}</title>
<style>
  @media only screen and (max-width: 620px) {
    .container { width: 100% !important; }
    .pad { padding-left: 20px !important; padding-right: 20px !important; }
    .stat { display: block !important; width: 100% !important; padding-bottom: 12px !important; }
    h1 { font-size: 26px !important; }
  }
</style>
</head>
<body style="margin:0;padding:0;background:{{ c.background }};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">{{ preheader }}&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{{ c.background }};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;background:{{ c.card }};">

  <!-- Header -->
  <tr><td class="pad" style="background:{{ c.primary }};padding:22px 32px;">
    {% if brand.logo_url %}<img src="{{ brand.logo_url }}" alt="{{ brand.name }}" height="36" style="display:block;border:0;height:36px;">
    {% else %}<div style="font-family:{{ brand.heading_font_stack }};font-size:22px;font-weight:bold;color:#FFFFFF;">{{ brand.name }}</div>{% endif %}
    <div style="font-family:{{ brand.heading_font_stack }};font-size:12px;color:#FFFFFF;opacity:0.9;padding-top:4px;">{{ brand.tagline }}{% if issue_label %} &nbsp;·&nbsp; {{ issue_label }}{% endif %}</div>
  </td></tr>

  <!-- Hero -->
  <tr><td class="pad" style="padding:32px 32px 8px 32px;">
    <h1 style="margin:0 0 12px 0;font-family:{{ brand.heading_font_stack }};font-size:32px;line-height:1.2;color:{{ c.primary }};">{{ headline }}</h1>
    <p style="margin:0;font-family:{{ brand.font_stack }};font-size:18px;line-height:1.5;color:{{ c.muted }};">{{ dek }}</p>
  </td></tr>
  {% if hero_image %}<tr><td style="padding:16px 0 0 0;"><img src="{{ img(hero_image.file) }}" alt="{{ hero_image.alt }}" width="600" style="display:block;width:100%;max-width:600px;height:auto;border:0;"></td></tr>{% endif %}

  <!-- TL;DR -->
  <tr><td class="pad" style="padding:24px 32px 8px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{{ c.background }};border-left:4px solid {{ c.accent }};">
      <tr><td style="padding:16px 20px;">
        <div style="font-family:{{ brand.heading_font_stack }};font-size:12px;font-weight:bold;letter-spacing:1px;color:{{ c.accent }};text-transform:uppercase;padding-bottom:8px;">TL;DR</div>
        {% for t in tldr %}<div style="font-family:{{ brand.font_stack }};font-size:16px;line-height:1.5;color:{{ c.text }};padding:3px 0;">&bull;&nbsp; {{ t }}</div>{% endfor %}
      </td></tr>
    </table>
  </td></tr>

  <!-- Sections -->
  {% for s in sections %}
  <tr><td class="pad" style="padding:28px 32px 4px 32px;">
    <h2 style="margin:0 0 12px 0;font-family:{{ brand.heading_font_stack }};font-size:22px;line-height:1.3;color:{{ c.primary }};">{{ s.heading }}</h2>
    {% for p in s.paragraphs %}<p style="margin:0 0 14px 0;font-family:{{ brand.font_stack }};font-size:16px;line-height:1.65;color:{{ c.text }};">{{ p }}</p>{% endfor %}
    {% if s.callout %}<p style="margin:4px 0 14px 0;padding:12px 16px;background:{{ c.background }};border-left:4px solid {{ c.accent }};font-family:{{ brand.font_stack }};font-size:16px;line-height:1.5;font-style:italic;color:{{ c.primary }};">{{ s.callout }}</p>{% endif %}
  </td></tr>
  {% if s.image %}<tr><td style="padding:4px 0 8px 0;"><img src="{{ img(s.image.file) }}" alt="{{ s.image.alt }}" width="600" style="display:block;width:100%;max-width:600px;height:auto;border:0;"></td></tr>{% endif %}
  {% endfor %}

  <!-- By the numbers -->
  {% if stats %}
  <tr><td class="pad" style="padding:28px 32px 8px 32px;">
    <div style="font-family:{{ brand.heading_font_stack }};font-size:12px;font-weight:bold;letter-spacing:1px;color:{{ c.accent }};text-transform:uppercase;padding-bottom:12px;">By the numbers</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      {% for st in stats %}<td class="stat" width="{{ (100 / stats|length)|int }}%" valign="top" style="padding:0 6px;">
        <div style="background:{{ c.background }};border-top:3px solid {{ c.accent }};padding:14px 10px;text-align:center;">
          <div style="font-family:{{ brand.heading_font_stack }};font-size:26px;font-weight:bold;color:{{ c.primary }};">{{ st.value }}</div>
          <div style="font-family:{{ brand.heading_font_stack }};font-size:12px;line-height:1.4;color:{{ c.text }};padding-top:4px;">{{ st.label }}</div>
        </div></td>{% endfor %}
    </tr></table>
  </td></tr>
  {% endif %}

  <!-- CTA -->
  {% if cta %}
  <tr><td class="pad" style="padding:32px 32px 8px 32px;" align="center">
    <h2 style="margin:0 0 8px 0;font-family:{{ brand.heading_font_stack }};font-size:22px;color:{{ c.primary }};">{{ cta.heading }}</h2>
    <p style="margin:0 0 18px 0;font-family:{{ brand.font_stack }};font-size:16px;line-height:1.5;color:{{ c.text }};">{{ cta.text }}</p>
    <a href="{{ cta.url }}" style="display:inline-block;background:{{ c.primary }};color:#FFFFFF;font-family:{{ brand.heading_font_stack }};font-size:16px;font-weight:bold;text-decoration:none;padding:14px 28px;border-radius:4px;">{{ cta.button_label }}</a>
  </td></tr>
  {% endif %}

  <!-- Sources -->
  {% if sources %}
  <tr><td class="pad" style="padding:32px 32px 8px 32px;">
    <div style="font-family:{{ brand.heading_font_stack }};font-size:12px;font-weight:bold;letter-spacing:1px;color:{{ c.muted }};text-transform:uppercase;padding-bottom:6px;">Sources</div>
    {% for src in sources %}<div style="font-family:{{ brand.heading_font_stack }};font-size:12px;line-height:1.6;color:{{ c.muted }};">{{ loop.index }}. <a href="{{ src.url }}" style="color:{{ c.muted }};">{{ src.label }}</a>{% if src.date %} ({{ src.date }}){% endif %}</div>{% endfor %}
  </td></tr>
  {% endif %}

  <!-- Footer -->
  <tr><td class="pad" style="padding:28px 32px 32px 32px;">
    <p style="margin:0 0 8px 0;font-family:{{ brand.font_stack }};font-size:16px;color:{{ c.text }};">{{ brand.signoff }},<br><strong>{{ brand.name }}</strong></p>
    <p style="margin:0;font-family:{{ brand.heading_font_stack }};font-size:11px;line-height:1.5;color:{{ c.muted }};">{{ brand.footer }}</p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>
"""


def to_text(d, brand):
    lines = [d["headline"], d.get("dek", ""), "", "TL;DR"]
    lines += [f"- {t}" for t in d.get("tldr", [])]
    for s in d.get("sections", []):
        lines += ["", s["heading"].upper(), ""]
        lines += [p + "\n" for p in s["paragraphs"]]
        if s.get("callout"):
            lines.append(f"> {s['callout']}")
    if d.get("stats"):
        lines += ["", "BY THE NUMBERS"] + [f"- {s['value']}: {s['label']}" for s in d["stats"]]
    if d.get("cta"):
        c = d["cta"]
        lines += ["", c["heading"], c["text"], f"{c['button_label']}: {c['url']}"]
    if d.get("sources"):
        lines += ["", "SOURCES"] + [
            f"{i}. {s['label']} - {s['url']}" + (f" ({s['date']})" if s.get("date") else "")
            for i, s in enumerate(d["sources"], 1)]
    lines += ["", f"{brand['signoff']},", brand["name"], "", brand["footer"]]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    brand = load_brand()
    out_dir = Path(d["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    base = d.get("image_base_url", "images/")
    base = base if base.endswith("/") else base + "/"

    env = Environment(autoescape=select_autoescape(default=True, default_for_string=True))
    html = env.from_string(TEMPLATE).render(
        brand=brand, c=brand["colors"], img=lambda f: base + f,
        **{k: d.get(k) for k in ("subject", "preheader", "issue_label", "headline", "dek",
                                  "hero_image", "tldr", "sections", "stats", "cta", "sources")})
    (out_dir / "newsletter.html").write_text(html, encoding="utf-8")
    (out_dir / "newsletter.txt").write_text(to_text(d, brand), encoding="utf-8")
    print(f"wrote {out_dir / 'newsletter.html'} ({len(html.encode()) / 1024:.1f} KB)")
    print(f"wrote {out_dir / 'newsletter.txt'}")


if __name__ == "__main__":
    main()
