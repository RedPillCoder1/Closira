# Test Transcript 05 — Full Conversation + Session Summary

**Scenario:** Complete end-to-end session. Customer asks multiple questions — some in SOP, one out of scope. Full qualification collected. Session ends with structured summary.  
**Expected behaviour:** All 4 stages fire correctly. SOP gap logged. Summary includes intent, lead profile, gap, and next action — all grounded in what actually happened.

---

```
════════════════════════════════════════════════════════════
  PuzzleVault Experiences — AI Support Agent (Maya)
  Powered by Closira | Type 'exit' to end the session
════════════════════════════════════════════════════════════

  Maya: Hi there! Welcome to PuzzleVault Experiences. I'm Maya, your
  virtual assistant. How can I help you today?

  You: What are your weekend timings?

  Maya: Our weekend timings are Saturday and Sunday, 10:00 AM to 10:00 PM.

  Maya: While I have you here — mind if I ask a couple of quick questions
  to help find the best experience for your group? How many people will
  be joining you?

  You: 4 people

  Maya: What's the occasion — birthday, corporate outing, or just a fun
  group hangout?

  You: casual outing

  Maya: Have any of you done an escape room before, or will this be a
  first time?

  You: first time for all of us

  System: [Lead qualification complete]

  Maya: Perfect, thank you! I've noted that down. Now, is there anything
  else you'd like to know about our rooms or booking process?

  You: Can we take photos inside the rooms?

  Maya: Photography is not allowed inside the rooms to preserve the
  experience for future players. However, we take a complimentary group
  photo at the end of your session outside the room.

  You: Do you have a party room we can book after the game?

  System: [ESCALATION TRIGGERED — Question cannot be answered from the SOP]

  Maya: I completely understand, and I want to make sure you get the right
  support. Let me connect you with one of our team members who can help
  you directly. Please hold on — someone will reach out to you within
  15 minutes.

  You: exit

  Maya: Thank you for reaching out to PuzzleVault! Let me put together
  a quick summary of our conversation...

════════════════════════════════════════════════════════════
  SESSION SUMMARY
════════════════════════════════════════════════════════════
{
  "customer_intent": "Plan a casual outing for a group of 4 people",
  "lead_profile": {
    "group_size": "4 people",
    "occasion": "casual outing",
    "experience_level": "first time for all of us"
  },
  "sop_gaps": [
    "Do you have a party room we can book after the game?"
  ],
  "escalated": true,
  "escalation_reasons": [
    "Question cannot be answered from the SOP"
  ],
  "recommended_next_action": "Provide information about external party rooms or suggest alternative options for the group to celebrate after the game"
}
════════════════════════════════════════════════════════════
```

---

**Result:** ✅ Passed  
**Stages covered:**
- Stage 1 — FAQ Answering: weekend timings and photography policy answered from SOP ✅
- Stage 2 — Lead Qualification: all 3 fields collected sequentially ✅
- Stage 3 — Escalation Detection: party room question correctly flagged as out-of-scope ✅
- Stage 4 — Conversation Summary: intent, lead profile, SOP gap, and next action all present ✅

**SOP gap identified:** "Do you have a party room we can book after the game?" — flagged for SOP update  
**Hallucination check:** Photography answer matches SOP exactly. Party room question produced no invented answer — escalated immediately. Summary recommended next action is based only on what occurred in the conversation — no invented bookings or refunds.