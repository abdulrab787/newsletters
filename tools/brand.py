"""Load the machine-readable design tokens from workflows/brand_voice.md."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND_FILE = ROOT / "workflows" / "brand_voice.md"


def load_brand() -> dict:
    text = BRAND_FILE.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise SystemExit(f"No JSON design-token block found in {BRAND_FILE}")
    return json.loads(match.group(1))
