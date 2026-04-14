# Using skills and subagents in cursor
**Created:** 2026-03-13 15:31  |  **Updated:** 2026-03-13 16:10
**Composer ID:** `ac7255a5-d418-447d-817c-9c239d67c384`

---
### USER  ``

NOW CAN YOU BUILD A SUB AGENT TO CRETATE DOCTYPE AND PLACE IT IN THE C:\Users\pc\Desktop\PCB_IQC_ERPNext_Project\EXAMPLES\CHARGPT  TRIAL\PTS3 test THIS FOLDER ILL ASK MY MAIN CHAT TO USE THE SAME FOR CREATING ANY DOCTYPE ALSO THIS AGENT SHOULD UNDERSTAND THE MAIN CONTEXT

---
### AI  ``

Exploring the project structure and creating project-specific skills and subagents for the PTS3 ERPNext integration.

---
### AI  ``

Here’s what’s been set up:

---

## Subagent: `pts3-doctype-creator`

**Location:** `.cursor/agents/pts3-doctype-creator.md`  
*(Subagents must be in `.cursor/agents/` so Cursor can find them.)*

**Output folder:** `EXAMPLES/CHARGPT  TRIAL/PTS3 test/`

---

## What the subagent knows

- **PTS3 integration context:** ERP → connector → Python CLI, live updates, Left/Right/Diff format
- **Field schema:** All fields from `10_ERP_FIELD_SCHEMA.md` (PTS3 Test, PTS3 Lane, PTS3 Result, PTS3 Frequency Row)
- **Output path:** Writes scripts into the PTS3 test folder

---

## How main chat uses it

In main chat, use prompts like:

| Task | Example prompt |
|------|----------------|
| Create PTS3 Lane | *"Use the pts3-doctype-creator subagent to create the PTS3 Lane doctype"* |
| Create PTS3 Test | *"Use pts3-doctype-creator to create PTS3 Test"* |
| Create PTS3 Result | *"Create PTS3 Result doctype using the pts3-doctype-creator"* |
| Create PTS3 Frequency Row | *"Use the doctype creator subagent to add PTS3 Frequency Row"* |

---

## Files created

```
.cursor/agents/
└── pts3-doctype-creator.md     ← Subagent (Cursor reads this)

EXAMPLES/CHARGPT  TRIAL/PTS3 test/
└── SUBAGENT_README.md          ← Instructions for main chat
```

Generated scripts will be written as:

- `create_pts3_test.py`
- `create_pts3_lane.py`
- `create_pts3_result.py`
- `create_pts3_frequency_row.py`

---

## Note on placement

Subagents must live in `.cursor/agents/` so Cursor can discover them. The PTS3 test folder holds:

1. `SUBAGENT_README.md` – how to invoke the subagent from main chat  
2. The generated doctype scripts when you run it

If you want, I can run the subagent to generate one of the doctype scripts (e.g. PTS3 Lane) as a first example.

---
### AI  ``

Here’s how to use **skills** and **subagents** in your PCB IQC ERPNext project.

---

## 1. Project-level skill for ERPNext doctypes

Create a skill that encodes your doctype patterns and naming so the AI follows them automatically.

**Location:** `PCB_IQC_ERPNext_Project/.cursor/skills/erpnext-doctypes/`

**What it should include:**
- DocType naming: `PTS1 Test`, `PTS1 Lane`, `PCB Master`, `PCB Ledger`, `PCB IQC Result`
- Field schema from `10_ERP_FIELD_SCHEMA.md`
- Pattern from `create_pts1_lane_doctype.py` (frappe API, field structure)
- Note that field names are fixed and must match the schema

**Example description:**
> "Creates and modifies ERPNext/Frappe DocTypes. Use when creating doctypes, adding fields, or writing bench console scripts. Follows PCB IQC project naming (PTS1, PTS3, PCB Master, PCB Ledger) and field schema from 10_ERP_FIELD_SCHEMA.md."

---

## 2. Project rule for ERPNext/Frappe code

