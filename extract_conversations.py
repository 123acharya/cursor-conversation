"""
Cursor conversation extractor — exports ALL messages (user + AI) as readable markdown.
Run: python extract_conversations.py
Output: conversations/<date>_<title>.md
"""
import sqlite3, json, os, re
from datetime import datetime

DB_PATH = os.path.expandvars(r"C:\Users\pc\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversations")

ROLE = {1: "USER", 2: "AI"}


def safe_filename(name, max_len=60):
    name = re.sub(r'[\\/*?:"<>|]', "", name or "untitled")
    name = name.strip().replace(" ", "_")
    return name[:max_len] or "untitled"


def ts_to_str(ms):
    try:
        return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def extract(db_path=DB_PATH, out_dir=OUT_DIR):
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return 0

    os.makedirs(out_dir, exist_ok=True)

    # open read-only so we never corrupt the live DB
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = con.cursor()

    # --- load composer headers ---
    cur.execute("SELECT value FROM ItemTable WHERE key='composer.composerHeaders'")
    row = cur.fetchone()
    if not row:
        print("No composer headers found in DB.")
        con.close()
        return 0

    composers = json.loads(row[0]).get("allComposers", [])
    print(f"Found {len(composers)} conversations")

    # --- load ALL bubbles into memory, keyed by composerId ---
    print("Loading messages from DB (this may take a moment)...")
    cur.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'bubbleId:%'")
    bubbles_by_composer: dict[str, list] = {}
    for key, raw in cur.fetchall():
        parts = key.split(":", 2)          # bubbleId : composerId : bubbleId
        if len(parts) != 3:
            continue
        composer_id = parts[1]
        try:
            val = json.loads(raw) if isinstance(raw, (str, bytes)) else {}
        except Exception:
            continue
        bubbles_by_composer.setdefault(composer_id, []).append(val)

    con.close()

    saved = 0
    for comp in composers:
        cid   = comp.get("composerId", "")
        name  = comp.get("name") or comp.get("subtitle") or "untitled"
        ctime = ts_to_str(comp.get("createdAt", 0))
        utime = ts_to_str(comp.get("lastUpdatedAt", 0))

        msgs = bubbles_by_composer.get(cid, [])
        if not msgs:
            continue

        # sort chronologically (createdAt can be int or str)
        def sort_key(m):
            v = m.get("createdAt", 0)
            try:
                return int(v)
            except (TypeError, ValueError):
                return 0
        msgs.sort(key=sort_key)

        date_prefix = ctime[:10] if ctime else "0000-00-00"
        fname = f"{date_prefix}_{safe_filename(name)}.md"
        fpath = os.path.join(out_dir, fname)

        lines = [
            f"# {name}",
            f"**Created:** {ctime}  |  **Updated:** {utime}",
            f"**Composer ID:** `{cid}`",
            "",
        ]

        for m in msgs:
            role     = ROLE.get(m.get("type"), "UNKNOWN")
            msg_time = ts_to_str(m.get("createdAt", 0))
            text     = (m.get("text") or "").strip()
            if not text:
                continue
            lines.append(f"---\n### {role}  `{msg_time}`\n")
            lines.append(text)
            lines.append("")

        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        saved += 1

    print(f"Saved {saved} conversations to: {out_dir}")
    return saved


if __name__ == "__main__":
    extract()
