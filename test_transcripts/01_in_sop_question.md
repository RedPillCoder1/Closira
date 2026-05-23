# Test Transcript 01 — In-SOP Question

**Scenario:** Customer asks what rooms are available — a question directly covered by the SOP.  
**Expected behaviour:** AI answers accurately from SOP only, with HIGH confidence. No escalation.

---

```
════════════════════════════════════════════════════════════
  PuzzleVault Experiences — AI Support Agent (Maya)
  Powered by Closira | Type 'exit' to end the session
════════════════════════════════════════════════════════════

  Maya: Hi there! Welcome to PuzzleVault Experiences. I'm Maya, your
  virtual assistant. How can I help you today?

  You: What rooms do you have available?

  Maya: We have four immersive escape rooms available: The Pharaoh's Curse,
  Operation Blackout, The Last Signal, and Heist at the Grand. Each room
  offers a unique theme and experience. Would you like to know more about
  a specific room or their details?

  Maya: While I have you here — mind if I ask a couple of quick questions
  to help find the best experience for your group? How many people will
  be joining you?

  You: we are a group of 6 people

  Maya: What's the occasion — birthday, corporate outing, or just a fun
  group hangout?

  You: fun group hangout

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
  "customer_intent": "book an escape room",
  "lead_profile": {
    "group_size": "6 people",
    "occasion": "fun group hangout",
    "experience_level": "first time"
  },
  "sop_gaps": [],
  "escalated": false,
  "escalation_reasons": [],
  "recommended_next_action": "Provide more details about the available escape rooms and assist with booking"
}
════════════════════════════════════════════════════════════
```

---

**Result:** ✅ Passed  
**Confidence:** HIGH  
**Escalated:** No  
**SOP gaps:** None  
**Hallucination check:** All four room names match SOP exactly. No invented details.