Add a rule so the AI uses your conventions when editing ERPNext-related files.

**Location:** `PCB_IQC_ERPNext_Project/.cursor/rules/erpnext-frappe.mdc`

**Example content:**
- Use `frappe.db.exists("DocType", name)` before creating
- Use `frappe.get_doc("DocType", name)` for updates
- Match field names exactly to the schema
- Use `istable=1` for child tables, `module="Stock"` for stock doctypes

---

## 3. ERPNext subagent

Create a subagent focused on ERPNext/Frappe work.

**Location:** `PCB_IQC_ERPNext_Project/.cursor/agents/erpnext-specialist.md`

**Example description:**
> "ERPNext/Frappe specialist for PCB IQC project. Use when creating doctypes, Server Scripts, Client Scripts, or API integrations. Knows PTS1/PTS3 schema, PCB Master/Ledger flow, and bench console patterns."

---

## Suggested setup for your project

| Type | Path | Purpose |
|------|------|---------|
| **Skill** | `.cursor/skills/erpnext-doctypes/SKILL.md` | Teaches doctype creation and naming |
| **Rule** | `.cursor/rules/erpnext-frappe.mdc` | Enforces conventions in ERPNext code |
| **Subagent** | `.cursor/agents/erpnext-specialist.md` | Dedicated ERPNext assistant |

---

## How to use it

1. **Skill** – Ask things like:
   - *"Create a new child doctype PTS3 Lane with fields from the schema"*
   - *"Add the run_id field to PTS1 Lane doctype"*

2. **Rule** – It applies automatically when you work on matching files (e.g. `**/*.py` in the project).

3. **Subagent** – Ask:
   - *"Use the erpnext-specialist to add a new field to PCB Ledger"*

---

If you want, I can draft the exact contents for:
- `.cursor/skills/erpnext-doctypes/SKILL.md`
- `.cursor/rules/erpnext-frappe.mdc`
- `.cursor/agents/erpnext-specialist.md`

Tell me which ones you want created and I’ll generate them.

---
### AI  ``

Checking the skill files to provide accurate guidance.

---
### AI  ``

Here’s what’s set up and how to use it.

---

## What’s in place

### 1. **Project skill** – `pts3-erpnext-integration`

**Path:** `.cursor/skills/pts3-erpnext-integration/SKILL.md`

This skill gives the AI project context when you work on PTS3 integration:

- DocType names: PTS3 Test, PTS3 Lane, PTS3 Result
- Exact field names from `10_ERP_FIELD_SCHEMA.md`
- Bench console pattern for creating doctypes
- Spec file locations and constraints

**How to use:** Ask about PTS3 doctypes, connector, CLI, or live updates. The AI will use this skill automatically when the request matches.

---

### 2. **Project rule** – `pts3-erpnext-doctypes`

**Path:** `.cursor/rules/pts3-erpnext-doctypes.mdc`

This rule applies when you edit:

- `create_pts*.py`
- `ADD_*PTS*.py`
- `*PTS3*.py`

It enforces:

- Exact field names from the schema
- Correct DocType names
- `istable = 1` for child tables
- Bench console usage pattern

**How to use:** Open or edit any of those files; the rule is applied automatically.

---

### 3. **Subagent** – `erpnext-doctype-specialist`

**Path:** `.cursor/agents/erpnext-doctype-specialist.md`

This subagent is focused on creating and updating ERPNext doctypes for PTS3.

**How to use:** Ask explicitly, for example:

- *“Use the erpnext-doctype-specialist subagent to create the PTS3 Lane doctype”*
- *“Create a bench script for PTS3 Result using the doctype specialist”*

---

## Example prompts

| Goal | Example prompt |
|------|----------------|
| Create PTS3 Lane doctype | *“Create a bench console script for PTS3 Lane with all fields from the schema”* |
| Create PTS3 Result | *“Use the erpnext-doctype-specialist to create PTS3 Result doctype”* |
| Add a field | *“Add the live_graph_json field to PTS3 Lane”* (skill + rule keep names correct) |
| Connector work | *“How should the connector push live sweep points to ERP?”* |

