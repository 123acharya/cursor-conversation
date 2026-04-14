# ERPNext custom document permissions
**Created:** 2026-04-14 12:35  |  **Updated:** 2026-04-14 13:09
**Composer ID:** `71d79f66-e90c-439c-86f1-df0fe4081e9b`

---
### USER  ``

in this doctype of pts3 result what is the format of run id

---
### AI  ``

Not yet — the permission command failed due to Windows/PowerShell quoting issues, so nothing was applied. I’m going to run the fix **inside the backend container** (so it works reliably on Windows), then I’ll verify the user has the role and the DocType permissions exist.

---
### USER  ``

run command and give acces to this these Give that role permission on each Custom DocType
For each of these DocTypes (from your screenshot):

PCB IQC Result
PCB Ledger
PCB Master
PTS1 Lane Result
PTS1 Test
PTS3 Result
PTS3 Test
modules for this user
developer@rapture.works

G:\frappe_docker-main\frappe_docker-main
frappe locationn

---
### USER  ``

did you give permisssion to the use 
developer@rapture.works

---
### AI  ``

I’ve got the quoting approach working; the last failure was only because I accidentally nested PowerShell inside PowerShell. Next I’ll run the `docker exec ... bench --site ... execute ...` commands directly (no extra `powershell -Command`), apply to both sites, then verify the user’s roles.

---
### AI  ``

Next I’ll detect your running Frappe container and site name from `compose.yaml`/`.env`, then I’ll execute a single command inside the backend container to: create the role, assign it to `developer@rapture.works`, and set `read/select` (and optionally write/create) permissions for the 7 DocTypes.

---
### AI  ``

## What to do (recommended: Role-based, safe)

### 1) Create a dedicated role
- Go to **Role** list → **New**
- Role name: `Stock Custom Documents User` (any name is fine)
- Save

### 2) Give that role permission on each Custom DocType
For each of these DocTypes (from your screenshot):
- `PCB IQC Result`
- `PCB Ledger`
- `PCB Master`
- `PTS1 Lane Result`
- `PTS1 Test`
- `PTS3 Result`
- `PTS3 Test`

Do:
- Open **Role Permission Manager**
- Select **DocType** = (one of the above)
- Add/enable permissions for role `Stock Custom Documents User` as needed:
  - Minimum: **Read**, **Select**
  - If they must create/edit: **Write**, **Create**
  - If they must submit/cancel: **Submit** / **Cancel**
  - If they must print/export: **Print** / **Export**
- Save
- Repeat for all 7 DocTypes

### 3) Assign the role to the user
- Open **User**: `developer@rapture.works`
- In **Roles** table → add `Stock Custom Documents User`
- Save

## Make sure they “show up” in Stock
- Open each DocType (via **DocType** list) and confirm **Module = Stock**
  - If the Module is something else, the documents may not appear under Stock menus/workspaces (even if permissions are correct).

## Common gotcha
- If any of these DocTypes link to other DocTypes (child tables, linked masters), the user may also need **Read/Select** on those linked DocTypes, otherwise forms can open but fields will error/appear blank.

## If you want, I can do it via script
Tell me your **site name** (e.g. `site1.local`) and whether the user should get **Read-only** or **Create/Write** too, and I’ll give you a single bench console script that applies all permissions + assigns the role.

---
### AI  ``

I found you have **two sites** in the container: `frontend` and `test-pcb-ledger`. I’m going to apply the role + permissions to **both sites** (so whichever one you’re using will work), then clear cache so the user sees the Stock module documents immediately.

---
### AI  ``

Yes — now `developer@rapture.works` has access.

- **Role added**: `Stock Custom Documents User` (via the user’s **Role Profile `developer`**, so it won’t get overwritten)
- **Permissions granted** on these Custom DocTypes (permlevel 0): **Read + Select + Write + Create**
  - `PCB IQC Result`
  - `PCB Ledger`
  - `PCB Master`
  - `PTS1 Lane Result`
  - `PTS1 Test`
  - `PTS3 Result`
  - `PTS3 Test`

I also cleared cache. If the user is logged in, have them **log out and log in again** to refresh roles/menus.

---
### AI  ``

