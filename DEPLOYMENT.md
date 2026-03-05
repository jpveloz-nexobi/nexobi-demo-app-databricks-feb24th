# NexoBI Genie App — Client Deployment Guide

This guide covers everything needed to deploy the NexoBI Genie chat app on a client's Databricks workspace using **Databricks Apps (free edition)**. Follow each section in order.

---

## Architecture Overview

```
Client Browser
     │
     ▼
Databricks Apps  ──── auto-injects OAuth credentials ────▶ Genie API
     │                                                          │
     │  (hosts Streamlit app)                                   ▼
     │                                               Unity Catalog Tables
     │                                               (workspace.gold.*)
     ▼
app-XXXXX nexo-agent  ← auto-created Service Principal
```

- **No tokens stored anywhere.** Databricks Apps injects OAuth credentials automatically.
- The app runs as an auto-created **service principal** — you just need to grant it table access.

---

## Prerequisites

The client must have:

| Requirement | Details |
|---|---|
| Databricks workspace | Any edition (free works) |
| Databricks Apps enabled | Check: Compute → Apps |
| Genie Space created | With tables configured and working |
| Unity Catalog enabled | Tables in `catalog.schema.table` format |
| Admin access | To grant permissions to the service principal |

---

## Step 1 — Fork / Copy the Repo

The client's git repo must contain these files:

```
your-repo/
├── app.py                      # Main Streamlit app
├── app.yaml                    # Databricks Apps config
├── requirements.txt            # Python dependencies
└── .streamlit/
    ├── config.toml             # Streamlit server config
    └── secrets.toml            # Empty file (suppresses warning)
```

### `app.yaml`
```yaml
command:
  - python
  - -m
  - streamlit
  - run
  - app.py
```
> **No tokens here.** Never store credentials in `app.yaml` — Databricks Apps injects auth automatically.

### `requirements.txt`
```
streamlit>=1.35.0
pandas>=2.0.0
requests>=2.31.0
databricks-sdk>=0.20.0
```

### `.streamlit/config.toml`
```toml
[server]
enableCORS = false
enableXsrfProtection = false
headless = true
port = 8080
address = "0.0.0.0"

[browser]
gatherUsageStats = false
```
> These settings are **required** for Databricks Apps proxy to work. Do not add `--server.*` flags to `app.yaml` — they conflict with this file.

### `.streamlit/secrets.toml`
```
# intentionally empty
```
> This empty file suppresses Streamlit's "no secrets found" warning on startup.

---

## Step 2 — Configure the Genie Space ID

In `app.py`, find this line:

```python
GENIE_SPACE_ID = _secret("NEXOBI_GENIE_SPACE_ID", "YOUR_SPACE_ID_HERE")
```

Get the Genie Space ID from:
**Databricks → Genie** → open the space → copy the ID from the URL:
`/genie/spaces/01f1180e851210c6bf3967bf360cecef` → ID is `01f1180e851210c6bf3967bf360cecef`

Replace the default value or set it as an environment variable in the Databricks App settings (preferred for multi-client deployments).

---

## Step 3 — Deploy the App on Databricks

1. Go to **Compute → Apps → Create App**
2. Choose **Custom app**
3. Connect your git repo (GitHub/GitLab)
4. Select the branch (e.g. `main`)
5. Click **Deploy**

Databricks will:
- Pull the repo
- Install `requirements.txt`
- Start the Streamlit app on port 8080
- **Auto-create a service principal** named `app-XXXXX nexo-agent`

---

## Step 4 — Grant Unity Catalog Permissions

This is the most critical step. The auto-created service principal needs access to the tables Genie queries.

### 4a — Find the Service Principal's Application ID

