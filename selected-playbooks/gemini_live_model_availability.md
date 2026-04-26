---
name: Gemini Live Model Availability
description: Only one live model is currently available; ngrok free tier audio quality issues
type: reference
---

# Gemini Live Model Availability

## Available models
As of 2026-04-05, only **gemini-3.1-flash-live-preview** is available for real-time voice interactions (Pipecat, live streaming).

Do not attempt to use `gemini-2.0-flash-live` or other variations — they will fail during model initialization.

## Audio quality
The prior auth bot uses ngrok free tier by default. This causes:
- **Syllable dropouts**: words like "prauthorization" become "prauth_rization" (packet loss)
- **Solution**: Use Cloudflare Tunnel as a drop-in replacement:
  ```bash
  cloudflared tunnel --url http://localhost:8765
  ```
  Better latency and fewer packet loss issues than ngrok free.

## Integration with Pipecat
The bot (Pipecat + Gemini Live) feeds bot audio and user audio through the same model. If audio quality is poor, the model struggles with comprehension — syllable loss is not just cosmetic, it breaks insurance IVR navigation.

Test with a real call to a UnitedHealthcare number (not simulated) to detect audio issues early.

## Related
- Prior auth bot: `/Users/moltyjoe/.openclaw/workspace/memory/playbooks/prior_auth_test_call.md`
- Twilio webhook: `/Users/moltyjoe/.openclaw/workspace/memory/playbooks/twilio_webhook_signature_validation.md`
