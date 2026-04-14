# Knowledge base for ERP system
**Created:** 2026-04-09 16:02  |  **Updated:** 2026-04-09 16:07
**Composer ID:** `4b74314e-5af6-4505-96f1-eadb99cc1040`

---
### USER  ``

i want you to go though every file of erp next and want you to remember all the protocol that we created includig doctype files servcer script and client script

---
### AI  ``

Creating a personal Cursor skill that guides building and maintaining a knowledge base for your custom ERP. Checking for `C:\Users\pc\.cursor\skills` and creating the skill files.

---
### AI  ``

Locating your ERPNext/Frappe installation and customizations so we can inventory DocTypes, server scripts, and client scripts. Scanning the full upstream ERPNext tree isn't useful (thousands of stock files); we'll focus on your project and custom apps.

---
### AI  ``

## What’s realistic here

1. **“Every file of ERPNext”** — The stock **erpnext** / **frappe** trees are on the **bench (usually inside Docker)**, not as a full tree under `Desktop`. Walking **all** of upstream ERPNext would be huge and mostly irrelevant to *your* protocols.

2. **“Remember”** — I don’t keep a permanent memory across chats. What **does** persist is **your repo + docs** (and any exports you generate). That’s why the inventory lives in files Cursor can read anytime.

---

## What I did for you

1. **`docs/knowledge-base/CUSTOM_PROTOCOLS_INVENTORY.md`**  
   A structured list of **your** side of things, drawn from this repo:
   - Custom app **pcb_pts3** / **pts3-book**
   - DocTypes: **PTS3** (Result / Lane / Test), **PTS1**, **PCB IQC Result**, **PCB Ledger**
   - API Server Scripts: **`pts3_api`**, **`pts1_api`**
   - Named DocType Event scripts (PCB IQC ↔ Ledger, Stock Entry, Sonic guardrail, PR duplicate serials, etc.)
   - Main **client script** files in the repo
   - **`pcb_ledger_api` / `pcb_iqc_result_api`** install targets

2. **`docs/knowledge-base/META.md`** and **`INDEX.md`** — Entry points for the KB.

3. **`EXPORT_FRAPPE_CUSTOMIZATIONS_SNAPSHOT.py`** (project root)  
   When Docker + bench are up, it dumps **live** DB content to JSON under  
   `sites/<site>/private/files/kb_export_<timestamp>/`  
   (`server_scripts.json`, `client_scripts.json`, `custom_doctype_names.json`, `custom_doctypes_full.json`).  
   The script prints a **`docker compose cp`** line so you can copy that folder into **`docs/knowledge-base/_exports/snapshot_*`**.

---

## What you should run for a *complete* script/DocType snapshot

With your stack running:

```text
cd C:\Users\pc\Desktop\PCB_IQC_ERPNext_Project
python EXPORT_FRAPPE_CUSTOMIZATIONS_SNAPSHOT.py
```

Then run the printed `docker compose cp ...` so the JSON lands in `_exports`. That is the closest thing to “remember everything” for **Server Script / Client Script / custom DocTypes** on the site.

If you want, next step is to **run that export on your machine** and paste any error output (or the first lines of `server_scripts.json`), and we can align the markdown inventory with what’s actually on `frontend`.

---
### AI  ``

Scanning the project for DocType definitions, server/client scripts, and API protocols. Checking for a local `erpnext` clone and gathering inventory.

---
### AI  ``

Reading the Cursor skill-creation guide so we can draft a skill for your ERP knowledge base.

---
### AI  ``

Rewriting the export script: removing the broken duplicate `main()` and the unused `_bench_code` function.

---
### AI  ``

We can't scan every upstream ERPNext file on disk (it's inside Docker / not in this repo). Creating a project knowledge base that catalogs your custom protocols and adding an export script to snapshot live Server Scripts + Client Scripts from the DB when Docker is running.

---
### AI  ``

Gathering named Server Scripts, API methods, and DocTypes from list/dump scripts and key installers.

---
### AI  ``

Creating the personal skills directory and adding a focused skill plus a reference file with KB templates.

---
### AI  ``

Here’s what was set up for you.

## Skill: `local-erp-knowledge-base`

**Location (personal skill — all Cursor projects):**  
`C:\Users\pc\.cursor\skills\local-erp-knowledge-base\`

| File | Role |
|------|------|
| `SKILL.md` | When to use it, rules (code over guesses, no fake DocTypes/APIs, secrets handling), and steps to build/update the KB |
| `reference.md` | Folder layout under `docs/knowledge-base/`, plus starter templates for `INDEX.md`, `META.md`, apps, workflows, integrations |

**Description (for discovery):** The skill is written so the agent applies it when you talk about documenting your ERP, maintaining a KB, or answering questions **about your machine’s ERP** using **your repo/docs**, not generic ERP behavior.

## What you do next

1. **Point the KB at your real ERP folder**  
   In chat, say something like: “My ERP is at `C:\Users\pc\Desktop\PCB_IQC_ERPNext_Project`” (or whatever path you use). The agent should create `docs/knowledge-base/` there and fill `META.md` with that root.

2. **Optional — tie it to one repo only**  
   Copy the same `local-erp-knowledge-base` folder into **that project’s** `.cursor\skills\` if you want this workflow only when that repo is open.

3. **First KB pass**  
   Ask Cursor to: “Using the local ERP knowledge base skill, create `docs/knowledge-base/` from the current codebase: overview, custom apps, main DocTypes, and integrations.”

If you tell me the **exact absolute path** to your ERP project (Frappe bench root or app root), I can add a one-line default in `META.md` or tailor the skill to ERPNext vs a fully custom stack.

---
### USER  ``

/create-skill  Help me create this skill for Cursor: i need to create knowledge base for the erp system that i develeoped in my pc
