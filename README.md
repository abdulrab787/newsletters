# ARI Newsletters

Generate researched, branded, email-safe HTML newsletters with code-generated infographics. Built on the **WAT framework** (Workflows, Agents, Tools): an AI agent handles reasoning and coordination, and deterministic Python scripts handle execution.

Give it a topic and it researches sources, writes copy in the ARI brand voice, fact-checks, builds charts, renders HTML, runs QA, and uploads the result to Google Drive with a Gmail draft ready for review. It never sends email.

## How it works

| Layer | Location | Role |
|-------|----------|------|
| Workflows | [`workflows/`](workflows/) | Markdown SOPs the agent follows |
| Agent | [`CLAUDE.md`](CLAUDE.md) | Instructions for the coordinating agent |
| Tools | [`tools/`](tools/) | Python scripts that do the work |

Pipeline (see [`workflows/newsletter_generate.md`](workflows/newsletter_generate.md)):

1. Research sources, saved to `.tmp/<slug>/research.json`
2. Outline and write `content.json` in the brand voice
3. Fact-check every number
4. Build charts with `tools/make_infographic.py` (stat cards, bar, hbar, line, timeline)
5. Render with `tools/render_newsletter.py` to `newsletter.html` and `newsletter.txt`
6. QA with `tools/qa_check.py`
7. Publish with `tools/publish_newsletter.py` to Google Drive plus a Gmail draft

## Setup

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

Create a `.env` file for any API keys (it is gitignored).

### Google (Drive and Gmail)

1. In a Google Cloud project, enable the **Drive API** and **Gmail API**.
2. Create a **Desktop app** OAuth client and save it as `credentials.json` in the project root.
3. Add your Google address under OAuth consent screen > **Test users**.
4. Run any publish command. The first run opens a browser sign-in and writes `token.json`.

While the app is in Testing mode, `token.json` expires after 7 days. Delete it and sign in again, or publish the app to production. Scopes are minimal: `drive.file` and `gmail.compose`.

`credentials.json`, `token.json` and `.env` are gitignored. Never commit them.

## Usage

Ask the agent: `Newsletter on <topic>`. Optional: angle, length (short, standard or deep), date range, must-include sources.

Or run the tools directly:

```bash
python tools/make_infographic.py .tmp/<slug>/charts.json
python tools/render_newsletter.py .tmp/<slug>/content.json
python tools/qa_check.py .tmp/<slug>/content.json
python tools/publish_newsletter.py .tmp/<slug>/content.json   # --to <email>, --no-draft
```

## Customizing the brand

Edit [`workflows/brand_voice.md`](workflows/brand_voice.md). Its machine-readable block at the bottom drives the renderer and charts.

## Layout

```
.tmp/         Disposable intermediates (gitignored)
tools/        Python scripts
workflows/    Markdown SOPs
CLAUDE.md     Agent instructions
```