I’m switching to a **single bash script inside the backend container** (instead of a PowerShell loop) so quoting doesn’t break on Windows. It will be **idempotent** (safe to run even if some perms already exist), apply to **both sites** `frontend` and `test-pcb-ledger`, then clear cache.{"description":"Run bash loop inside backend container to grant role+perms","command":"powershell -NoProfile -Command \"docker exec frappe_docker-main-backend-1 bash -lc 'set -euo pipefail; cd /home/frappe/frappe-bench; role=\"Stock Custom Documents User\"; user=\"developer@rapture.works\"; doctypes=(\"PCB IQC Result\" \"PCB Ledger\" \"PCB Master\" \"PTS1 Lane Result\" \"PTS1 Test\" \"PTS3 Result\" \"PTS3 Test\"); perms=(read select write create); for site in frontend test-pcb-ledger; do echo \"--- SITE: $site\"; bench --site \"$site\" execute frappe.core.doctype.role.role.create_role --kwargs \"{\\\"role_name\\\":\\\"$role\\\"}\" || true; bench --site \"$site\" execute frappe.core.doctype.user.user.add_role --kwargs \"{\\\"user\\\":\\\"$user\\\",\\\"role\\\":\\\"$role\\\"}\" || true; for dt in \"${doctypes[@]}\"; do bench --site \"$site\" execute frappe.permissions.add_permission --kwargs \"{\\\"doctype\\\":\\\"$dt\\\",\\\"role\\\":\\\"$role\\\",\\\"permlevel\\\":0}\" || true; for p in \"${perms[@]}\"; do bench --site \"$site\" execute frappe.permissions.update_permission_property --kwargs \"{\\\"doctype\\\":\\\"$dt\\\",\\\"role\\\":\\\"$role\\\",\\\"permlevel\\\":0,\\\"permission\\\":\\\"$p\\\",\\\"value\\\":1}\"; done; done; bench --site \"$site\" clear-cache; done; echo \"DONE\"'\"","block_until_ms":300000}```)}*** End Patch"} 
}

Unfortunately, the response included extraneous text, so I won't be able to process it. Please try again with only a valid JSON object.

---
### AI  ``

Got it. I’ll (1) confirm the exact DocType names from your screenshot, (2) give you the safest UI steps to grant access via a dedicated Role (recommended), and (3) also give you an optional one-shot bench/console script to apply the same permissions quickly.

---
### USER  ``

in the erp next that i have built can you give this user 
developer@rapture.works
the permisssion to see and use these custome documentres in stock module

---
### AI  ``

I’ll pull the `PTS3 Result` DocType definition from your running ERP (field list + autoname/naming settings) and then tell you exactly what **Run ID** is supposed to look like (and whether it’s enforced or free text).

---
### AI  ``

That still failed because PowerShell is trying to interpret parts of the JSON/quotes before it even reaches Docker. Next I’ll avoid PowerShell parsing entirely by writing the command in a way PowerShell treats as a literal string, then re-run and verify the role assignment.

---
### AI  ``

I’m going to inspect your `G:\frappe_docker-main\frappe_docker-main` setup to see how you run Frappe (docker compose vs local bench), then I’ll run the right command to create a role, assign it to `developer@rapture.works`, and grant permissions on all 7 DocTypes.

---
### AI  ``

I found this is a **Docker-based ERPNext v15** setup (`compose.yaml`) with an external `sites` volume, so we need to apply permissions **inside the running backend container**. Next I’ll detect the site(s) in `/home/frappe/frappe-bench/sites` and then run a single `bench --site ... execute` script to grant role + permissions + user role.

---
### AI  ``

## `PTS3 Result` → Run ID format

In your `PTS3 Result` DocType, **`run_id` is a `Data` field** with **no format enforced** (no options/regex/naming series on the DocType).

From the latest saved records, the Run ID is being stored in **one of these formats**:

- **`PTS3-TEST-00001|1|20260413_193`**  
  Pattern: `<PTS3 Test name>|<lane_no>|<YYYYMMDD_HHMM?>`

- **`pts3run_1111_PTS3-TEST-00001_001`**  
  Pattern: `pts3run_<something>_<PTS3 Test name>_<run_no?>`

So: **it’s free-text**, and the “format” is whatever your capture script/client is generating (currently it’s using the pipe-separated style in the newest entries).
