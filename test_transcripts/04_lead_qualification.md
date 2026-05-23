# Test Transcript 04 — Lead Qualification Flow

**Scenario:** Customer asks an in-SOP question, triggering the qualification flow. AI asks all 3 structured questions sequentially and produces a qualification summary.  
**Expected behaviour:** Questions asked one at a time, all answers stored, lead profile complete in summary.

---

```
════════════════════════════════════════════════════════════
  PuzzleVault Experiences — AI Support Agent (Maya)
  Powered by Closira | Type 'exit' to end the session
════════════════════════════════════════════════════════════

  Maya: Hi there! Welcome to PuzzleVault Experiences. I'm Maya, your
  virtual assistant. How can I help you today?

  You: What is the best room for beginners?

  Maya: The Pharaoh's Curse is our beginner-friendly room and is the
  best starting point for first-timers.

  Maya: While I have you here — mind if I ask a couple of quick questions
  to help find the best experience for your group? How many people will
  be joining you?

  You: 6 people

  Maya: What's the occasion — birthday, corporate outing, or just a fun
  group hangout?

  You: birthday

  Maya: Have any of you done an escape room before, or will this be a
  first time?

  You: yes

  System: [Lead qualification complete]

  Maya: Perfect, thank you! I've noted that down. Now, is there anything
  else you'd like to know about our rooms or booking process?

  You: exit

  Maya: Thank you for reaching out to PuzzleVault! Let me put together
  a quick summary of our conversation...

════════════════════════════════════════════════════════════
  SESSION SUMMARY
════════════════════════════════════════════════════════════
{
  "customer_intent": "book a room for a birthday group of 6 people",
  "lead_profile": {
    "group_size": "6 people",
    "occasion": "birthday",
    "experience_level": "yes"
  },
  "sop_gaps": [],
  "escalated": false,
  "escalation_reasons": [],
  "recommended_next_action": "book a birthday package for the customer in The Pharaoh's Curse room on a date and time of their choice"
}
════════════════════════════════════════════════════════════
```

---

**Result:** ✅ Passed  
**Lead profile collected:** All 3 fields (group size, occasion, experience level)  
**Questions asked one at a time:** Yes — never batched  
**Escalated:** No  
**Hallucination check:** Recommended next action references The Pharaoh's Curse (SOP-defined beginner room) and the birthday package (SOP-defined offering) — no invented actions or bookings.
