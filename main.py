"""
Closira AI Assignment — PuzzleVault Experiences
Author: Tanish Shah
A 4-stage AI customer support workflow: FAQ -> Lead Qualification -> Escalation -> Summary
"""

import json
import os
import re
import time
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = "llama-3.1-8b-instant"

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

#Load SOP
with open("sop.json", "r") as f:
    SOP = json.load(f)

SOP_TEXT = json.dumps(SOP, indent=2)


SYSTEM_PROMPT = f"""
You are Maya, a friendly and professional AI customer support agent for PuzzleVault Experiences — a premium escape room and immersive experience company.

Your job is to help customers with questions, qualify their interest, detect when to escalate, and always stay grounded in the SOP data below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SOP DATA (your only source of truth):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{SOP_TEXT}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRICT RULES:
1. ONLY answer from the SOP data above. If the answer is not explicitly stated in the SOP, do NOT guess, deny, or infer. Even a denial like "we don't offer X" is fabrication if X is not mentioned in the SOP. Set confidence to OUT_OF_SCOPE and escalate immediately.
2. When escalating due to OUT_OF_SCOPE, your "answer" field must simply be: "I don't have that information on hand." Nothing else. Do not describe what the business offers or doesn't offer.
3. If you are uncertain or the question is outside the SOP, set confidence to "OUT_OF_SCOPE" and escalate.
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

{{
  "answer": "<your response to the customer — this is what they see>",
  "confidence": "<HIGH | LOW | OUT_OF_SCOPE>",
  "escalate": <true | false>,
  "escalation_reason": "<brief reason if escalate is true, else null>",
  "stage": "<faq | qualification | escalation | summary>"
}}
"""

#State
conversation_history = []
lead_profile = {}
escalation_log = []
sop_gaps = []
unanswered_count = 0
qualification_step = 0
session_escalated = False

QUALIFICATION_QUESTIONS = [
    "How many people will be joining you?",
    "What's the occasion — birthday, corporate outing, or just a fun group hangout?",
    "Have any of you done an escape room before, or will this be a first time?"
]

ESCALATION_KEYWORDS = [
    "refund", "complaint", "ridiculous", "terrible", "awful", "angry",
    "frustrated", "unacceptable", "speak to someone", "human", "manager",
    "this is a joke", "waste of money", "disgusting", "horrible", "worst"
]

#Helpers

def detect_escalation_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in ESCALATION_KEYWORDS)


def log_escalation(reason: str):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "conversation_snapshot": conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
    }
    escalation_log.append(entry)
    with open("escalation_log.json", "w") as f:
        json.dump(escalation_log, f, indent=2)


