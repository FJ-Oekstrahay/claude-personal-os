#!/bin/bash
# Sanitized for public sharing — replace variables in the Config section before use.
#
# sync-to-public.sh
#
# Syncs ~/.claude to a public GitHub repo.
# Personal info is redacted and sensitive directories are excluded.
# Selected playbooks (no personal or customer info) are copied from the workspace
# memory library using an explicit allowlist.
#
# Strategy: maintain a persistent git working dir at
#   $HOME/.openclaw/public-sync/claude-personal-os/
# On each run: pull latest, wipe + re-copy sanitized content, commit, push.
#
# Runs from cron as part of the nightly backup job.

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SOURCE_DIR="$HOME/.claude"
SYNC_DIR="$HOME/.openclaw/public-sync/claude-personal-os"
EXCLUDE_FILE="$HOME/.openclaw/bin/claude-public-exclude.txt"
PLAYBOOKS_SRC="$HOME/.openclaw/workspace/memory/playbooks"
PUBLIC_REMOTE="https://github.com/FJ-Oekstrahay/claude-personal-os.git"
LOG="$HOME/.openclaw/logs/sync-claude-public.log"
ALERT="$HOME/.openclaw/workspace/BACKUP-ALERT.md"

# ---------------------------------------------------------------------------
# Playbook allowlist — explicit list of playbooks with no personal or customer info.
# Add new entries here when a playbook is confirmed clean.
# Do NOT use grep heuristics at sync time; false negatives are silent leaks.
# ---------------------------------------------------------------------------
SELECTED_PLAYBOOKS=(
    agent_context_error_injection_gap.md
    agent_first_feature_design.md
    agent_model_selection.md
    agent_system_prompt_confirmation_contradiction.md
    agent_system_prompt_execution_model.md
    agent_system_stale_capability_instruction.md
    agent_third_person_language_removal.md
    anthropic_multimodal_content_field.md
    api_key_placement_user_friction.md
    batch_skill_model_invocation_constraint.md
    betaflight_adjrange_function_ids.md
    betaflight_arm64_renderer_blank.md
    betaflight_blackbox_pull_modes.md
    betaflight_cli_get_output_parsing.md
    betaflight_cli_gotchas_2025.md
    betaflight_diff_unsaved_changes_limitation.md
    betaflight_dji_msp.md
    betaflight_msc_mode_sd_card.md
    betaflight_msp_error_frame_parser.md
    betaflight_serial_reconnect_timeout.md
    blackbox_multilog_auto_analyze_last.md
    bmx_bike_sourcing.md
    camera_vs_hdmi_capture.md
    cli_argument_subparser_completeness.md
    cloudflare_workers_kv_namespace.md
    cloudflare_workers_user_agent_bypass.md
    config_diff_completeness.md
    dev_volume_flag_testing_pattern.md
    droneteleo_safety_philosophy.md
    dt_agent_byok_tier_routing.md
    dt_agent_fc_detection_pattern.md
    dt_agent_startup_diff_scope.md
    dt_diff_baseline_fallback.md
    edgetx_radio_battery_alert.md
    edit_tool_unicode_failures.md
    eval_harness_api_key_resolution.md
    eval_harness_compression_nocompress.md
    fc_context_key_params_visibility.md
    fc_serial_cdc_sleep_overhead.md
    fft_blackbox_filter_tuning.md
    gadfly_multi_pass_spec_review.md
    gemini_live_model_availability.md
    gemini_live_voice_bot_patterns.md
    hardware_isolation_testing.md
    hid_typing_unicode_handling.md
    jarface_output_filtering_debug_only.md
    jarface_telemetry_event_queue.md
    launchd_git_backup_cron.md
    llm_system_prompt_safety_language.md
    macos_device_path_vs_file.md
    macos_fat32_file_permissions.md
    macos_homebrew_python_venv_requirement.md
    macos_sed_bash_gotchas.md
    mock_daemon_virtual_testing.md
    motor_health_nag_muting_pattern.md
    motor_health_post_flag_outcome_capture.md
    msp_framing_module_locations.md
    nw_builder_arm64_builds.md
    obsidian_dashboard_queries.md
    obsidian_sync_setup.md
    osd_apply_disables_active_items_warning.md
    osd_apply_verification_gap.md
    osd_ascii_preview_fidelity_disclaimer.md
    osd_coordinate_validation.md
    pandoc_docx_image_extraction.md
    pillow_exif_jpeg_webp_stripping.md
    playbook_motor_baseline_schema.md
    playbook_motor_test_safety_mitigations.md
    process_session_flagged_yaml_archival.md
    protocol_mismatch_safety_gate_pattern.md
    python_cli_pi_arm64_porting.md
    python_global_flags_async.md
    python_venv_yaml_parsing.md
    radio_edgetx_config_generation.md
    radiomaster_boxer_mount_detection.md
    radiomaster_pocket_mount_detection.md
    research_question_triage_cto.md
    review_sequence_protocol.md
    serial_delimiter_false_positives.md
    serial_port_contention.md
    signal_swallowing_interrupt_handling.md
    skill_invocation_spawn_pattern.md
    spec_presearch_codebase_check.md
    usb_composite_gadget_config.md
    usb_hid_gadget_mode.md
)

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
}

fail() {
    local msg="$*"
    log "ERROR: $msg"
    {
        echo ""
        echo "## sync-claude-to-public failure — $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "**Error:** $msg"
        echo ""
    } >> "$ALERT"
    exit 1
}

# ---------------------------------------------------------------------------
# Trap: log any unexpected exit
# ---------------------------------------------------------------------------
trap 'status=$?; [ $status -ne 0 ] && fail "Script exited unexpectedly (exit $status)"' EXIT

