# Test Transcript 02 — Out-of-Scope Question

**Scenario:** Customer asks about VR experience rooms — not mentioned anywhere in the SOP.  
**Expected behaviour:** AI does not guess or deny. Flags as OUT_OF_SCOPE, escalates immediately, logs SOP gap.

---

```
════════════════════════════════════════════════════════════
  PuzzleVault Experiences — AI Support Agent (Maya)
  Powered by Closira | Type 'exit' to end the session
════════════════════════════════════════════════════════════

  Maya: Hi there! Welcome to PuzzleVault Experiences. I'm Maya, your
  virtual assistant. How can I help you today?

  You: Do you offer any VR experience rooms?

  System: [ESCALATION TRIGGERED — AI flagged low confidence or out-of-scope]

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
  "customer_intent": "Get information about VR experience rooms",
  "lead_profile": {},
  "sop_gaps": [
    "Do you offer any VR experience rooms?"
  ],
  "escalated": true,
  "escalation_reasons": [
    "AI flagged low confidence or out-of-scope"
  ],
  "recommended_next_action": "Provide the customer with the information about VR experience rooms or escalate to a human agent who can assist further"
}
════════════════════════════════════════════════════════════
```

---

**Result:** ✅ Passed  
**Confidence:** OUT_OF_SCOPE  
**Escalated:** Yes — immediately, before any fabricated answer  
**SOP gap logged:** "Do you offer any VR experience rooms?"  
**Hallucination check:** AI did not deny or confirm VR offerings. No invented information. Handed off cleanly.