---

## File layout

```
PCB_IQC_ERPNext_Project/
├── .cursor/
│   ├── skills/
│   │   └── pts3-erpnext-integration/
│   │       └── SKILL.md
│   ├── rules/
│   │   └── pts3-erpnext-doctypes.mdc
│   └── agents/
│       └── erpnext-doctype-specialist.md
└── ...
```

---

## Tips

1. **Skills** – Mention PTS3, doctypes, connector, or live updates so the skill is triggered.
2. **Rules** – Work in the matching files so the rule applies.
3. **Subagents** – Use them for focused tasks, e.g. *“Use the erpnext-doctype-specialist to…”*.
4. **Schema** – Keep `10_ERP_FIELD_SCHEMA.md` as the source of truth; the skill and rule reference it.

If you tell me which doctype you want to create first (PTS3 Test, PTS3 Lane, or PTS3 Result), I can generate the bench console script for it.

---
### AI  ``

Creating project-specific skills, rules, and a subagent for the PTS3 ERPNext integration.

---
### AI  ``

Checking the project structure and creating project-specific skills and rules.

---
### USER  ``

how to use skill and subagetnts in cursor im very new to this

---
### AI  ``

Here’s a concise guide to **Skills** and **Subagents** in Cursor.

---

## Skills in Cursor

**Skills** are reusable instructions that teach the AI how to do specific tasks. They’re stored as markdown files and are applied automatically when your request matches their description.

### Where skills live

| Type | Path | Scope |
|------|------|-------|
| **Personal** | `~/.cursor/skills/` | All your projects |
| **Project** | `.cursor/skills/` | Only that project |

### How they work

1. Each skill has a **name** and **description**.
2. The AI uses the description to decide when to apply the skill.
3. When it matches, it loads the skill’s instructions and follows them.

### Example skills you already have

- **create-skill** – Create new skills
- **create-rule** – Create Cursor rules (`.cursor/rules/`)
- **create-subagent** – Create custom subagents
- **update-cursor-settings** – Change editor settings

### Using skills

You don’t need to do anything special. Ask for something that matches a skill’s description, and the AI will use it. For example:

- *“Create a rule for TypeScript standards”* → uses `create-rule`
- *“Create a code reviewer subagent”* → uses `create-subagent`

---

## Subagents in Cursor

**Subagents** are specialized AI assistants that run in separate contexts with their own system prompts. They’re useful for:

- Keeping exploration separate from your main chat
- Focusing on specific tasks (e.g. code review, debugging)
- Reusing the same configuration across projects

### Where subagents live

| Location | Scope |
|----------|--------|
| `.cursor/agents/` | Current project (can be shared via git) |
| `~/.cursor/agents/` | All your projects (personal) |

### How to use subagents

1. **Built-in subagent types** (via the `mcp_task` tool):
   - **generalPurpose** – General research and multi-step tasks
   - **explore** – Codebase exploration
   - **shell** – Running commands (git, terminal, etc.)

2. **Custom subagents** – You define them in `.md` files with:
   - A `name` and `description`
   - A system prompt (the markdown body)

### Example: creating a custom subagent

Create `~/.cursor/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Expert code review specialist. Use when reviewing pull requests or code changes.
---

You are a senior code reviewer. When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Provide feedback on quality, security, and best practices
```

Then you can say: *“Use the code-reviewer subagent to review my recent changes.”*

---

## Quick comparison

| Feature | Skills | Subagents |
|--------|--------|-----------|
| **Purpose** | Teach the AI how to do a task | Run a specialized assistant in a separate context |
| **Location** | `~/.cursor/skills/` or `.cursor/skills/` | `~/.cursor/agents/` or `.cursor/agents/` |
| **Format** | `SKILL.md` in a folder | `.md` file with frontmatter |
| **When used** | When your request matches the description | When you ask to use that agent or when the AI delegates to it |

