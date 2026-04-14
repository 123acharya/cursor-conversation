import json
import os
import re
from datetime import datetime


ROOT = os.path.dirname(os.path.abspath(__file__))
FULL_DIR = os.path.join(ROOT, "full_conversations")
OUT_DIR = os.path.join(ROOT, "exports")


def _safe_filename(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9._ -]+", "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" ", "_")
    return s[:180] or "conversation"


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _guess_title(doc: dict, fallback: str) -> str:
    # Some files may not contain a chat name; use first user message prefix as best-effort.
    msgs = doc.get("messages") or []
    for m in msgs:
        if (m.get("type") == "user") and (m.get("text") or "").strip():
            t = (m.get("text") or "").strip().splitlines()[0].strip()
            if t:
                return t[:80]
    return fallback


def export_one(path: str) -> str:
    doc = _load_json(path)
    composer_id = doc.get("composer_id") or "unknown"
    base = os.path.basename(path)
    fallback_title = base.replace("FULL_", "").replace(".json", "")
    title = _guess_title(doc, fallback_title)

    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_name = f"{_safe_filename(title)}__{composer_id}.md"
    out_path = os.path.join(OUT_DIR, out_name)

    lines: list[str] = []
    lines.append(f"## {title}")
    lines.append("")
    lines.append(f"- **source**: `{path}`")
    lines.append(f"- **composer_id**: `{composer_id}`")
    lines.append(f"- **exported_at**: `{created}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    for m in doc.get("messages") or []:
        role = (m.get("type") or "unknown").strip().lower()
        text = (m.get("text") or "").rstrip()
        if not text:
            continue
        if role == "user":
            lines.append("### User")
        elif role == "assistant":
            lines.append("### Assistant")
        else:
            lines.append(f"### {role.title()}")
        lines.append("")
        lines.append(text)
        lines.append("")
        lines.append("---")
        lines.append("")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    return out_path


def main() -> int:
    if not os.path.isdir(FULL_DIR):
        print(f"Missing folder: {FULL_DIR}")
        return 2

    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(
        [
            os.path.join(FULL_DIR, f)
            for f in os.listdir(FULL_DIR)
            if f.lower().endswith(".json") and f.startswith("FULL_conversation_")
        ]
    )
    if not files:
        print(f"No FULL_conversation_*.json files found in {FULL_DIR}")
        return 0

    written = []
    for p in files:
        try:
            written.append(export_one(p))
        except Exception as e:
            print(f"[ERROR] {p}: {e}")

    print(f"Exported {len(written)} conversations to {OUT_DIR}")
    for p in written:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