log "Starting sync-claude-to-public"

# ---------------------------------------------------------------------------
# 1. Ensure the persistent sync directory exists and is a valid git repo
# ---------------------------------------------------------------------------
if [ ! -d "$SYNC_DIR/.git" ]; then
    log "No existing clone found — cloning public repo"
    mkdir -p "$(dirname "$SYNC_DIR")"
    git clone "$PUBLIC_REMOTE" "$SYNC_DIR" >> "$LOG" 2>&1 || fail "git clone failed"
else
    git -C "$SYNC_DIR" remote set-url origin "$PUBLIC_REMOTE" 2>/dev/null || true
    log "Pulling latest from origin"
    git -C "$SYNC_DIR" pull --rebase origin main >> "$LOG" 2>&1 || {
        log "Pull failed (empty repo or diverged) — resetting to current remote state"
        git -C "$SYNC_DIR" fetch origin >> "$LOG" 2>&1 || true
        git -C "$SYNC_DIR" reset --hard origin/main >> "$LOG" 2>&1 || true
    }
fi

# ---------------------------------------------------------------------------
# 2. Wipe all tracked content from the working dir (keep .git)
# ---------------------------------------------------------------------------
log "Wiping working directory content"
find "$SYNC_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

# ---------------------------------------------------------------------------
# 3. rsync sanitized content from ~/.claude
# ---------------------------------------------------------------------------
log "rsync from $SOURCE_DIR"
rsync -a \
    --exclude-from="$EXCLUDE_FILE" \
    "$SOURCE_DIR/" "$SYNC_DIR/" >> "$LOG" 2>&1 || fail "rsync failed"

# ---------------------------------------------------------------------------
# 4. Use public-facing CLAUDE.md
# ---------------------------------------------------------------------------
if [ -f "$SOURCE_DIR/CLAUDE.public.md" ]; then
    log "Using CLAUDE.public.md as public CLAUDE.md"
    cp "$SOURCE_DIR/CLAUDE.public.md" "$SYNC_DIR/CLAUDE.md"
elif [ -f "$SYNC_DIR/CLAUDE.md" ]; then
    log "CLAUDE.public.md not found — redacting internal CLAUDE.md"
    sed -i '' \
        -e 's/your\.real\.email@example\.com/your@email.com/g' \
        -e 's/Real Name/FJ Oekstrahay/g' \
        "$SYNC_DIR/CLAUDE.md" || fail "CLAUDE.md redaction failed"
fi

# ---------------------------------------------------------------------------
# 5a. Global redaction pass — all .md files
# ---------------------------------------------------------------------------
log "Redacting personal info from all .md files"
while IFS= read -r -d '' f; do
    sed -i '' \
        -e 's/your\.real\.email@example\.com/your@email.com/g' \
        -e 's/Real Name/FJ Oekstrahay/g' \
        -e 's/18789/<gateway-port>/g' \
        "$f" 2>/dev/null || true
done < <(find "$SYNC_DIR" -name "*.md" -print0)

# ---------------------------------------------------------------------------
# 5b. Redact settings.json
# ---------------------------------------------------------------------------
if [ -f "$SYNC_DIR/settings.json" ]; then
    log "Redacting settings.json"
    sed -i '' \
        -e 's/your\.real\.email@example\.com/your@email.com/g' \
        -e 's/Real Name/FJ Oekstrahay/g' \
        "$SYNC_DIR/settings.json" || fail "settings.json redaction (names) failed"

    sed -i '' \
        -E 's/("(token|key|password|secret)[^"]*"[[:space:]]*:[[:space:]]*)"[^"]*"/\1"<redacted>"/gI' \
        "$SYNC_DIR/settings.json" || fail "settings.json redaction (secrets) failed"
fi

# ---------------------------------------------------------------------------
# 5c. Copy selected playbooks
# Explicit allowlist only — no heuristics. New playbooks must be reviewed and
# added to SELECTED_PLAYBOOKS above before they appear in the public repo.
# ---------------------------------------------------------------------------
if [ -d "$PLAYBOOKS_SRC" ]; then
    log "Copying ${#SELECTED_PLAYBOOKS[@]} selected playbooks"
    PLAYBOOKS_DEST="$SYNC_DIR/selected-playbooks"
    mkdir -p "$PLAYBOOKS_DEST"

    for fname in "${SELECTED_PLAYBOOKS[@]}"; do
        src="$PLAYBOOKS_SRC/$fname"
        if [ -f "$src" ]; then
            cp "$src" "$PLAYBOOKS_DEST/$fname"
        else
            log "WARNING: listed playbook not found: $fname"
        fi
    done
else
    log "WARNING: playbooks source directory not found: $PLAYBOOKS_SRC"
fi

# ---------------------------------------------------------------------------
# 6. Commit and push if there are changes
# ---------------------------------------------------------------------------
git -C "$SYNC_DIR" add -A

if git -C "$SYNC_DIR" diff --cached --quiet; then
    log "No changes to commit — public repo is already up to date"
    trap - EXIT
    exit 0
fi

COMMIT_MSG="sync: $(date '+%Y-%m-%d')"
log "Committing: $COMMIT_MSG"
git -C "$SYNC_DIR" commit -m "$COMMIT_MSG" >> "$LOG" 2>&1 || fail "git commit failed"

log "Pushing to origin main"
git -C "$SYNC_DIR" push --force origin main >> "$LOG" 2>&1 || fail "git push failed"

log "Done — sync complete"

trap - EXIT
