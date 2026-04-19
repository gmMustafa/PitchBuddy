# PitchBuddy

> AI-powered startup pitch simulator. Practice your pitch against a skeptical VC, get coached in real time, and sharpen your story before the real meeting.

**Live demo:** *(add your Cloud Run URL here)*

---

## Overview

PitchBuddy combines two AI roles in every response:

- **[VC]** Asks one sharp, targeted question aimed at your weakest assumption
- **[COACH]** Tells you what landed, what didn't, and one concrete improvement

Select your investor type and funding stage before you start — the AI adjusts its behavior, scrutiny level, and focus areas accordingly. Conversations are saved to Firestore and can be resumed within the same browser session.

---

## Features

- **5 investor personas** — Angel, Seed VC, Series A VC, YC Partner, Corporate VC, each with distinct behavior and priorities
- **4 founder stages** — Idea through Series A+, which controls how aggressive the AI's questioning gets
- **Persistent chat history** — Conversations saved to Firestore and restored with the original persona and stage (scoped to the browser session — closing the tab starts fresh)
- **Suggestion cards** — One-click prompts to drill into TAM, business model, defensibility, traction, funding ask
- **Zero friction** — No account creation; each browser session is automatically isolated

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| UI | Streamlit | App framework, chat interface, custom CSS |
| LLM | Gemini 2.5 Flash | AI responses via LangChain |
| Database | Firebase Firestore | Conversation persistence, user-scoped |
| Session auth | Anonymous UUID | Per-browser-tab isolation, no login required |
| Retry logic | Tenacity | Handles Gemini 429 / 502 / 503 errors |
| Containerization | Docker | Reproducible builds |
| Deployment | Google Cloud Run | Serverless, scales to zero |
| CI/CD | Google Cloud Build | Auto-deploy on push |
| Secrets | Google Secret Manager | API keys and credentials at runtime |

---

## Local Setup

**Prerequisites:** Python 3.11+, a [Google AI Studio API key](https://aistudio.google.com/app/apikey), Firebase project with Firestore enabled.

```bash
# Clone and enter
git clone https://github.com/your-username/pitchbuddy.git
cd pitchbuddy

# Create virtualenv
python -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Open .env and paste your GOOGLE_API_KEY

# Add Firebase service account
# Firebase Console → Project Settings → Service Accounts → Generate new private key
# Save the downloaded file as: firebase-credentials.json

# Run
streamlit run app.py
```

App runs at `http://localhost:8501`.

---

## Project Structure

```
pitchbuddy/
├── app.py                    # Entry point — layout, routing, session handling
├── src/
│   ├── config.py             # System prompt, persona prompts, stages, UI copy
│   ├── ai/
│   │   ├── agent.py          # LangChain chain, dynamic system prompt assembly
│   │   └── clients.py        # Gemini LLM client (Streamlit-cached)
│   ├── db/
│   │   └── firestore.py      # Firestore read/write, user-scoped collections
│   ├── ui/
│   │   ├── auth.py           # Anonymous UUID session isolation
│   │   ├── chat.py           # Welcome screen, chat history rendering
│   │   ├── input_bar.py      # Message input and submission
│   │   ├── session.py        # Message processing, conversation loading
│   │   ├── sidebar.py        # Persona/stage selectors, conversation list
│   │   └── styles.py         # Full light theme CSS
│   └── utils/
│       └── retry.py          # Tenacity retry decorator for API calls
├── Dockerfile
├── cloudbuild.yaml
├── requirements.txt
└── .env.example
```

---

## Deployment

Full step-by-step guide: [REPRODUCIBILITY.md](REPRODUCIBILITY.md)

Covers Firebase setup, GCP project config, Secret Manager, Cloud Build trigger, and Cloud Run deploy flags.

---

## Design Decisions

**No login required.** Each Streamlit browser session gets a UUID on first load. All Firestore writes are scoped to `users/{uuid}/conversations/`. Sessions are private by construction — there is no shared state between tabs or users.

**Persona injected per call, not stored in history.** The selected investor persona and founder stage are appended to the system prompt on every API call. This means switching personas mid-conversation takes effect immediately, and the full behavioral instructions are never diluted by growing chat history.

**`thinking_budget=0`.** Gemini 2.5 Flash supports extended thinking which can add 30–120s of latency. Disabled here — the base model handles pitch coaching well, and fast back-and-forth is more valuable than extra reasoning depth.

**Two-phase rerun for conversation switching.** Loading a saved conversation needs to restore `persona` and `stage` into session state *before* the sidebar selectboxes render. A direct call would raise a `StreamlitAPIException`. Instead, clicking a conversation sets a `_load_conv_id` key and reruns; on the next run, the app processes it at the top before any widgets are instantiated.
