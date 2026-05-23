# Test Transcript 03 — Escalation Trigger (Angry Customer)

**Scenario:** Customer expresses frustration, makes a complaint, and demands a refund.  
**Expected behaviour:** Python keyword layer detects sentiment before the AI call, logs escalation immediately, hands off to human agent. AI is never invoked for this message.

---

```
════════════════════════════════════════════════════════════
  PuzzleVault Experiences — AI Support Agent (Maya)
  Powered by Closira | Type 'exit' to end the session
════════════════════════════════════════════════════════════

  Maya: Hi there! Welcome to PuzzleVault Experiences. I'm Maya, your
  virtual assistant. How can I help you today?

  You: This is absolutely ridiculous. We booked a room last week and the
  experience was terrible. I want a full refund.

  System: [ESCALATION TRIGGERED — Customer expressed frustration or complaint (keyword detection)]

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
  "customer_intent": null,
  "lead_profile": {},
  "sop_gaps": [],
  "escalated": true,
  "escalation_reasons": [
    "Customer expressed frustration or complaint (keyword detection)"
  ],
  "recommended_next_action": "Review conversation history and escalate to a human agent for further assistance"
}
════════════════════════════════════════════════════════════
```

---

**Result:** ✅ Passed  
**Escalation layer:** Python keyword detection (keywords matched: "ridiculous", "terrible", "refund")  
**Escalated:** Yes — before AI call was made  
**Design note:** The dual-layer escalation system intentionally fires the Python keyword check first. For clear anger or complaint signals, we do not risk the AI attempting to handle something it shouldn't. The AI is bypassed entirely for this message type.