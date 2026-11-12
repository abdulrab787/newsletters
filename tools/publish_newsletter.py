"""Upload a rendered newsletter to Google Drive with public image links, then create a Gmail draft.

Usage: python tools/publish_newsletter.py .tmp/<slug>/content.json [--to you@example.com] [--no-draft]

Steps: Drive folder "ARI Newsletters/<slug>" -> upload PNGs (link-shareable) -> rewrite image
src in newsletter.html to the hosted URLs (writes newsletter_hosted.html) -> upload html/txt/research
-> Gmail draft (HTML + plain-text) addressed to --to (default: the authenticated account).
"""
import argparse
import base64
import json
import mimetypes
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from googleapiclient.http import MediaFileUpload

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import load_brand  # noqa: E402
from google_auth import drive_service, gmail_service  # noqa: E402

FOLDER_MIME = "application/vnd.google-apps.folder"


def find_or_create_folder(drive, name, parent=None):
    q = f"name = '{name}' and mimeType = '{FOLDER_MIME}' and trashed = false"
    if parent:
        q += f" and '{parent}' in parents"
    hits = drive.files().list(q=q, fields="files(id)", spaces="drive").execute()["files"]
    if hits:
        return hits[0]["id"]
    meta = {"name": name, "mimeType": FOLDER_MIME}
    if parent:
        meta["parents"] = [parent]
    return drive.files().create(body=meta, fields="id").execute()["id"]


def upload(drive, path, parent, public=False):
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    existing = drive.files().list(
        q=f"name = '{path.name}' and '{parent}' in parents and trashed = false",
        fields="files(id)").execute()["files"]
    media = MediaFileUpload(str(path), mimetype=mime)
    if existing:
        fid = drive.files().update(fileId=existing[0]["id"], media_body=media, fields="id").execute()["id"]
    else:
        fid = drive.files().create(body={"name": path.name, "parents": [parent]},
                                   media_body=media, fields="id").execute()["id"]
    if public:
        drive.permissions().create(fileId=fid, body={"type": "anyone", "role": "reader"}).execute()
    return fid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("--to")
    ap.add_argument("--no-draft", action="store_true")
    args = ap.parse_args()

    d = json.loads(Path(args.content).read_text(encoding="utf-8"))
    out = Path(d["out_dir"])
    slug = out.name
    brand = load_brand()
    drive = drive_service()

    root_id = find_or_create_folder(drive, f"{brand['name']} Newsletters")
    folder_id = find_or_create_folder(drive, slug, root_id)

    html = (out / "newsletter.html").read_text(encoding="utf-8")
    for png in sorted((out / "images").glob("*.png")):
        fid = upload(drive, png, folder_id, public=True)
        url = f"https://lh3.googleusercontent.com/d/{fid}"
        html = html.replace(f"images/{png.name}", url)
        print(f"image {png.name} -> {url}")

    hosted = out / "newsletter_hosted.html"
    hosted.write_text(html, encoding="utf-8")
    for f in (hosted, out / "newsletter.txt", out / "research.json"):
        upload(drive, f, folder_id)
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"Drive folder: {folder_url}")

    if args.no_draft:
        return
    gmail = gmail_service()
    to = args.to or gmail.users().getProfile(userId="me").execute()["emailAddress"]
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["Subject"] = d["subject"]
    msg.attach(MIMEText((out / "newsletter.txt").read_text(encoding="utf-8"), "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = gmail.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    print(f"Gmail draft created (id {draft['id']}) to {to}. Open Gmail > Drafts.")


if __name__ == "__main__":
    main()
