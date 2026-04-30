# Selected Playbooks

Playbooks are persistent lessons extracted from real incidents and patterns — not documentation written in advance, but constraints written after something went wrong or a non-obvious pattern was confirmed. Each file records what happened, why it happened, and how to apply the constraint going forward.

Format: YAML frontmatter (`what`, `why`, `how` keys or equivalent) followed by prose. The frontmatter is designed to be machine-searchable; the prose is the actual lesson.

This is a curated subset of a larger library (~150 entries). Excluded: project-specific playbooks for DroneTeleos, Jarface, personal financial tooling, and BMX sourcing — entries that only make sense with private context.

---

## Start here

Six entries worth reading before anything else — each one covers a failure mode that isn't obvious until you've hit it:

- [`edit_tool_unicode_failures.md`](edit_tool_unicode_failures.md) — The Edit tool silently fails on em dashes and curly quotes; the fix is non-obvious
- [`macos_sed_bash_gotchas.md`](macos_sed_bash_gotchas.md) — BSD sed and GNU sed differ in ways that cause silent failures on Mac
- [`macos_homebrew_python_venv_requirement.md`](macos_homebrew_python_venv_requirement.md) — Homebrew Python 3.14+ blocks system-wide pip with no clear error message
- [`agent_model_selection.md`](agent_model_selection.md) — Which models actually follow system-prompt tool-use sequences reliably
- [`llm_system_prompt_safety_language.md`](llm_system_prompt_safety_language.md) — How to write "warn, don't block" guardrails vs hard refusals
- [`review_sequence_protocol.md`](review_sequence_protocol.md) — Four-role adversarial review: Critic → Gadfly → Architect → CTO

---

## Tier 1 — General

No special system context needed. Applicable to most macOS development environments and Claude Code setups.

### macOS / shell gotchas

- [`macos_sed_bash_gotchas.md`](macos_sed_bash_gotchas.md) — BSD sed vs. GNU sed differences that cause silent failures on Mac
- [`macos_homebrew_python_venv_requirement.md`](macos_homebrew_python_venv_requirement.md) — Homebrew Python 3.14+ venv enforcement and pip behavior
- [`macos_device_path_vs_file.md`](macos_device_path_vs_file.md) — Device path vs. file path distinctions on macOS
- [`macos_fat32_file_permissions.md`](macos_fat32_file_permissions.md) — FAT32 volumes don't preserve Unix permissions; what breaks and why
- [`pillow_exif_jpeg_webp_stripping.md`](pillow_exif_jpeg_webp_stripping.md) — Pillow strips EXIF data on JPEG/WebP save unless explicitly preserved
- [`pandoc_docx_image_extraction.md`](pandoc_docx_image_extraction.md) — How pandoc handles embedded images when converting docx

### Claude Code patterns

- [`edit_tool_unicode_failures.md`](edit_tool_unicode_failures.md) — Edit tool silent failures on em dashes, curly quotes, and other Unicode
- [`skill_invocation_spawn_pattern.md`](skill_invocation_spawn_pattern.md) — How skills should invoke subprocesses and hand off to spawned agents
- [`spec_presearch_codebase_check.md`](spec_presearch_codebase_check.md) — Check the codebase before proposing a spec; avoid re-inventing existing patterns
- [`config_diff_completeness.md`](config_diff_completeness.md) — Why diffs of config files need to show full before/after, not just the delta
- [`batch_skill_model_invocation_constraint.md`](batch_skill_model_invocation_constraint.md) — Constraints on model selection when invoking skills in batch

### AI / system prompt design

- [`llm_system_prompt_safety_language.md`](llm_system_prompt_safety_language.md) — "Warn, don't block" vs. hard refusal language in system prompts
- [`agent_model_selection.md`](agent_model_selection.md) — Model reliability for instruction-following and tool-use sequences
- [`api_key_placement_user_friction.md`](api_key_placement_user_friction.md) — Where API key placement creates user friction and how to reduce it
- [`anthropic_multimodal_content_field.md`](anthropic_multimodal_content_field.md) — How the `content` field works for multimodal inputs in the Anthropic API