---

## Getting started

1. **Skills** – Use them by asking for the task they describe (e.g. “Create a rule for React patterns”).
2. **Subagents** – Create one with the `create-subagent` skill, or ask: *“Create a debugger subagent for me.”*
3. **Rules** – Use the `create-rule` skill to add project-specific rules in `.cursor/rules/`.

If you tell me what you want to automate (e.g. code review, debugging, project conventions), I can suggest a concrete skill or subagent setup for it.

---
### AI  ``

Exploring your ERPNext project to provide tailored advice.

---
### AI  ``

Creating a subagent that understands the PTS3 context and outputs doctype scripts to the PTS3 test folder.

---
### USER  ``

im working on erpnext where im creating doctype and using names 
how can i use it in this project
# PTS3 ERPNext Integration - Master Context

## Project Goal

We already have a working Windows Python PTS3 testing program.
Now we want to integrate it with ERPNext in the same operational style as our PTS1 integration.

Main goal:
- Run PTS3 tests from ERPNext page buttons
- Use a connector process like PTS1
- Execute the existing Python test logic through CLI commands
- Show live graph/data in ERP while the test is running
- Store final results in ERP in an operator-friendly format
- Keep full per-PCB history, including multiple test runs on the same PCB

This is not a new standalone tester.
This is an ERP-controlled integration of the existing PTS3 application.

---

## Current Python App Reality

Current Python app already does these things:
- Windows Tkinter desktop app
- Uses Tektronix scope via `Scope_header_v2.py`
- Step Sweep updates live plots while the sweep is running
- Mode 1 / 2 / 3 / 0 tests update combined mode chart
- Stores results locally in Excel
- Uses tri-row summary format:
  - Left
  - Right
  - Diff
- Summary columns are:
  - Serial number
  - Date
  - Status
  - Dominent channel
  - Max value
  - Channel
  - 40hz to 80hz
  - Mode1 Mode2 Mode3 Mode0
- Uploads results to Google Sheet in the same understandable format for operators

Important:
ERP integration must preserve this operator-friendly structure.
Do not replace it with an abstract/raw-only data model in the UI.

---

## Non-Negotiable Functional Requirements

### 1. ERP must trigger the test
PTS3 should be started from ERPNext buttons, not manually from the Python GUI.

### 2. Use connector pattern like PTS1
Architecture should be:
ERPNext client/script -> PTS3 connector -> Python CLI worker

### 3. Live updates during test
This is critical.

For Step Sweep:
- every frequency point is generated during the test
- ERP must receive and display points live while test is running
- graph in ERP must grow point-by-point
- operator should not wait until full test completion

For Mode 1 / 2 / 3 / 0:
- ERP must also receive live progress/value updates while test is running
- if the mode produces evolving values/graph, ERP must update in near real time

### 4. Final result storage
After completion:
- save structured final result in ERP
- keep same understandable Left/Right/Diff presentation
- store graph data
- store summary
- store detailed per-frequency values

### 5. PCB history
Need one master/history path for each PCB:
- same PCB can have multiple PTS3 runs
- ERP must preserve all runs, not only latest result
- this should fit into overall PCB master / ledger concept

---

## Required Architecture

### A. Python Side
Existing Python app should be refactored, not rewritten blindly.

We need:
1. reusable core test functions
2. CLI entry mode
3. live event output
4. final JSON result output

Target pattern:
- GUI mode remains possible
- ERP connector uses CLI mode

Example CLI operations:
- submit/init
- step_sweep
- mode1
- mode2
- mode3
- mode0
- full_test
- upload_result (optional if ERP handles upload separately)

Python must emit:
- live events during run
- final structured result on completion

Best implementation:
- print JSON lines to stdout with flush=True for live events
- final result can be JSON file and/or final JSON line

### B. Connector Side
PTS3 connector should behave like PTS1 connector but with live streaming.