1. Go to **Settings → Identity & Access → Service Principals**
2. Find `app-XXXXX nexo-agent` (created automatically by Databricks Apps)
3. Click on it → **Configurations** tab
4. Copy the **Application ID** (a UUID like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

> **Important:** Use the Application ID UUID, not the display name. The display name does not work in SQL GRANT statements.

### 4b — Run GRANT Commands in SQL Editor

Open **SQL Editor** in Databricks and run:

```sql
-- Replace <APPLICATION_ID> with the UUID from step 4a
-- Replace catalog/schema/table names with the client's actual names

GRANT USE CATALOG ON CATALOG workspace TO `<APPLICATION_ID>`;

GRANT USE SCHEMA ON SCHEMA workspace.gold TO `<APPLICATION_ID>`;

GRANT SELECT ON TABLE workspace.gold.acquisition TO `<APPLICATION_ID>`;
```

Run each statement individually. If Genie queries multiple tables, add a `GRANT SELECT` for each one.

### 4c — Verify Access

After granting, ask a question in the app. If you still get `TABLES_MISSING_EXCEPTION`, check:
- The table name matches exactly (case-sensitive)
- The Application ID UUID was copied correctly (no extra spaces)
- The catalog/schema names are correct

---

## Step 5 — Verify the Deployment

| Check | Expected |
|---|---|
| App loads in browser | NexoBI UI renders, no "App not available" |
| No auth errors (401/403) | SDK uses auto-injected OAuth |
| Genie responds | Question returns an answer (not an error) |
| Data table shows | SQL results render in the UI |

---

## Environment Variables Reference

Databricks Apps **automatically injects** these — do not set them manually:

| Variable | Source | Purpose |
|---|---|---|
| `DATABRICKS_HOST` | Auto-injected | Workspace URL |
| `DATABRICKS_TOKEN` | Auto-injected | OAuth token |
| `DATABRICKS_CLIENT_ID` | Auto-injected | SP client ID |
| `DATABRICKS_CLIENT_SECRET` | Auto-injected | SP client secret |

You **can** set these in the App's environment settings (optional):

| Variable | Purpose |
|---|---|
| `NEXOBI_GENIE_SPACE_ID` | Override the Genie Space ID without changing code |

---

## Troubleshooting

### "App not available" on load
- Check the app logs in Databricks for Python errors
- Ensure `.streamlit/config.toml` exists with port 8080
- Make sure `app.yaml` has no extra `--server.*` flags

### `set_page_config` must be first command
- `st.set_page_config()` must be the very first Streamlit call in `app.py`
- Any `st.*` call before it (including `st.secrets`) will crash the app

### 401 Unauthorized
- Never override `DATABRICKS_TOKEN` with a PAT in `app.yaml`
- Use `WorkspaceClient()` with no arguments — it uses auto-injected credentials

### 403 Forbidden
- The service principal lacks permission to call the Genie API
- Check that the Genie Space is linked to the app in App resources

### `TABLES_MISSING_EXCEPTION`
- The service principal cannot access the underlying tables
- Follow Step 4 to grant Unity Catalog permissions using the Application ID UUID

### `PRINCIPAL_DOES_NOT_EXIST` on GRANT
- Use the **Application ID UUID** from the Configurations tab, not the display name
- Backtick the UUID in the SQL: `` GRANT ... TO `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`; ``

### "Multiple auth methods" SDK error
- Do not pass `token=` or `host=` to `WorkspaceClient()` when env vars are present
- Use `WorkspaceClient()` with no arguments

---

## Security Notes

- **Never commit tokens to git.** GitHub will flag them and they may be auto-revoked.
- Databricks Apps handles auth — no PAT tokens needed.
- The service principal is scoped to the workspace; grant only the minimum tables it needs.
- Rotate any accidentally exposed tokens immediately in **Settings → Developer → Access tokens**.

---

## Per-Client Checklist

Use this for each new client deployment:

- [ ] Fork/copy repo to client's git provider
- [ ] Update `GENIE_SPACE_ID` (in code or as env var in App settings)
- [ ] Deploy app on Databricks Apps
- [ ] Note the auto-created service principal name
- [ ] Get the service principal's Application ID UUID
- [ ] Run GRANT statements for all required tables
- [ ] Test end-to-end: ask a question, verify data returns
- [ ] Share app URL with client

---

*Last updated: March 2026*
