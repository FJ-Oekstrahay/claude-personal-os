# EXPLORE-LATER — Un-AI prose tone-pass pipeline

**Status:** not started. Triggered by Anita-deck feedback 2026-06-30 (item 3.1.3).
**Model to run with:** Opus for the design; the pass itself is a candidate for GLM 5.2 as a divergent lens.

## The goal
Establish a repeatable **final pass** that takes drafted prose (Sonnet-written
slides/docs) and removes the "AI tells" before it reaches a human reader —
especially Anita, who is acutely sensitive to anything that reads as an AI
talking to her (she won't even use Siri). See [[anita]] persona.

The pass should strip / rewrite:
- Conversational AI tics: "to be honest," "let's be real," "I'm here to help,"
  "great question," "I understand how you feel," "we should do this together."
- Second-person emotional mind-reading.
- Hedging filler, over-explanation, and the cheerful-assistant register.
- Em-dash overuse, tricolon overuse, and other LLM stylistic fingerprints.
Output should read like a competent human professional wrote it (here: like the user,
prepared with analysis), not like a chatbot.

## Investigate first (don't do this yet)
the user believes a similar pipeline may already exist in one of:
- `~/.openclaw/public-sync/`
- `~/.openclaw/workspace/projects/git-public-repo/`
Check whether the public-repo README/landing-page sync flow already has an
"un-AI the prose" or tone-normalization step we can reuse or adapt, rather than
building from scratch. (the user said explicitly: do not go looking yet — this note
is the trigger to look when we pick this up.)

## Deliverable
Either: a reusable skill/prompt ("tone-pass") that any project can invoke as the
last step before a human-facing doc ships, OR a documented manual checklist if a
skill is overkill. Decide based on what the public-sync investigation turns up.

## Run order
After the Anita deck + anita-discussion doc are content-correct and the user has done
his own Opus/GLM tone pass once manually — that manual pass is the spec for what
to automate.