Responsibilities:
- poll ERP for requested PTS3 jobs
- mark lane queued/running
- start Python CLI subprocess
- read stdout continuously
- when live event arrives, immediately push it to ERP
- when final result arrives, save final result to ERP
- on crash/error, mark job failed in ERP

### C. ERP Side
ERP should have:
- PTS3 Test doctype
- PTS3 Lane child table
- PTS3 Result doctype for permanent run history
- optional PTS3 Frequency Row child table
- PCB Ledger or PCB Master linkage for long-term traceability

---

## Exact Behavior Wanted

### Step Sweep
When operator clicks Step Sweep in ERP:
1. ERP marks lane Requested
2. connector picks job
3. connector starts Python CLI step_sweep
4. every time a new frequency point is available, connector pushes it to ERP
5. ERP page refreshes live
6. graph grows in ERP
7. final summary/result is saved at the end

### Mode Tests
When operator clicks Mode 1 / 2 / 3 / 0:
1. ERP marks requested action
2. connector runs Python CLI mode action
3. connector pushes live mode progress/value updates to ERP
4. ERP page shows live update
5. final result saved at end

---

## ERP UI Requirement

Operator-facing ERP page must stay understandable like the current sheet format.

### Required display style
Show result block as:
- Left row
- Right row
- Diff row

Columns:
- 40hz to 80hz
- Mode1 Mode2 Mode3 Mode0
- plus summary fields like Status, Dominant channel, Max value

### Required graph display
ERP should show:
- live sweep graph during Step Sweep
- live mode visualization if data supports it
- final graph after completion

Preferred graph rendering:
- Chart.js or ERP/Frappe chart inside HTML field
- live data pulled from lane JSON field

---

## Data Model Direction

### 1. PTS3 Test
Main ERP session page used by operator.

### 2. PTS3 Lane
Holds per-lane working state:
- serial
- device/com mapping
- requested action
- action status
- live graph JSON
- live table JSON
- progress message
- latest summary fields
- link to latest final result

### 3. PTS3 Result
Permanent record for one completed run:
- serial
- run_id
- operation
- datetime
- pass/fail
- dominant channel
- max value
- mode values
- final graph JSON
- raw result JSON
- artifact paths if any

### 4. PCB Ledger / PCB Master link
Every completed PTS3 run should be linkable into overall PCB history.

---

## Important Constraint

Do not destroy current working Python logic.
Refactor around it.

We already have a working acquisition app.
Main work is:
- extract reusable engine logic
- add CLI wrapper
- add live JSON event emission
- connect to ERP through connector

---

## Recommended Technical Strategy

### Python output format
Use JSON events over stdout, one line at a time.

Example event types:
- status
- sweep_point
- mode_progress
- mode_point
- log
- completed
- failed

### ERP live update storage
During run, store temporary live data in lane JSON fields:
- live_graph_json
- live_table_json
- live_status
- live_current_freq
- live_current_mode
- live_progress_message
- last_live_update_at

### ERP final storage
At run completion:
- create PTS3 Result
- save summary and raw result
- link lane to latest result
- optionally create ledger history entry

---

## Acceptance Criteria

Project is successful only when all of these work:

1. Operator can open ERP PTS3 page and trigger Step Sweep / Mode tests from ERP buttons
2. Connector launches Python test without manual GUI interaction
3. ERP graph updates live while test is still running
4. ERP table updates live while test is still running
5. Final result is saved in ERP in Left / Right / Diff format
6. Same PCB can have multiple historical PTS3 results
7. Result is readable for blue-collar operators
8. Integration pattern feels similar to existing PTS1 connector flow
9. Failure handling is clean
10. Re-run and retry do not corrupt prior history

---

## What Cursor Should Focus On First

First priority:
1. define stable event contract between Python and connector
2. add CLI worker mode to Python app
3. define ERP doctypes/fields
4. create connector polling + live push flow
5. build ERP live rendering
6. only then polish history/ledger linking

Cursor should avoid random rewriting of working acquisition logic unless necessary.
