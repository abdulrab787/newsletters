# Brand & Voice (fill in once, reused for every issue)

> `tools/render_newsletter.py` and `tools/make_infographic.py` read the machine-readable block at the bottom.

## Identity
- **Newsletter name:** ARI
- **Tagline:** Agents, workflows, and what actually works.
- **Sign-off:** Until next time
- **Logo URL (public, PNG, ~200px wide):** none yet (text wordmark used)

## Audience
- **Who they are:** Solo founders, builders, and professionals using autonomous AI agents and automated workflows to scale their businesses.
- **Expertise level:** Practitioner (comfortable with AI tools, not necessarily engineers).
- **What they want from each issue:** One clear takeaway they can act on this week, backed by real numbers.

## Tone
- **Adjectives:** Pragmatic, forward-thinking, technical yet accessible, value-driven.
- **Do:** Short sentences, concrete numbers, one clear takeaway per issue, say what is uncertain.
- **Don't:** Hype words ("revolutionary", "game-changing"), jargon without explanation, unsourced claims, "in today's fast-paced world".
- **Example sentence in your voice:** Most teams use agents. Few have scaled one. Here is the gap, and how to close it.

## Issue structure (fixed order)
1. Subject line (<= 50 chars) + preheader (<= 90 chars). Provide 3 subject options.
2. Hero headline + one-line dek
3. TL;DR: 3 bullets
4. 2-4 insight sections, each: heading, 2-4 short paragraphs, one stat or infographic
5. By the numbers: 3-4 stat cards
6. What to do next: one CTA
7. Sources (every number cited, with date)
8. Footer: sign-off, unsubscribe/legal text

## Quality rules
- Every number has a source and date in the research log. No unsourced claims.
- Reading time target: short ~2 min, standard ~4 min, deep ~7 min.
- Every image has alt text.
- Prefer primary sources and data from the last 24 months unless history is the point.
- Flag any claim you could only verify from one source.

## Footer / legal text
Built with Claude Code & automated pipelines. Published weekly. You are receiving this because you subscribed to ARI. Unsubscribe anytime. TODO: add postal address / sender entity if your email platform requires it.

## Design tokens (machine-readable, edit values only)
```json
{
  "name": "ARI",
  "tagline": "Agents, workflows, and what actually works.",
  "logo_url": "",
  "signoff": "Until next time",
  "footer": "Built with Claude Code & automated pipelines. Published weekly. You are receiving this because you subscribed to ARI. Unsubscribe anytime.",
  "colors": {
    "primary": "#2563EB",
    "accent": "#F59E0B",
    "background": "#F9FAFB",
    "card": "#FFFFFF",
    "text": "#1F2937",
    "muted": "#6B7280"
  },
  "font_stack": "Georgia, 'Times New Roman', serif",
  "heading_font_stack": "Arial, Helvetica, sans-serif"
}
```
