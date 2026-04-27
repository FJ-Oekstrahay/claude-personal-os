# Selected Playbooks

A representative subset of the full playbook library (~150 entries). Each file follows the format: what happened, why, how to apply. No personal or system-specific context.

Playbooks are populated by `sync-to-public.sh` from an explicit allowlist. This directory is empty until the sync runs.

## Index

| Playbook | Topic |
|---|---|
| `agent_context_error_injection_gap` | Tool errors injected into agent context can silently corrupt downstream reasoning |
| `agent_first_feature_design` | How to scope the first feature for a new agent without over-building |
| `agent_model_selection` | Worker agents require Haiku minimum; GPT-4.1-mini cannot reliably follow system-prompt tool-use sequences |
| `agent_system_prompt_confirmation_contradiction` | Agents hallucinate confirmation when a system prompt instruction conflicts with a user-turn imperative |
| `agent_system_prompt_execution_model` | Agents that can execute code must have an explicit "how execution works" section or they claim inability |
| `agent_system_stale_capability_instruction` | System prompt capability claims go stale when tools are added or removed — keep them current |
| `agent_third_person_language_removal` | Third-person self-references in agent system prompts ("The assistant will...") produce stilted behavior |
| `anthropic_multimodal_content_field` | Anthropic API multimodal messages require a `content` array, not a string, when images are included |
| `api_key_placement_user_friction` | Where you ask for an API key in onboarding has a large effect on drop-off rate |
| `batch_skill_model_invocation_constraint` | `/batchc` throttle rules, wave sizing, and how to avoid rapid re-dispatch |
| `betaflight_adjrange_function_ids` | Betaflight `adjrange` function IDs are not stable across firmware versions |
| `betaflight_arm64_renderer_blank` | Betaflight Configurator blank screen on Apple Silicon — GPU renderer workaround |
| `betaflight_blackbox_pull_modes` | Blackbox data pull via USB vs. SD card — when each works and when it silently fails |
| `betaflight_cli_get_output_parsing` | Parsing `get` output from the Betaflight CLI — field format quirks and edge cases |
| `betaflight_cli_gotchas_2025` | Accumulated Betaflight CLI gotchas: command ordering, save timing, echo behavior |
| `betaflight_diff_unsaved_changes_limitation` | `diff` in Betaflight CLI does not show unsaved in-memory changes — must `save` first |
| `betaflight_dji_msp` | DJI MSP configuration quirks for Betaflight — OSD and telemetry framing |
| `betaflight_msc_mode_sd_card` | MSC mode for SD card access requires specific Betaflight build and timing |
| `betaflight_msp_error_frame_parser` | MSP error frame parsing — distinguishing error responses from data corruption |
| `betaflight_serial_reconnect_timeout` | Serial reconnect after Betaflight reset requires a delay — 200ms is not always enough |
| `blackbox_multilog_auto_analyze_last` | Auto-analyzing the last log in a multi-log blackbox file — offset calculation |
| `bmx_bike_sourcing` | BMX bike sourcing notes — geometry, size, and age considerations |
| `camera_vs_hdmi_capture` | When to use a camera directly vs. HDMI capture card for video input |
| `cli_argument_subparser_completeness` | CLI subparsers silently drop arguments if not explicitly forwarded — verify completeness |
| `cloudflare_workers_kv_namespace` | Cloudflare Workers KV namespace binding setup and gotchas |
| `cloudflare_workers_user_agent_bypass` | Cloudflare bot protection and user-agent bypass patterns for Workers fetch |
| `config_diff_completeness` | Config diffs must include all changed sections — partial diffs cause silent regressions |
| `dev_volume_flag_testing_pattern` | Testing volume/threshold flags in dev — how to wire a fast feedback loop |
| `droneteleo_safety_philosophy` | DroneTeleo safety design principles — motor test guards, failsafes, user confirmation |
| `dt_agent_byok_tier_routing` | BYOK tier routing for DroneTeleo agent — how model selection works per API key |
| `dt_agent_fc_detection_pattern` | Flight controller detection pattern used by the DroneTeleo agent |
| `dt_agent_startup_diff_scope` | DroneTeleo agent startup diff scope — what gets compared and why |
| `dt_diff_baseline_fallback` | Diff baseline fallback behavior when no prior snapshot exists |
| `edgetx_radio_battery_alert` | EdgeTX battery alert configuration — threshold, sound, and timing |
| `edit_tool_unicode_failures` | The Edit tool fails silently on Unicode characters (em dashes, curly quotes) — use Python str.replace() via Bash |
| `eval_harness_api_key_resolution` | Eval harness API key resolution order — env var vs. config file vs. BYOK |
| `eval_harness_compression_nocompress` | Eval harness compression flag behavior — `--nocompress` side effects |
| `fc_context_key_params_visibility` | Flight controller context key parameters — what the agent can and cannot see |
| `fc_serial_cdc_sleep_overhead` | USB CDC serial sleep overhead on flight controllers — timing implications |
| `fft_blackbox_filter_tuning` | FFT-based filter tuning from Betaflight blackbox — workflow and interpretation |
| `gadfly_multi_pass_spec_review` | Specs with new user-facing commands often need two Gadfly rounds — first finds structure issues, second finds surface-area gaps |
| `gemini_live_model_availability` | Gemini Live model availability and regional restrictions |
| `gemini_live_voice_bot_patterns` | Patterns for building voice bots with Gemini Live — session management and audio framing |
| `hardware_isolation_testing` | Isolating hardware variables in embedded testing — one change at a time |
| `hid_typing_unicode_handling` | USB HID typing of Unicode characters — OS-level keysym vs. raw HID report |
| `jarface_output_filtering_debug_only` | Jarface output filtering should be debug-only — do not ship filtered output to users |
| `jarface_telemetry_event_queue` | Jarface telemetry event queue — flush timing and drop behavior under load |
| `launchd_git_backup_cron` | Setting up a launchd git backup cron — env var requirements and silent failure modes |
| `llm_system_prompt_safety_language` | How to write warn-not-block safety guardrails in system prompts — hard refusal vs. proposed guidance |
| `macos_device_path_vs_file` | macOS device paths (`/dev/disk*`) vs. file paths — when each is needed for disk operations |
| `macos_fat32_file_permissions` | FAT32 volumes on macOS do not preserve Unix permissions — don't rely on chmod |
| `macos_homebrew_python_venv_requirement` | Homebrew Python requires venv for pip installs — system-wide installs are blocked |
| `macos_sed_bash_gotchas` | macOS BSD sed gotchas — `-i ''` syntax, ERE flags, and differences from GNU sed |
| `mock_daemon_virtual_testing` | Pattern for testing daemon behavior with a mock virtual device |
| `motor_health_nag_muting_pattern` | Pattern for muting motor health nag messages after user acknowledgment |
| `motor_health_post_flag_outcome_capture` | Capturing motor health post-flag outcomes — what to log after the user acts |
| `msp_framing_module_locations` | MSP framing module locations across Betaflight firmware versions |
| `nw_builder_arm64_builds` | NW.js builder arm64 build gotchas — native module compatibility |
| `obsidian_dashboard_queries` | Obsidian Dataview dashboard query patterns — task and backlink aggregation |
| `obsidian_sync_setup` | Obsidian Sync setup — vault conflicts and initial merge behavior |
| `osd_apply_disables_active_items_warning` | OSD apply in Betaflight disables active items that are not in the current profile |
| `osd_apply_verification_gap` | OSD apply verification gap — confirming apply success requires re-reading OSD state |
| `osd_ascii_preview_fidelity_disclaimer` | ASCII OSD preview fidelity limits — what it can and cannot represent |
| `osd_coordinate_validation` | OSD coordinate validation — out-of-range coordinates fail silently |
| `pandoc_docx_image_extraction` | Extracting images from .docx files with pandoc — media directory behavior |
| `pillow_exif_jpeg_webp_stripping` | Stripping EXIF data from JPEG and WebP files with Pillow — format-specific behavior |
| `playbook_motor_baseline_schema` | Motor baseline schema design — fields, versioning, and comparison logic |
| `playbook_motor_test_safety_mitigations` | Motor test safety mitigations — guard conditions, abort triggers, and user confirmation |
| `process_session_flagged_yaml_archival` | Archiving flagged YAML session files — naming convention and retention policy |
| `protocol_mismatch_safety_gate_pattern` | Safety gate pattern for protocol mismatch detection — fail closed, require explicit override |
| `python_cli_pi_arm64_porting` | Porting a Python CLI to Raspberry Pi arm64 — native module and venv considerations |
| `python_global_flags_async` | Python global flags in async contexts — argparse and click interaction |
| `python_venv_yaml_parsing` | Python venv yaml parsing issues — PyYAML vs. ruamel.yaml in isolated envs |
| `radio_edgetx_config_generation` | EdgeTX radio config generation — model file structure and field ordering |
| `radiomaster_boxer_mount_detection` | Radiomaster Boxer mount detection — USB path and HID report structure |
| `radiomaster_pocket_mount_detection` | Radiomaster Pocket mount detection — distinguishing from Boxer via USB descriptors |
| `research_question_triage_cto` | Bouncing research questions off a CTO agent before dispatching a researcher sharpens scope and avoids out-of-scope work |
| `review_sequence_protocol` | Four-role adversarial review protocol — Critic, Gadfly, Architect, CTO — with sequencing rules |
| `serial_delimiter_false_positives` | Serial framing delimiter false positives — escaping vs. length-prefixing tradeoffs |
| `serial_port_contention` | Serial port contention between two processes — detection and resolution |
| `signal_swallowing_interrupt_handling` | Signal swallowing in interrupt handlers — when SIGINT is caught but not re-raised |
| `skill_invocation_spawn_pattern` | Skill output vs. auto-spawn behavior — manual Agent tool invocation required for spawning |
| `spec_presearch_codebase_check` | Verify module existence before writing a spec for a new CLI feature — catch duplicated implementations |
| `usb_composite_gadget_config` | USB composite gadget configuration on Linux — interface ordering and descriptor conflicts |
| `usb_hid_gadget_mode` | USB HID gadget mode setup — configfs paths, endpoint sizing, and kernel module loading |
