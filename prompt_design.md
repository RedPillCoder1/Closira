# Prompt Design — PuzzleVault AI Support Agent (Maya)

**Author:** Tanish Shah  
**Business:** PuzzleVault Experiences (custom SMB, escape room industry)

---

## 1. System Prompt

```
You are Maya, a friendly and professional AI customer support agent for PuzzleVault Experiences — a premium escape room and immersive experience company.

Your job is to help customers with questions, qualify their interest, detect when to escalate, and always stay grounded in the SOP data below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SOP DATA (your only source of truth):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Full SOP JSON injected here at runtime via f-string]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRICT RULES:
1. ONLY answer from the SOP data above. If the answer is not explicitly stated in the SOP,
   do NOT guess, deny, or infer. Even a denial like "we don't offer X" is fabrication if X
   is not mentioned in the SOP. Set confidence to OUT_OF_SCOPE and escalate immediately.
2. When escalating due to OUT_OF_SCOPE, your "answer" field must simply be:
   "I don't have that information on hand." Nothing else. Do not describe what the business
   offers or doesn't offer.
3. If you are uncertain or the question is outside the SOP, set confidence to "OUT_OF_SCOPE"
   and escalate.
4. Never make up prices, room details, policies, or offers not listed in the SOP.
5. Always be warm, concise, and human-feeling. Do not sound robotic.
6. Ask qualification questions one at a time — never dump all questions at once.

ESCALATION TRIGGERS (set escalate: true if ANY of these are true):
- Customer expresses anger, frustration, or makes a complaint
- Customer asks for a refund
- Customer requests a human agent or manager
- Question cannot be answered from the SOP
- Customer has asked more than 2 questions you couldn't answer
- Pricing negotiation beyond stated discounts

TONE GUIDELINES:
- Warm and enthusiastic — this is a fun, exciting product
- Professional but not stiff
- Concise — customers on WhatsApp don't want essays
- Use the customer's name if they've shared it

RESPONSE FORMAT:
You MUST respond with valid JSON only. No markdown, no extra text. Use this exact schema:

{
  "answer": "<your response to the customer — this is what they see>",
  "confidence": "<HIGH | LOW | OUT_OF_SCOPE>",
  "escalate": <true | false>,
  "escalation_reason": "<brief reason if escalate is true, else null>",
  "stage": "<faq | qualification | escalation | summary>"
}
```

---

## 2. Key Design Decisions

### Why JSON-structured output?

Forcing the model to respond in a strict JSON schema is the single most important design decision in this prompt. It creates a **machine-readable control layer** on top of the natural language response:

- `confidence` lets the Python layer independently verify whether the AI felt it could answer
- `escalate` allows the AI to self-report when it should hand off, rather than relying solely on keyword matching
- `stage` tracks where in the workflow the conversation currently is
- Structured output eliminates the ambiguity of trying to parse intent from free-form text

This is not just a formatting preference — it is the reliability mechanism.

### Why inject the full SOP into the system prompt?

Rather than using retrieval (RAG), the full SOP JSON is injected directly into the system prompt as an f-string at runtime. This is a deliberate choice for this scope:

- The SOP is small enough (~2KB) to fit comfortably within the context window
- Direct injection guarantees the model always has complete context — no retrieval misses
- For production at scale with multiple businesses, RAG with a vector database (e.g., Qdrant) would be the right approach, but for a single-business SMB workflow, full injection is more reliable and simpler to reason about

### Why `temperature: 0.3`?

Lower temperature reduces creative deviation. For a support agent that must stay within SOP boundaries, high temperature is a liability — it encourages the model to "fill in" information it doesn't have. 0.3 gives enough flexibility for natural-sounding responses while keeping the model grounded.

### Why python-dotenv?

The final code uses `python-dotenv` with a `.env` file to manage the `GROQ_API_KEY`. This is a cleaner approach than relying solely on shell exports — it makes the project self-contained and easier to run without environment setup instructions being the first thing someone hits.

---

## 3. Hallucination Prevention

Three explicit mechanisms work together:

**A. Instruction-level grounding with explicit denial prohibition**

The system prompt says: *"If the answer is not explicitly stated in the SOP, do NOT guess, deny, or infer. Even a denial like 'we don't offer X' is fabrication if X is not mentioned in the SOP."*

This rule was added after observing the model confidently saying "We don't offer VR rooms" — a hallucinated denial that sounded accurate but had no SOP basis. The rule closes the loophole where a model treats a plausible-sounding "no" as safe.

**B. OUT_OF_SCOPE answer constraint**

Rule 2 in the system prompt restricts the `answer` field when escalating: *"your answer field must simply be: 'I don't have that information on hand.' Nothing else."* This prevents the model from padding an escalation response with invented context about what the business does or doesn't offer.

**C. Confidence flag + Python-layer counter**

The model outputs `OUT_OF_SCOPE` when it cannot answer. The Python layer tracks this with `unanswered_count`. At 2 or more, escalation is forced at the system level — independently of whether the model remembered to set `escalate: true`. This is a safety net against model instruction drift over long conversations.

