the user (or a review pass) just corrected something a model produced. Preserve the before→after pair for the distillation pipeline.

## Steps

1. **Identify the correction.** Use the most recent fix in this session where model-produced output was wrong and got corrected (by the user, by a review agent, or by you). If more than one candidate exists, ask the user which one. If the "before" is no longer in context, ask the user to paste or describe it — do not reconstruct it from imagination.
2. **Write the pair file** to `~/.openclaw/workspace/projects/claude-config/distillation/pairs/YYYY-MM-DD-<short-slug>.md` using exactly this schema:

   ---
   date: YYYY-MM-DD
   model: <model that produced the BEFORE, e.g. opus-4.8 / sonnet-5 / haiku-4.5>
   trigger: <manual | review-sequence | critic | correction>
   project: <dir where it happened, e.g. financial>
   files: [<paths touched, repo-relative>]
   distilled: false
   ---
   # <one-line title of the failure>

   ## Context
   <2–4 lines: what was asked, what constraints applied>

   ## Before
   <the wrong output — code snippet or description. NEVER include secret values; file:line + short prefix only>

   ## What was wrong
   <1–3 lines: the actual defect, not a paraphrase of the diff>

   ## After
   <the corrected version, or a pointer to the commit/file that holds it>

   ## Rule candidate
   WHEN <concrete trigger> DO <concrete action>   ← one flat sentence a weak model can apply literally

3. **Register it:** append one line to `distillation/pairs/INDEX.md`: `- [<title>](YYYY-MM-DD-<slug>.md) — <rule candidate, abbreviated>`.
4. **Commit** in claude-config, scoped to the two files (standing commit order applies; do not push).
5. **Reply** with the file path and the rule-candidate line, nothing else.