### Code quality, review, and testing

- [`review_sequence_protocol.md`](review_sequence_protocol.md) — Four-role adversarial review sequence: Critic, Gadfly, Architect, CTO
- [`hardware_isolation_testing.md`](hardware_isolation_testing.md) — How to isolate hardware dependencies in tests without mocking too aggressively
- [`mock_daemon_virtual_testing.md`](mock_daemon_virtual_testing.md) — Virtual/mock daemon patterns for testing against daemons you don't control
- [`dev_volume_flag_testing_pattern.md`](dev_volume_flag_testing_pattern.md) — Using volume flags in dev environments to test path-sensitive behavior
- [`cli_argument_subparser_completeness.md`](cli_argument_subparser_completeness.md) — CLI subparser argument gaps that produce confusing errors
- [`signal_swallowing_interrupt_handling.md`](signal_swallowing_interrupt_handling.md) — How signal handlers silently swallow interrupts and how to prevent it
- [`serial_delimiter_false_positives.md`](serial_delimiter_false_positives.md) — Delimiter false positives in serial protocol parsing
- [`serial_port_contention.md`](serial_port_contention.md) — Serial port contention and lock behavior across processes
- [`python_global_flags_async.md`](python_global_flags_async.md) — Global flag state bugs in async Python code
- [`python_venv_yaml_parsing.md`](python_venv_yaml_parsing.md) — YAML parsing edge cases in Python venv-isolated environments
- [`cloudflare_workers_kv_namespace.md`](cloudflare_workers_kv_namespace.md) — KV namespace binding gotchas in Cloudflare Workers
- [`cloudflare_workers_user_agent_bypass.md`](cloudflare_workers_user_agent_bypass.md) — User-agent bypass patterns for Cloudflare Workers rate limiting

---

## Tier 2 — Multi-agent systems

Most useful if you're running autonomous agents. Assumes familiarity with orchestration, system prompts, and agent-to-agent delegation.

### Agent behavior and reliability

- [`agent_context_error_injection_gap.md`](agent_context_error_injection_gap.md) — How context errors get injected into agent state without surfacing as failures
- [`agent_first_feature_design.md`](agent_first_feature_design.md) — Designing features for agent-first usage rather than human-first
- [`agent_system_prompt_execution_model.md`](agent_system_prompt_execution_model.md) — How agents actually execute against system prompts vs. how authors assume they do
- [`agent_system_stale_capability_instruction.md`](agent_system_stale_capability_instruction.md) — Stale capability descriptions in system prompts causing silent misbehavior
- [`agent_system_prompt_confirmation_contradiction.md`](agent_system_prompt_confirmation_contradiction.md) — Confirmation and contradiction patterns in multi-section system prompts
- [`agent_third_person_language_removal.md`](agent_third_person_language_removal.md) — Why third-person language in agent identity prompts causes behavioral drift

### Orchestration and research

- [`research_question_triage_cto.md`](research_question_triage_cto.md) — How to triage research questions through a CTO-style prioritization lens

### Infrastructure / ops

- [`launchd_git_backup_cron.md`](launchd_git_backup_cron.md) — launchd cron patterns for git-based backup jobs and their failure modes
- [`public_sync_showcase_durability.md`](public_sync_showcase_durability.md) — Durability constraints for public/private repo sync and showcase patterns

---

## How to use these

Entries are searchable by keyword — filename convention is `{domain}_{topic}.md`. The **Start here** section above covers the highest-value entries for anyone new to this library.

When Claude references a playbook constraint in a response, the source file is the canonical explanation. The frontmatter `why` field is the concise version; the prose is the full incident.

This directory is regenerated nightly by the sync script from the full playbook library.
