# Workflow: Generate a Newsletter

## Objective
Given a topic, produce a researched, branded, email-safe HTML newsletter with code-generated infographics, uploaded to Google Drive for review.

## Trigger
`Newsletter on <topic>` with optional: angle, length (short ~2 min / standard ~4 / deep ~7; default standard), date range, must-include sources.

## Required inputs
- Topic (from user)
- `workflows/brand_voice.md` filled in (stop and ask the user if any TODO remains or brand name is still "Your Newsletter")

## Steps
1. **Setup.** Make slug (`kebab-case-topic-YYYYMMDD`), create `.tmp/<slug>/`.
2. **Research.** Use web search (Bright Data MCP if available, else WebSearch/WebFetch). Gather 8-15 sources, prefer primary and recent. Save to `.tmp/<slug>/research.json`: `[{claim, number?, source_label, url, date, confidence}]`. Flag single-source claims.
3. **Outline.** Pick 2-4 insights + 3-4 headline stats. Check for overlap with past issues in `.tmp/archive.json` (list of `{slug, topic, date}`); avoid repeating the same angle.
4. **Write copy** in brand voice into `.tmp/<slug>/content.json` (schema in `tools/render_newsletter.py` docstring). Include 3 subject options, preheader, TL;DR, sections, stats, CTA, sources.
5. **Fact-check pass.** Re-open the source for every number in the copy and charts; fix or cut anything unverified. Do not skip.
6. **Charts.** Write `.tmp/<slug>/charts.json` (schema in `tools/make_infographic.py`; types: `stat_cards`, `bar`, `hbar`, `line`, `timeline`; set `out_dir` to `.tmp/<slug>/images`). One chart per section where there is data worth showing; every chart needs a `source`. Run `python tools/make_infographic.py .tmp/<slug>/charts.json`, then visually inspect each PNG.
7. **Render.** `python tools/render_newsletter.py .tmp/<slug>/content.json` -> `newsletter.html` + `newsletter.txt`.
8. **QA.** `python tools/qa_check.py .tmp/<slug>/content.json`. Fix any FAIL and rerun until it passes. Review WARNs.
9. **Deliver.** Run `python tools/publish_newsletter.py .tmp/<slug>/content.json` (use `--to` for another recipient, `--no-draft` for Drive only). It uploads PNGs to Drive `ARI Newsletters/<slug>/` as link-shareable, writes `newsletter_hosted.html` with public image URLs, uploads html/txt/research.json, and creates a Gmail draft (never sends). Auth is the Desktop OAuth flow in `tools/google_auth.py` (`credentials.json` -> `token.json`). The user runs this step themselves if the auto-mode permission check blocks it (it publishes images publicly and signs in with their Google account). Return to the user: Drive folder link, 3 subject options, QA summary, any low-confidence claims.
10. **Revise** on request (edit content.json/charts.json, rerun steps 6-9). On approval append to `.tmp/archive.json`.

## Edge cases / notes
- Images: relative `images/` works for local preview only. For a real send, images need public URLs: set `image_base_url` in content.json to the hosting folder URL, then rerun render.
- Never use SVG in the email; PNG only. Email clients strip modern CSS, so keep the table + inline-style template.
- Gmail clips HTML over ~102 KB; qa_check fails above that.
- Thin or conflicting research: say so in the delivery message rather than padding.
- Do not run paid generation APIs without checking with the user first.

## Lessons learned
- The Google Drive/Gmail MCP connectors were unusable (Drive: "Insufficient scope", Gmail plugin: OAuth registration error). Use the direct OAuth script instead.
- One-time Google setup: enable **both Drive API and Gmail API** in the Cloud project, create a Desktop-app OAuth client (`credentials.json`), and add the user's address under OAuth consent screen > **Test users**, otherwise sign-in fails with `403 access_denied`. API not enabled gives `accessNotConfigured` (enable, wait ~1 min, rerun).
- While the app is in Testing mode, `token.json` expires after 7 days: delete it and sign in again, or publish the app to "In production".
- Scopes are minimal: `drive.file` (only files the script creates) and `gmail.compose` (drafts only).
- Fetches of McKinsey PDF and Gartner pages timed out/403; flag figures taken from search summaries as medium confidence rather than presenting them as verified.
- Secondary/aggregator claims (X posts, roundups) were excluded or flagged; keep doing this.
