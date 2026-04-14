"""
Cursor conversation extractor
- Exports ALL messages (user + AI replies) as readable markdown
- Highlights file changes (edits, creates, reads) made during each conversation
- Output: I:/cursor database/conversations/<date>_<title>.md
"""
import sqlite3, json, os, re
from datetime import datetime

DB_PATH = os.path.expandvars(r"C:\Users\pc\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")
OUT_DIR = r"I:\cursor database\conversations"

ROLE = {1: "USER", 2: "AI"}

# Tool names that indicate file changes
EDIT_TOOLS = {"edit_file_v2", "write_file", "create_file", "rewrite_file"}
READ_TOOLS  = {"read_file_v2", "read_file"}


def safe_filename(name, max_len=60):
    name = re.sub(r'[\\/*?:"<>|]', "", name or "untitled")
    name = name.strip().replace(" ", "_")
    return name[:max_len] or "untitled"


def ts_to_str(ms):
    try:
        return datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def extract_file_path(tool_data: dict) -> str:
    """Pull file path from toolFormerData params/rawArgs."""
    for field in ("rawArgs", "params"):
        raw = tool_data.get(field, "")
        if not raw:
            continue
        try:
            d = json.loads(raw)
            for key in ("relativeWorkspacePath", "path", "targetFile", "filePath"):
                if d.get(key):
                    return d[key]
        except Exception:
            pass
    return ""


def extract_diff(tool_data: dict) -> str:
    """Extract the streamingContent diff from edit_file_v2 params."""
    raw = tool_data.get("params", "")
    if not raw:
        return ""
    try:
        d = json.loads(raw)
        content = d.get("streamingContent", "")
        if content:
            # Return only the first 1500 chars so files don't become huge
            return content[:1500] + ("..." if len(content) > 1500 else "")
    except Exception:
        pass
    return ""


def render_tool_block(tool_data: dict) -> str:
    """Render a single tool call as a markdown block."""
    name   = tool_data.get("name", "unknown_tool")
    status = tool_data.get("status", "")
    fpath  = extract_file_path(tool_data)

    if name in EDIT_TOOLS:
        diff = extract_diff(tool_data)
        lines = [f"> **✏️ EDITED FILE** `{fpath}`  _(status: {status})_"]
        if diff:
            lines.append("> ```diff")
            for line in diff.splitlines():
                lines.append(f"> {line}")
            lines.append("> ```")
        return "\n".join(lines)

    if name in READ_TOOLS:
        return f"> **📖 READ FILE** `{fpath}`"

    # Other tools (search, terminal, etc.)
    raw_args = tool_data.get("rawArgs") or tool_data.get("params") or ""
    preview = ""
    try:
        preview = str(json.loads(raw_args))[:120]
    except Exception:
        preview = str(raw_args)[:120]
    return f"> **🔧 TOOL** `{name}` — {preview}"


def extract(db_path=DB_PATH, out_dir=OUT_DIR):
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return 0

    os.makedirs(out_dir, exist_ok=True)

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = con.cursor()

    # Load composer headers
    cur.execute("SELECT value FROM ItemTable WHERE key='composer.composerHeaders'")
    row = cur.fetchone()
    if not row:
        print("No composer headers found.")
        con.close()
        return 0

    composers = json.loads(row[0]).get("allComposers", [])
    print(f"Found {len(composers)} conversations")

    con.close()

    saved = 0
    for comp in composers:
        cid   = comp.get("composerId", "")
        name  = comp.get("name") or comp.get("subtitle") or "untitled"
        ctime = ts_to_str(comp.get("createdAt", 0))
        utime = ts_to_str(comp.get("lastUpdatedAt", 0))

        # Query bubbles only for this composer (fast per-conversation lookup)
        con2 = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        c2   = con2.cursor()
        c2.execute(
            "SELECT value FROM cursorDiskKV WHERE key LIKE ?",
            (f"bubbleId:{cid}:%",)
        )
        msgs = []
        for (raw,) in c2.fetchall():
            try:
                val = json.loads(raw) if isinstance(raw, (str, bytes)) else {}
                msgs.append(val)
            except Exception:
                continue
        con2.close()

        if not msgs:
            continue

        # sort chronologically
        def _ts(m):
            try:
                return int(m.get("createdAt", 0))
            except (TypeError, ValueError):
                return 0

        msgs.sort(key=_ts)

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
            tfd      = m.get("toolFormerData")

            # Tool-only bubbles (no text but has toolFormerData)
            if tfd and not text:
                lines.append(f"---\n### AI TOOL CALL  `{msg_time}`\n")
                lines.append(render_tool_block(tfd))
                lines.append("")
                continue

            if not text:
                continue

            lines.append(f"---\n### {role}  `{msg_time}`\n")
            lines.append(text)

            # If AI message had file operations, show them inline
            if tfd and role == "AI":
                lines.append("")
                lines.append(render_tool_block(tfd))

            lines.append("")

        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        saved += 1

    print(f"Saved {saved} conversations to: {out_dir}")
    return saved


if __name__ == "__main__":
    extract()
