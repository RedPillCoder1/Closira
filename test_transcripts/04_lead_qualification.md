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

  Maya: The Pharaoh's Curse is our beginner-friendly room and is the best
  starting point for first-timers.

  Maya: While I have you here — mind if I ask a couple of quick questions
  to help find the best experience for your group? How many people will
  be joining you?

  You: we are a group of 6

  Maya: What's the occasion — birthday, corporate outing, or just a fun
  group hangout?

  You: birthday party

  Maya: Have any of you done an escape room before, or will this be a
  first time?

  You: first time

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
  "customer_intent": "best room for beginners",
  "lead_profile": {
    "group_size": "a group of 6",
    "occasion": "birthday party",
    "experience_level": "first time"
  },
  "sop_gaps": [],
  "escalated": false,
  "escalation_reasons": [],
  "recommended_next_action": "Direct the group to The Pharaoh's Curse room for their birthday party"
}
════════════════════════════════════════════════════════════
```

---

**Result:** ✅ Passed  
**Lead profile collected:** All 3 fields (group size, occasion, experience level)  
**Questions asked one at a time:** Yes — never batched  
**Escalated:** No  
**Recommended next action:** Correctly references The Pharaoh's Curse — the SOP-defined beginner room — no invented suggestions.