**D. Low temperature**

`temperature: 0.3` reduces the model's tendency to generate plausible-sounding but fabricated details.

---

## 4. Confidence-Based Escalation Logic

The model outputs one of three confidence levels with every response:

| Confidence | Meaning | Python Action |
|---|---|---|
| `HIGH` | Answer found clearly in SOP | Respond normally, continue flow |
| `LOW` | Partial match or uncertain | Log, monitor — escalate if repeated |
| `OUT_OF_SCOPE` | No SOP coverage | Increment `unanswered_count`; escalate at 2+ |

Additionally, the model can directly set `"escalate": true` for any response, regardless of confidence level. This handles cases like sentiment detection where confidence in the answer may still be HIGH, but escalation is required for other reasons (e.g. a complaint framed as a polite question).

The Python layer also independently counts `OUT_OF_SCOPE` responses via `unanswered_count`. If this reaches 2, escalation is forced at the system level — this prevents a model that fails to self-flag from staying in a loop giving non-answers.

---

## 5. Dual-Layer Escalation System

Two independent escalation mechanisms run in parallel:

**Layer 1 — Python keyword detection (fires before AI call)**

```python
ESCALATION_KEYWORDS = [
    "refund", "complaint", "ridiculous", "terrible", "awful", "angry",
    "frustrated", "unacceptable", "speak to someone", "human", "manager",
    "this is a joke", "waste of money", "disgusting", "horrible", "worst"
]
```

This runs on every customer message before the AI is invoked. For clear anger or complaint signals, the AI is bypassed entirely — speed and safety over nuance. This layer catches the obvious cases deterministically.

**Layer 2 — AI self-reporting (fires after AI call)**

The model sets `"escalate": true` in its JSON response when it detects a trigger. This handles nuanced cases the keyword list can't capture — implicit frustration, indirect requests for a manager, or uncertainty about whether a question is in scope.

This redundancy is intentional. Neither layer alone is sufficient. Keywords miss subtlety; the AI can miss obvious sentiment. Together, they cover the full range.

All escalations are logged to `escalation_log.json` with timestamp, reason, and a conversation snapshot of the last 3 turns.

---

## 6. Tone and Persona

**Name:** Maya  
**Personality:** Warm, enthusiastic, concise. Treats every customer like they're booking something genuinely fun, not just filling out a form.

**Design rationale:**
- Escape rooms are a *fun product*. A robotic, stiff tone would be a brand mismatch.
- SMB customers on WhatsApp expect conversational, fast responses — not long paragraphs.
- The name "Maya" gives the agent a human feel without pretending to be human.
- Tone guidance is embedded in the system prompt as explicit instructions rather than left to model defaults, ensuring consistency.

**What Maya does NOT do:**
- Apologise excessively
- Use corporate filler phrases
- Give essay-length responses to simple questions
- Pretend to know things she doesn't

---

## 7. Lead Qualification Design

Qualification questions are asked **one at a time**, sequentially, only after a successful FAQ response. This mirrors natural human conversation and avoids the "form-filling" feel of dumping all questions at once.

The qualification flow is managed entirely by the Python layer — not the AI. The `in_qualification` flag and `qualification_step` counter control which question is asked next, and answers are stored in the `lead_profile` dict via `handle_qualification_response()`. This keeps the qualification logic deterministic and independent of model behaviour.

The three questions are:
1. **Group size** — determines which rooms are available and pricing tier
2. **Occasion** — enables personalised recommendation (birthday package vs corporate vs casual)
3. **Experience level** — helps recommend appropriate difficulty tier

Answers are passed into the session summary prompt at conversation end.

---

## 8. Summary Generation

The session summary is a **separate API call** with its own focused system prompt. It receives:
- Full conversation history
- Collected lead profile
- SOP gaps list
- Escalation log

`temperature: 0.1` is used for the summary call — lower than the main agent — because the summary is a structured data extraction task, not a conversational one. The output schema is fixed JSON covering intent, lead profile, SOP gaps, escalation status, and recommended next action.

---

## 9. SOP Data Used

**Business:** PuzzleVault Experiences (custom SMB — escape room / immersive experiences)

Covers:
- 4 themed rooms with difficulty tiers, capacity, duration, and per-person pricing
- Business hours, location, contact channels, booking methods
- Booking and cancellation policy
- Corporate packages (10+ people, custom quote)
- Birthday packages (complimentary decoration and group photo)
- Discount structure (weekday 10%, student 15%, loyalty 10%)
- FAQ answers (parking, hints, photography, accessibility, food, gift vouchers)
- Escalation rules and escalation message

**Why a custom SOP?** The assignment's sample SOP (Bloom Aesthetics Clinic) is generic. Building a domain-specific SOP for an escape room company — which mirrors Breakout's own business — demonstrates that the candidate has thought about real SMB communication needs, not just implemented a template.