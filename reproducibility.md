# PitchBuddy — Reproducibility Guide

> Complete step-by-step instructions to clone, run locally, and deploy PitchBuddy from scratch on Google Cloud.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Prerequisites](#3-prerequisites)
4. [Project Structure](#4-project-structure)
5. [Local Setup](#5-local-setup)
6. [Environment Variables](#6-environment-variables)
7. [Firebase Setup](#7-firebase-setup)
8. [Running Locally](#8-running-locally)
9. [Google Cloud Deployment](#9-google-cloud-deployment)
10. [Verify Deployment](#10-verify-deployment)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Project Overview

**PitchBuddy** is an LLM-powered startup pitch simulator built on Google's AI and cloud infrastructure. It simulates a real investor conversation using Gemini 2.5 Flash — asking sharp VC questions and giving coach feedback after every response — with persistent multi-turn conversation history stored in Firebase Firestore.

**Key capabilities:**
- 5 investor personas (Angel, Seed VC, Series A VC, YC Partner, Corporate VC)
- Stage-adaptive difficulty (Idea → Series A+)
- Dual-role AI: VC challenger + pitch coach in every response
- Conversation persistence with persona/stage restored on reload
- No login required — anonymous UUID session isolation per browser tab

---

## 2. Architecture

```
User Browser
     │
     ▼
Cloud Run (Streamlit · Python 3.11)
     │                    │
     ▼                    ▼
Gemini 2.5 Flash     Firebase Firestore
(via LangChain)      (user-scoped conversation storage)
     ▲
     │
Secret Manager
(API key + Firebase credentials at runtime)
```

**Google services used:**

| Service | Role |
|---|---|
| Gemini 2.5 Flash | Core LLM — VC persona + coaching responses |
| Firebase Firestore | Persistent conversation and message storage |
| Cloud Run | Serverless container hosting |
| Cloud Build | CI/CD — builds Docker image and deploys |
| Artifact Registry / Container Registry | Stores Docker image |
| Secret Manager | Injects secrets into Cloud Run at runtime |

---

## 3. Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Google Cloud SDK | latest | https://cloud.google.com/sdk/docs/install |
| Docker | latest | https://docker.com (only needed for local container testing) |
| Git | any | https://git-scm.com |

---

## 4. Project Structure

```
pitchbuddy/
├── app.py                     # Streamlit entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── .dockerignore              # Files excluded from Docker image
├── cloudbuild.yaml            # Cloud Build CI/CD pipeline
├── .env.example               # Safe template for local secrets
├── .streamlit/
│   └── config.toml            # Streamlit server config
└── src/
    ├── config.py              # System prompt, persona prompts, stages, UI copy
    ├── ai/
    │   ├── agent.py           # LangChain chain + dynamic system prompt assembly
    │   └── clients.py         # Gemini LLM client (Streamlit-cached)
    ├── db/
    │   └── firestore.py       # Firestore CRUD, user-scoped collections
    ├── ui/
    │   ├── auth.py            # Anonymous UUID session isolation
    │   ├── chat.py            # Welcome screen + chat history rendering
    │   ├── input_bar.py       # Message input form
    │   ├── session.py         # Message processing, conversation loading
    │   ├── sidebar.py         # Persona/stage selectors, conversation list
    │   └── styles.py          # Full light theme CSS
    └── utils/
        └── retry.py           # Tenacity retry decorator (429 / 502 / 503)
```

---

## 5. Local Setup

**Clone the repository:**
```bash
git clone <repo-url>
cd pitchbuddy
```

**Create and activate a virtual environment:**
```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## 6. Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GOOGLE_API_KEY=AIzaSy...          # Gemini API key from AI Studio
FIREBASE_CREDENTIALS=firebase-credentials.json
```

**Get your Gemini API key:**
1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API key**
3. Select your GCP project
4. Copy the key — it starts with `AIza`

> **Note:** Use an AI Studio key, not a GCP Console key. Console keys with the "Gemini API" restriction enabled require a service account binding to work from Cloud Run.

---

## 7. Firebase Setup

**Step 1 — Create a Firebase project:**
1. Go to https://console.firebase.google.com
2. Click **Add project** → name it (e.g. `pitchbuddy`)
3. Google Analytics is optional, can be disabled

**Step 2 — Enable Firestore:**
1. In your Firebase project → **Build** → **Firestore Database**
2. Click **Create database**
3. Choose **Start in production mode**
4. Select a region (e.g. `us-central`)

**Step 3 — Set Firestore security rules:**

In Firestore → **Rules**, paste:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if true;
    }
  }
}
```
Click **Publish**. This allows unrestricted access to user-scoped paths (appropriate for anonymous sessions). Tighten rules if you add real authentication later.

**Step 4 — Download service account credentials:**
1. Firebase Console → **Project Settings** → **Service Accounts**
2. Click **Generate new private key**
3. Save the downloaded JSON as `firebase-credentials.json` in the project root

**Firestore data structure (auto-created on first use):**
```
users/
  {user_uuid}/
    conversations/
      {conv_id}/
        title:      "Ready — ask me to pitch"
        persona:    "Seed VC"
        stage:      "🌱 Pre-Seed"
        created_at: timestamp
        updated_at: timestamp
        messages/
          {msg_id}/
            role:    "user" | "assistant"
            content: "..."
            ts:      timestamp
```

Each browser session generates a fresh UUID. All data is scoped under `users/{uuid}/` — no two sessions share any documents.

---

## 8. Running Locally

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

**Expected behaviour on first run:**
- Sidebar shows **PitchBuddy** with a **New Chat** button
- Persona selector defaults to **Seed VC**, stage to **Pre-Seed**
- Welcome screen shows 6 suggestion cards
- After your first message, the conversation is saved to Firestore and appears in the sidebar
- Switching to a saved conversation restores the original persona and stage

> **Session scope:** Each browser tab generates its own anonymous UUID. Conversations are private and persist within the same tab session. Closing the tab or refreshing generates a new UUID — previous conversations remain in Firestore but are no longer reachable without the original UUID.

---

## 9. Google Cloud Deployment

### 9.1 — Initial GCP setup

```bash
# Authenticate
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com
```

### 9.2 — Store secrets in Secret Manager

```bash
# Store Gemini API key
# Write the key to a temp file with no trailing newline, then delete it

# macOS / Linux
printf 'AIzaSy...your-key...' > key.txt

# Windows CMD
echo|set /p="AIzaSy...your-key..." > key.txt

gcloud secrets create GOOGLE_API_KEY --data-file=key.txt
del key.txt   # or: rm key.txt

# Store Firebase credentials
gcloud secrets create FIREBASE_CREDENTIALS --data-file=firebase-credentials.json
```

If the secret already exists and you need to update it:
```bash
gcloud secrets versions add GOOGLE_API_KEY --data-file=key.txt
```

### 9.3 — Grant Cloud Run access to secrets

Cloud Run uses the Compute Engine default service account. Find your project number:

```bash
gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"
```

Then grant Secret Manager access to both secrets:

```bash
# Replace PROJECT_NUMBER with the value from above
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding FIREBASE_CREDENTIALS \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Also grant Cloud Build permission to deploy to Cloud Run:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 9.4 — Deploy via Cloud Build

From the project root:

```bash
gcloud builds submit --config cloudbuild.yaml .
```

This builds the Docker image, pushes it to Container Registry, and deploys to Cloud Run. First build takes approximately **4–6 minutes**.

### 9.5 — Make the app publicly accessible

```bash
gcloud run services add-iam-policy-binding pitchbuddy \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker
```

### 9.6 — Redeploy after code changes

```bash
gcloud builds submit --config cloudbuild.yaml .
```

Cloud Build uses `:latest` tag, so each deploy overwrites the previous image. To roll back to a previous revision:

```bash
# List revisions
gcloud run revisions list --service=pitchbuddy --region=us-central1

# Route traffic to a specific revision
gcloud run services update-traffic pitchbuddy \
  --region=us-central1 \
  --to-revisions=pitchbuddy-REVISION-ID=100
```

---

## 10. Verify Deployment

After deployment, Cloud Build prints:

```
Service URL: https://pitchbuddy-XXXXXXXXX.us-central1.run.app
```

**Smoke test checklist:**
- [ ] App loads in the browser without errors
- [ ] Sidebar shows persona and stage dropdowns
- [ ] Sending a message returns an AI response (with `[VC]` and `[COACH]` sections)
- [ ] Conversation appears in the sidebar after first message
- [ ] Switching to a saved conversation restores the original persona and stage
- [ ] Firebase Console → Firestore shows data under `users/{uuid}/conversations/`

---

## 11. Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `API key not valid` | Trailing newline in secret, wrong key type | Use AI Studio key (`AIza...`), re-store with `printf` not `echo` |
| `Permission denied on secret` | Cloud Run SA missing Secret Accessor role | Re-run Step 9.3 |
| `Billing not enabled` | No billing account linked | Link one at console.cloud.google.com/billing |
| `The caller does not have permission` on Cloud Build deploy | Cloud Build SA missing Cloud Run / SA User roles | Re-run the IAM bindings at end of Step 9.3 |
| Firestore not writing | Wrong credentials path or wrong project | Confirm `FIREBASE_CREDENTIALS` path and that the service account belongs to the Firebase project |
| App times out on first message | Cold start + slow first Gemini call | Cloud Run has `--timeout=300`; wait up to 30s on cold start |
| Conversations not persisting between deployments | Expected — anonymous UUIDs live in browser session state only | This is by design; Firestore data persists, but the UUID is regenerated on a new tab |
