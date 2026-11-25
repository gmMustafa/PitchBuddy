# PitchBuddy — Reproducibility Guide

> Everything you need to rebuild PitchBuddy from scratch: run it locally, set up Firebase and Google Sign-In, and deploy it on **Streamlit Community Cloud** (free, recommended) or **Google Cloud Run** (alternative).
>
> For a screenshot walkthrough of the app itself, see [flow.md](flow.md).

**Live instance:** <https://pitchbudddy.streamlit.app/>

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Prerequisites](#3-prerequisites)
4. [Project Structure](#4-project-structure)
5. [Local Setup](#5-local-setup)
6. [Configuration](#6-configuration)
7. [Groq API Key](#7-groq-api-key)
8. [Firebase Setup](#8-firebase-setup)
9. [Google Sign-In Setup](#9-google-sign-in-setup)
10. [Running Locally](#10-running-locally)
11. [Deploy: Streamlit Community Cloud (recommended)](#11-deploy-streamlit-community-cloud-recommended)
12. [Deploy: Google Cloud Run (alternative)](#12-deploy-google-cloud-run-alternative)
13. [Verify Deployment](#13-verify-deployment)
14. [Free-Tier Limits & Cost Safety](#14-free-tier-limits--cost-safety)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Project Overview

**PitchBuddy** is an LLM-powered startup pitch simulator. The founder pitches, and every AI reply has two parts:

- **[VC]** — one sharp, skeptical question aimed at the weakest assumption
- **[COACH]** — what worked, what didn't, and one actionable improvement

**Key capabilities:**
- 5 investor personas: Angel, Seed VC, Series A VC, YC Partner, Corporate VC
- 4 founder stages that set the difficulty: Idea → Pre-Seed → Seed → Series A+
- Two ways in: **Google Sign-In** (history saved in Firestore) or **Guest** (history in memory for that tab only)
- Saved conversations restore the persona and stage they were created with
- Built-in limits so one shared Groq key can serve a public demo for free

---

## 2. Architecture

```
                 User Browser
                      │
                      ▼
      Streamlit app (Python 3.11) — app.py
        │             │                 │
        ▼             ▼                 ▼
   Google OAuth   Groq API           Storage router (src/db/store.py)
   (Authlib)      gpt-oss-120b         ├─ Firestore      ← signed-in users
                  └─ 429 → gpt-oss-20b └─ session_state  ← guests
```

| Component | Role |
|---|---|
| **Streamlit** | UI, session state, hosting runtime |
| **Groq** (`openai/gpt-oss-120b`, fallback `openai/gpt-oss-20b`) via LangChain | VC + coach responses |
| **Tenacity** | Retries on 502/503 and per-minute 429s |
| **Authlib** | Google OAuth 2.0 redirect flow |
| **Firebase Firestore** (Admin SDK) | Saved history for signed-in users |
| **Streamlit Community Cloud** | Free public hosting (primary) |
| **GitHub Actions** | Keep-alive ping so the free app doesn't sleep |
| Docker + Cloud Build + Cloud Run | Optional alternative hosting |

**Request lifecycle (one message):**
1. `src/ui/session.py` checks the per-session message limit, then saves the user message.
2. `src/ai/agent.py` builds the prompt: system prompt + persona instructions + stage + the last `MAX_HISTORY_MESSAGES` turns.
3. `src/ai/clients.py` calls `gpt-oss-120b` with `reasoning_effort="low"` and a token cap. If it returns 429, the same request is sent to `gpt-oss-20b`.
4. The reply is saved and rendered. Errors show as a warning banner, not a traceback.

---

## 3. Prerequisites

| Requirement | Needed for | Where |
|---|---|---|
| Python **3.11+** | Everything | python.org |
| Git + a GitHub account | Cloning / Streamlit Cloud deploy | github.com |
| **Groq API key** (free) | AI replies — *the only required secret* | console.groq.com |
| Firebase project with Firestore | Saved history for signed-in users | console.firebase.google.com |
| Google Cloud OAuth client | Google Sign-In | console.cloud.google.com |
| Streamlit Community Cloud account | Free hosting | share.streamlit.io |
| `gcloud` CLI + billing account | Only for the Cloud Run option | cloud.google.com/sdk |

> **Minimum to run:** Python plus a Groq key. Guest mode works without Firebase or OAuth.

---

## 4. Project Structure

```
PitchBuddy/
├── app.py                         # Streamlit entry point: auth gate, layout, routing
├── requirements.txt               # Python dependencies
├── flow.md                        # User walkthrough with screenshots
├── reproducibility.md             # This file
├── .env.example                   # Template for local secrets
├── .streamlit/
│   ├── config.toml                # Theme + server config
│   └── secrets.toml.example       # Template for Streamlit Cloud secrets (TOML)
├── .github/workflows/
│   └── keep-alive.yml             # Pings the app every 6h so it doesn't sleep
├── Dockerfile / .dockerignore     # Container build (Cloud Run option)
├── cloudbuild.yaml                # Cloud Build → Cloud Run pipeline
├── docs/screenshots/              # UI screenshots used in README / flow.md
└── src/
    ├── config.py                  # Settings loader (env → st.secrets), prompts, personas, limits
    ├── ai/
    │   ├── agent.py               # Prompt assembly, history window, model fallback
    │   └── clients.py             # Cached Groq clients (primary + fallback)
    ├── db/
    │   ├── store.py               # Routes to Firestore (signed in) or session_store (guest)
    │   ├── firestore.py           # Firestore CRUD; credentials from secrets/env/file
    │   └── session_store.py       # In-memory guest storage
    ├── ui/
    │   ├── auth.py                # Google OAuth redirect flow + Guest mode
    │   ├── chat.py                # Suggestion cards + chat rendering
    │   ├── input_bar.py           # Message input form
    │   ├── session.py             # Message processing, limits, error banner
    │   ├── sidebar.py             # Persona/stage pickers, recent conversations
    │   └── styles.py              # Custom CSS
    └── utils/
        └── retry.py               # Tenacity retry policy + rate-limit detection
```

---

## 5. Local Setup

```bash
git clone https://github.com/gmMustafa/PitchBuddy.git
cd PitchBuddy

python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

---

## 6. Configuration

Settings are read from **environment variables / `.env` first**, then from **`st.secrets`** (`.streamlit/secrets.toml` locally, or the Secrets box on Streamlit Cloud). See `src/config.py`.

| Key | Required | Default | Purpose |
|---|---|---|---|
| `GROQ_API_KEY` | **Yes** | — | Groq API key |
| `GOOGLE_CLIENT_ID` | For sign-in | — | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | For sign-in | — | OAuth client secret |
| `OAUTH_REDIRECT_URI` | For sign-in | `http://localhost:8501` | Must exactly match an authorised redirect URI |
| `[firebase]` TOML table | For history | — | Service-account fields (Streamlit Cloud) |
| `FIREBASE_CREDENTIALS_JSON` | For history | — | Service-account JSON as a single string |
| `FIREBASE_CREDENTIALS` | For history | `firebase-credentials.json` | Path to the service-account file (local / Cloud Run) |
| `GROQ_MODEL` | No | `openai/gpt-oss-120b` | Primary model |
| `GROQ_FALLBACK_MODEL` | No | `openai/gpt-oss-20b` | Used when the primary returns 429 |
| `MAX_RESPONSE_TOKENS` | No | `900` | Max tokens per reply (reasoning included) |
| `MAX_HISTORY_MESSAGES` | No | `12` | Number of past messages sent each turn |
| `MAX_MESSAGES_PER_SESSION` | No | `40` | User messages allowed per browser session |

Firebase credentials are checked in this order: `[firebase]` table → `FIREBASE_CREDENTIALS_JSON` → `FIREBASE_CREDENTIALS` file.

Example `.env`:
```env
GROQ_API_KEY=gsk_...
FIREBASE_CREDENTIALS=firebase-credentials.json
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
OAUTH_REDIRECT_URI=http://localhost:8501
```

---

## 7. Groq API Key

1. Go to <https://console.groq.com/keys> and sign in.
2. Click **Create API Key** and copy it (it starts with `gsk_`).
3. Put it in `.env` as `GROQ_API_KEY`.
4. Check the per-model rate limits at <https://console.groq.com/settings/limits>.

> **Model availability changes.** Groq retires models; `llama-3.3-70b-versatile` has already been removed. To see which models your key can use:
> ```bash
> python -c "import groq,os;from dotenv import load_dotenv;load_dotenv();[print(m.id) for m in groq.Groq().models.list().data]"
> ```
> Change models by setting `GROQ_MODEL` / `GROQ_FALLBACK_MODEL`; no code change needed.

---

## 8. Firebase Setup

*Only needed for signed-in users' history. Guests never touch Firestore.*

**Step 1: Create a project and database**
1. <https://console.firebase.google.com> → **Add project** (Analytics optional).
2. **Build → Firestore Database → Create database → Start in production mode** → pick a region.
3. Stay on the free **Spark** plan; see [§14](#14-free-tier-limits--cost-safety).

**Step 2: Lock down security rules**

The app uses the **Admin SDK**, which bypasses security rules, so browser clients don't need any access. In **Firestore → Rules**, deny everything:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

> ⚠️ Don't use `allow read, write: if true`. It lets anyone who knows your project ID read and change every conversation.

**Step 3: Download the service-account key**
1. **Project Settings → Service Accounts → Generate new private key**.
2. Save it as `firebase-credentials.json` in the project root. It's gitignored and dockerignored, so never commit it.

**Data layout (created on first use):**
```
users/
  {google_user_id}/            # Google "sub" claim, stable across visits
    conversations/
      {conv_id}/
        title, persona, stage, created_at, updated_at
        messages/
          {msg_id}/  role: "user" | "assistant", content, ts
```

---

## 9. Google Sign-In Setup

*Optional. Without it the Google button won't work, but Guest mode will.*

1. <https://console.cloud.google.com> → choose the same project as Firebase (or any project).
2. **APIs & Services → OAuth consent screen**: user type **External**, app name *PitchBuddy*, scopes `openid`, `email`, `profile` (all non-sensitive, so no Google verification is needed).
3. **Publish** the consent screen. In *Testing* mode only listed test users can sign in.
4. **Credentials → Create credentials → OAuth client ID → Web application.**
5. Under **Authorised redirect URIs**, add every place the app runs:
   - `http://localhost:8501`
   - `https://pitchbudddy.streamlit.app` (your Streamlit Cloud URL)
   - your Cloud Run URL, if you use it
6. Copy the client ID and secret into `.env` / secrets. `OAUTH_REDIRECT_URI` must match the environment exactly, with no trailing slash difference.

---

## 10. Running Locally

```bash
streamlit run app.py
```

Open <http://localhost:8501>.

**Expected behaviour:**
- Landing page with **Sign in with Google** and **Continue as Guest**
- After entering: sidebar with **New Chat**, persona (default *Seed VC*), stage (default *Pre-Seed*), **Recents**
- Six suggestion cards; clicking one starts a conversation
- Every reply after the opening has a `[VC]` question and a `[COACH]` block
- Guest: history disappears when the tab closes. Signed in: history appears under **Recents** on later visits

**Docker (optional):**
```bash
docker build -t pitchbuddy .
docker run --rm -p 8501:8501 --env-file .env \
  -v "$PWD/firebase-credentials.json:/app/firebase-credentials.json:ro" pitchbuddy
```

---

## 11. Deploy: Streamlit Community Cloud (recommended)

Free, no billing account, and it redeploys automatically on every push to `main`.

**Step 1: Push to GitHub.** Public or private repo. Make sure `.env`, `firebase-credentials.json` and `.streamlit/secrets.toml` are **not** committed (they're gitignored).

**Step 2: Create the app**
1. <https://share.streamlit.io> → **Create app → Deploy a public app from GitHub**.
2. Repository: `gmMustafa/PitchBuddy`, branch `main`, main file `app.py`.
3. **App URL:** choose a subdomain (live instance: `pitchbudddy`).
4. **Advanced settings → Python version: 3.11.**

**Step 3: Add secrets (TOML)**

Paste into **Advanced settings → Secrets** (or later: app **⋮ → Settings → Secrets**). Template: [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example).

```toml
GROQ_API_KEY = "gsk_..."
GOOGLE_CLIENT_ID = "xxxxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-..."
OAUTH_REDIRECT_URI = "https://pitchbudddy.streamlit.app"

[firebase]
type = "service_account"
project_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
# ...remaining fields from firebase-credentials.json
```

Generate the `[firebase]` block from your JSON file instead of copying it by hand:
```bash
python -c "import json;d=json.load(open('firebase-credentials.json'));print('[firebase]');[print(f'{k} = {json.dumps(v)}') for k,v in d.items()]"
```

**Step 4: Deploy.** The first build takes about 2–4 minutes. Then add the app URL to the OAuth redirect URIs ([§9](#9-google-sign-in-setup)).

**Step 5: Keep it awake**

Free apps sleep after about 12 hours with no visitors. [`.github/workflows/keep-alive.yml`](.github/workflows/keep-alive.yml) opens the app in headless Chromium every 6 hours and clicks the wake button if the app is asleep.

1. GitHub repo → **Settings → Secrets and variables → Actions → Variables → New repository variable**.
2. Name `APP_URL`, value `https://pitchbudddy.streamlit.app`.
3. **Actions → keep-alive → Run workflow** to test it.

> GitHub disables scheduled workflows after 60 days with no repo activity. If that happens, re-enable it from the **Actions** tab.

**Updating:** `git push` to `main` redeploys. Changes to secrets restart the app.

---

## 12. Deploy: Google Cloud Run (alternative)

Use this if you need custom domains, more memory, or no sleeping. It **requires a billing account**; Cloud Run's free tier usually covers a small app, but set a budget alert.

### 12.1 Enable APIs
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  secretmanager.googleapis.com containerregistry.googleapis.com
```

### 12.2 Store secrets
```bash
# printf avoids a trailing newline, which breaks API keys
printf '%s' 'gsk_...'              | gcloud secrets create GROQ_API_KEY --data-file=-
printf '%s' 'xxxxx.apps.googleusercontent.com' | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
printf '%s' 'GOCSPX-...'           | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-
gcloud secrets create FIREBASE_CREDENTIALS --data-file=firebase-credentials.json
```
To update a secret later: `gcloud secrets versions add NAME --data-file=...`

### 12.3 Grant access
```bash
PN=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")

for s in GROQ_API_KEY GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET FIREBASE_CREDENTIALS; do
  gcloud secrets add-iam-policy-binding $s \
    --member="serviceAccount:${PN}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PN}@cloudbuild.gserviceaccount.com" --role="roles/run.admin"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PN}@cloudbuild.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
```

### 12.4 Build and deploy
```bash
gcloud builds submit --config cloudbuild.yaml .
```
[`cloudbuild.yaml`](cloudbuild.yaml) builds the image, pushes it, and deploys the `pitchbuddy` service to `us-central1` with the secrets above. The first build takes about 4–6 minutes.

### 12.5 Set the OAuth redirect
After the first deploy, copy the service URL, add it to the OAuth client's redirect URIs, and set it on the service:
```bash
gcloud run services update pitchbuddy --region=us-central1 \
  --update-env-vars=OAUTH_REDIRECT_URI=https://pitchbuddy-XXXXXXXX.us-central1.run.app
```

### 12.6 Roll back
```bash
gcloud run revisions list --service=pitchbuddy --region=us-central1
gcloud run services update-traffic pitchbuddy --region=us-central1 \
  --to-revisions=pitchbuddy-REVISION-ID=100
```

---

## 13. Verify Deployment

- [ ] App loads; landing page shows both sign-in options
- [ ] **Guest:** a suggestion card returns an AI reply
- [ ] After the opening questions, replies contain `[VC]` and `[COACH]`
- [ ] Dollar amounts (e.g. `$4k MRR, raising $750k`) display as plain text, not maths formatting
- [ ] **Google sign-in** redirects back and shows your name in the sidebar
- [ ] Signed-in conversation appears under **Recents**; reopening it restores persona and stage
- [ ] Firebase Console → Firestore shows `users/{id}/conversations/...`
- [ ] *(Streamlit Cloud)* the **keep-alive** workflow run succeeds

---

## 14. Free-Tier Limits & Cost Safety

| Service | Free allowance | What happens when it runs out | How you could be charged |
|---|---|---|---|
| **Groq** | Per-model RPM / RPD / TPM / TPD limits ([console](https://console.groq.com/settings/limits)) | 429 → app retries, then falls back to `gpt-oss-20b`, then shows "AI is busy" until the limit resets | Only if you add a payment method (Developer tier) |
| **Firestore** (Spark) | Daily read/write/delete quota + 1 GiB storage | Writes and reads fail until the daily reset (midnight Pacific); guests unaffected | Only if you upgrade to Blaze |
| **Streamlit Cloud** | Free; about 1 GB RAM per app | Slows down or restarts under heavy load; sleeps when idle | Never |
| **Cloud Run** (option) | Monthly free tier | Billed beyond it | Requires billing; set a budget alert |

**Built-in limits** (all adjustable in config, see [§6](#6-configuration)): fallback model on 429, `reasoning_effort="low"`, `MAX_RESPONSE_TOKENS=900`, `MAX_HISTORY_MESSAGES=12`, `MAX_MESSAGES_PER_SESSION=40`.

> The per-session limit resets when the page is refreshed. If someone abuses the demo, the worst case is that the Groq quota runs out for the day; it never costs money on the free tier. To tighten things further: lower `MAX_MESSAGES_PER_SESSION`, remove Guest mode, or add a bring-your-own-key field.

---

## 15. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `model_not_found` / 404 from Groq | Model retired | List the models available to your key ([§7](#7-groq-api-key)) and set `GROQ_MODEL` |
| "The AI is busy right now…" banner | Groq rate limit on both models | Wait for the limit to reset; check usage in the Groq console |
| `Connection error` / `CERTIFICATE_VERIFY_FAILED` locally (Windows) | Antivirus HTTPS scanning (Avast/AVG/Kaspersky) re-signs TLS | Turn off HTTPS scanning for Python, or use the Windows-certificate workaround in [flow.md §3](flow.md#3-run-it-locally); for git: `git config http.sslBackend schannel` |
| `redirect_uri_mismatch` on Google sign-in | `OAUTH_REDIRECT_URI` doesn't exactly match an authorised URI | Add the exact URL in Google Cloud Credentials (note the spelling: `pitchbudddy`) |
| "Access blocked: app is in testing" | Consent screen not published | OAuth consent screen → **Publish app** |
| `Firebase credentials not configured` | No `[firebase]` secret / JSON / file found | Add credentials ([§8](#8-firebase-setup), [§11](#11-deploy-streamlit-community-cloud-recommended)) |
| `Invalid private key` from Firebase | Newlines lost when pasting `private_key` | Generate the `[firebase]` block with the script in §11; keep the `\n` escapes |
| Secrets changes ignored locally | `.env` takes priority over `secrets.toml` | Edit `.env`, or remove the key from it |
| App says "This app has gone to sleep" | Idle more than about 12 hours on Streamlit Cloud | Click wake; make sure the keep-alive workflow has `APP_URL` set and is enabled |
| Streamlit Cloud build fails on dependencies | Unpinned package released a breaking change | Pin the offending package in `requirements.txt`; check the build log in **Manage app** |
| `Permission denied on secret` (Cloud Run) | Missing Secret Accessor role | Re-run §12.3 |