def call_ai(user_message: str) -> dict:
    conversation_history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    time.sleep(0.5)  # gentle rate limiting for Groq

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=600
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if model wraps in ```json
    raw = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if model breaks format
        parsed = {
            "answer": raw,
            "confidence": "LOW",
            "escalate": False,
            "escalation_reason": None,
            "stage": "faq"
        }

    conversation_history.append({"role": "assistant", "content": parsed["answer"]})
    return parsed


def generate_summary() -> str:
    summary_prompt = f"""
The customer conversation has ended. Generate a structured session summary based on the conversation history and data below.

Conversation history:
{json.dumps(conversation_history, indent=2)}

Lead profile collected:
{json.dumps(lead_profile, indent=2)}

SOP gaps (questions AI couldn't answer):
{json.dumps(sop_gaps, indent=2)}

Escalations:
{json.dumps(escalation_log, indent=2)}

Return ONLY valid JSON:
{{
  "customer_intent": "<what the customer was looking for>",
  "lead_profile": {{
    "group_size": "<if collected>",
    "occasion": "<if collected>",
    "experience_level": "<if collected>"
  }},
  "sop_gaps": ["<list of questions the AI could not answer>"],
  "escalated": <true | false>,
  "escalation_reasons": ["<list of reasons if any>"],
  "recommended_next_action": "<what the human agent or business should do next>"
}}
"""

    messages = [
        {"role": "system", "content": "You are a data summarization assistant. Respond only with valid JSON."},
        {"role": "user", "content": summary_prompt}
    ]

    time.sleep(0.5)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=600
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Summary generation failed", "raw": raw}


def handle_qualification_response(user_message: str):
    """Store lead qualification answers based on which question we just asked."""
    global qualification_step
    q_index = qualification_step - 1  # step was already incremented before this call
    if q_index == 0:
        lead_profile["group_size"] = user_message
    elif q_index == 1:
        lead_profile["occasion"] = user_message
    elif q_index == 2:
        lead_profile["experience_level"] = user_message


def print_banner():
    print("\n" + "═" * 60)
    print("  PuzzleVault Experiences — AI Support Agent (Maya)")
    print("  Powered by Closira | Type 'exit' to end the session")
    print("═" * 60 + "\n")


def print_ai(text: str):
    print(f"\n  Maya: {text}\n")


def print_system(text: str):
    print(f"\n  System: [{text}]\n")


def main():
    global unanswered_count, qualification_step, session_escalated

    print_banner()
    print_ai("Hi there! 👋 Welcome to PuzzleVault Experiences. I'm Maya, your virtual assistant. How can I help you today?")

    in_qualification = False
    qualification_done = False

    while True:
        try:
            user_input = input("  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "bye", "done"]:
            print_ai("Thank you for reaching out to PuzzleVault! Let me put together a quick summary of our conversation...")
            summary = generate_summary()
            print("\n" + "═" * 60)
            print("SESSION SUMMARY")
            print("═" * 60)
            print(json.dumps(summary, indent=2))
            print("═" * 60 + "\n")
            break

        # Keyword-based escalation check (Python layer, independent of AI)
        if detect_escalation_keywords(user_input) and not session_escalated:
            reason = "Customer expressed frustration or complaint (keyword detection)"
            log_escalation(reason)
            session_escalated = True
            print_system(f"ESCALATION TRIGGERED — {reason}")
            print_ai(SOP["escalation_rules"]["escalation_message"])
            continue

        #If already escalated, keep routing to human
        if session_escalated:
            print_ai("I've already flagged your case for our team. A PuzzleVault team member will reach out to you within 15 minutes. Is there anything else I can note down for them?")
            continue

        # Handle qualification flow
        if in_qualification and not qualification_done:
            handle_qualification_response(user_input)

            if qualification_step < len(QUALIFICATION_QUESTIONS):
                next_q = QUALIFICATION_QUESTIONS[qualification_step]
                qualification_step += 1
                print_ai(next_q)
                continue
            else:
                qualification_done = True
                in_qualification = False
                print_system("Lead qualification complete")
                print_ai(f"Perfect, thank you! I've noted that down. Now, is there anything else you'd like to know about our rooms or booking process?")
                continue

        result = call_ai(user_input)

        answer = result.get("answer", "")
        confidence = result.get("confidence", "HIGH")
        escalate = result.get("escalate", False)
        escalation_reason = result.get("escalation_reason")

        # Track SOP gaps
        if confidence == "OUT_OF_SCOPE":
            sop_gaps.append(user_input)
            unanswered_count += 1

        # AI-flagged escalation
        if escalate and not session_escalated:
            reason = escalation_reason or "AI flagged low confidence or out-of-scope"
            log_escalation(reason)
            session_escalated = True
            print_system(f"ESCALATION TRIGGERED — {reason}")
            print_ai(SOP["escalation_rules"]["escalation_message"])
            continue

        # Too many unanswered questions
        if unanswered_count >= 2 and not session_escalated:
            reason = "Customer asked 2+ questions outside SOP scope"
            log_escalation(reason)
            session_escalated = True
            print_system(f"ESCALATION TRIGGERED — {reason}")
            print_ai(SOP["escalation_rules"]["escalation_message"])
            continue

        print_ai(answer)

        #Trigger qualification after first successful FAQ response
        if not in_qualification and not qualification_done and confidence == "HIGH" and not escalate:
            in_qualification = True
            qualification_step = 1
            time.sleep(0.3)
            print_ai(f"While I have you here — mind if I ask a couple of quick questions to help find the best experience for your group? {QUALIFICATION_QUESTIONS[0]}")


if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("\n  ⚠️  GROQ_API_KEY not set. Run: export GROQ_API_KEY=your_key_here\n")
    else:
        main()