# PuzzleVault AI Support Agent
**Author:** Tanish Shah

---

## What This Is

A Python-based AI customer support workflow for **PuzzleVault Experiences** — a premium escape room and immersive experience company. The agent, named Maya, handles end-to-end customer conversations across four stages: FAQ answering, lead qualification, escalation detection, and conversation summary.

Built with Groq (Llama 3.1 8B Instant) via an OpenAI-compatible client. No frontend — CLI only, as specified.

---

## Why PuzzleVault?

The assignment's sample SOP used a generic aesthetics clinic. I chose to build a custom SOP for an escape room business because:

- It's directly relevant to Breakout's own industry — the evaluators know this domain
- The qualification flow (group size, occasion, experience level) maps naturally to real booking decisions
- It demonstrates the SOP and prompts were designed for a specific business context, not filled in from a template

---

## Project Structure

```
closira/
├── main.py                          # Core workflow — all 4 stages
├── sop.json                         # SOP data for PuzzleVault Experiences
├── prompt_design.md                 # System prompt + all design decisions
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── .env                             # Your GROQ_API_KEY goes here (not committed)
├── .gitignore                       # Excludes venv, .env, escalation_log, __pycache__
├── escalation_log.json              # Auto-generated when escalation events occur
└── test_transcripts/
    ├── 01_in_sop_question.md        # Customer asks a question covered by the SOP
    ├── 02_out_of_scope.md           # Customer asks something not in the SOP
    ├── 03_escalation_trigger.md     # Angry customer / complaint / refund request
    ├── 04_lead_qualification.md     # Full 3-question qualification flow
    └── 05_conversation_summary.md   # End-to-end session with structured summary
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/RedPillCoder1/closira.git
cd closira
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key

Create a `.env` file in the project root:

```bash
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

Get a free key at [console.groq.com](https://console.groq.com). No credit card required.

### 5. Run

```bash
python main.py
```

Type `exit` at any point to end the session and trigger the conversation summary.

---

## How It Works — The 4 Stages

### Stage 1 — FAQ Answering
The full `sop.json` is injected into the system prompt as an f-string at runtime. The AI is strictly instructed to answer only from SOP data. Every AI response returns a structured JSON with a `confidence` flag: `HIGH`, `LOW`, or `OUT_OF_SCOPE`. Responses flagged `OUT_OF_SCOPE` are logged as SOP gaps and tracked by a counter.

### Stage 2 — Lead Qualification
Triggers automatically after the first successful FAQ response. Three questions are asked sequentially, one at a time — never batched. The qualification flow is controlled entirely by the Python layer (`in_qualification` flag, `qualification_step` counter) rather than the AI, keeping it deterministic. Answers are stored in a `lead_profile` dict and passed into the session summary.

**Questions asked:**
1. How many people will be joining you?
2. What's the occasion — birthday, corporate outing, or just a fun group hangout?
3. Have any of you done an escape room before, or will this be a first time?

### Stage 3 — Escalation Detection
Two independent layers run in parallel:

**Layer 1 — Python keyword detection** fires on every customer message *before* the AI is called. For clear anger or complaint signals, the AI is bypassed entirely. This is fast and deterministic.

**Layer 2 — AI self-reporting** — the model sets `"escalate": true` in its JSON response when it detects a trigger. This handles nuanced cases the keyword list can't catch.

All escalation events are logged to `escalation_log.json` with a timestamp, reason, and a 3-turn conversation snapshot.

**Escalation triggers:**
- Anger, frustration, or complaint keywords
- Refund requests
- Explicit request for a human or manager
- Question outside SOP scope (`OUT_OF_SCOPE`)
- 2 or more unanswered questions in a session
- Pricing negotiation beyond stated discounts

### Stage 4 — Conversation Summary
Triggered when the user types `exit`, `quit`, `bye`, or `done`. A separate AI call with `temperature: 0.1` generates a structured JSON summary covering customer intent, lead profile, SOP gaps identified, escalation history, and recommended next action for the human agent.

---

## Hallucination Prevention

Three mechanisms work together:

1. **Explicit denial prohibition in the system prompt** — the model is told that even a confident "we don't offer X" is fabrication if X is not in the SOP. This closes the loophole where a plausible-sounding denial feels safe to the model.
2. **OUT_OF_SCOPE answer constraint** — when escalating, the model's `answer` field is restricted to "I don't have that information on hand." No padding with invented context.
3. **Python-layer unanswered counter** — `unanswered_count` tracks `OUT_OF_SCOPE` responses. At 2+, escalation is forced at the system level regardless of model behaviour. Safety net against instruction drift.

---

## Tech Stack

| Component | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | Specified in assignment |
| LLM API | Groq (`llama-3.1-8b-instant`) | Free tier, OpenAI-compatible, sub-second latency |
| API Client | `openai` package | Works with Groq via `base_url` swap — one line to switch to GPT-4o |
| Env management | `python-dotenv` | Clean key management without shell exports |
| Interface | CLI | As specified — no frontend required |
| Storage | In-memory + `escalation_log.json` | Sufficient for single-session scope |

---

## Trade-offs and Known Limitations

**Groq free tier rate limits**
Groq's free tier allows ~30 RPM. A `time.sleep(0.5)` between API calls prevents hitting limits under normal usage. Under stress testing with rapid inputs this could be an issue. Easily resolved by upgrading to a paid tier or switching `base_url` to OpenAI.

**Full SOP injection vs RAG**
The entire `sop.json` is injected into the system prompt rather than retrieved dynamically. This is reliable and simple for a single small SOP, but would not scale to a multi-business platform. In production, RAG with Qdrant would be the right approach.

**Static keyword list for sentiment**
The escalation keyword list is hardcoded. A production system would use a lightweight sentiment classifier to catch implicit frustration that doesn't use obvious keywords.

**No session persistence**
Conversation history lives in memory only. Restarting the script starts a fresh session. A production deployment would store history in a database keyed by customer ID.

**Summary call on long sessions**
The session summary passes the full conversation history in a single prompt. Very long sessions could approach context limits for the 8B model. Mitigation: summarise incrementally or switch to a larger context model for the summary step.