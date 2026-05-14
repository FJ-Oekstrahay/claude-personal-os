#!/usr/bin/env python3
"""
Stop hook: post any unlogged assistant text to the source Discord channel.

Two jobs:
1. Flush text produced *after the last tool call* — the text extractor only
   fires on PreToolUse/PostToolUse, so final-turn text (e.g. "context safe to
   clear") is never flushed otherwise. Uses the text-extractor state file to
   avoid double-posting.
2. Safety-net: if Claude never used the reply tool this turn, post last text.

Called with: session_id transcript_path
Reads DISCORD_BOT_TOKEN from discord-webhook.conf; falls back to openclaw.json.
"""
import json
import os
import re
import subprocess
import sys

CONF_PATH = os.path.expanduser('~/.claude/hooks/discord-webhook.conf')
CHANNEL_TAG_RE = re.compile(r'<channel[^>]+source="plugin:discord:discord"[^>]+chat_id="(\d+)"')

QUESTION_PHRASES = ('which', 'would you like', 'do you want', 'should i', 'can you')

# Matches: "Model set to sonnet46 (anthropic/claude-sonnet-4-6)."
#          "Model reset to default (sonnet46 (anthropic/claude-sonnet-4-6))."
# Captures the full provider/model ID from the innermost parentheses.
MODEL_SWITCH_RE = re.compile(r'Model (?:set to|reset to default)\b.*?\(([a-zA-Z0-9_][a-zA-Z0-9_./-]*)\)\.')


def load_conf():
    bot_token = ''
    alert_user_id = ''
    try:
        with open(CONF_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if line.startswith('DISCORD_BOT_TOKEN='):
                    bot_token = line.partition('=')[2].strip().strip('"').strip("'")
                elif line.startswith('DISCORD_ALERT_USER_ID='):
                    alert_user_id = line.partition('=')[2].strip().strip('"').strip("'")
    except Exception:
        pass
    if not bot_token:
        # Fallback: read from the canonical plugin env file
        try:
            plugin_env = os.path.expanduser('~/.claude/channels/discord/.env')
            with open(plugin_env) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('DISCORD_BOT_TOKEN='):
                        bot_token = line.partition('=')[2].strip()
                        break
        except Exception:
            pass
    return bot_token, alert_user_id


def get_user_content_str(entry):
    content = entry.get('message', {}).get('content', '')
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict) and b.get('type') == 'text':
                parts.append(b.get('text', ''))
        return '\n'.join(parts)
    return ''


def is_question(text):
    lower = text.lower()
    if lower.rstrip().endswith('?'):
        return True
    return any(phrase in lower for phrase in QUESTION_PHRASES)


def _resolve_log_channel(session_id):
    """Return the log channel ID for this session using per-session state files."""
    log_channels_path = os.path.expanduser('~/.claude/hooks/discord-log-channels.json')
    try:
        mapping = json.load(open(log_channels_path))
    except Exception:
        return ''
    state_dir = os.path.expanduser('~/.claude/hooks/state')
    for suffix in ('routechatid', 'chatid'):
        try:
            chat_id = open(os.path.join(state_dir, f'{session_id}.{suffix}')).read().strip()
            if chat_id and chat_id in mapping:
                return mapping[chat_id]
        except Exception:
            pass
    return ''


def main():
    if len(sys.argv) < 3:
        sys.exit(0)

    session_id = sys.argv[1]
    jsonl_path = sys.argv[2]

    bot_token, alert_user_id = load_conf()
    if not bot_token:
        sys.exit(0)

    if not os.path.exists(jsonl_path):
        sys.exit(0)

    entries = []
    with open(jsonl_path) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass

    # Find the last Discord user message and its index
    last_discord_chat_id = None
    last_discord_idx = -1
    for i, entry in enumerate(entries):
        if entry.get('type') == 'user':
            text = get_user_content_str(entry)
            m = CHANNEL_TAG_RE.search(text)
            if m:
                last_discord_chat_id = m.group(1)
                last_discord_idx = i

    if not last_discord_chat_id or last_discord_idx < 0:
        sys.exit(0)

    # --- Model switch detection: update state file if model changed this turn ---
    # UserPromptSubmit reads this file to label non-default models. Writing it here
    # (after the turn completes) means the next turn sees the correct model with no lag.
    state_dir = os.path.expanduser('~/.claude/hooks/state')
    model_state_file = os.path.join(state_dir, f'{session_id}.model')
    for entry in entries[last_discord_idx:]:
        if entry.get('type') != 'assistant':
            continue
        content = entry.get('message', {}).get('content', [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get('type') != 'text':
                continue
            m = MODEL_SWITCH_RE.search(block.get('text', ''))
            if m:
                new_model = m.group(1)
                try:
                    os.makedirs(state_dir, exist_ok=True)
                    with open(model_state_file, 'w') as f:
                        f.write(new_model)
                except Exception:
                    pass

    # --- Job 1: flush unposted text since last text-extractor run ---
    # The text extractor (PreToolUse/PostToolUse) writes a state file tracking
    # the last JSONL line it processed. Any assistant text after that line is
    # "final-turn" text that was never flushed to Discord.
    state_dir = os.path.expanduser('~/.claude/hooks/state')
    state_file = os.path.join(state_dir, f'{session_id}.txt')
    last_processed_line = 0
    if os.path.exists(state_file):
        try:
            last_processed_line = int(open(state_file).read().strip())
        except Exception:
            pass

    unposted = []
    for i, entry in enumerate(entries):
        if i < last_processed_line:
            continue
        if entry.get('type') != 'assistant':
            continue
        content = entry.get('message', {}).get('content', [])
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                t = block.get('text', '').strip()
                if t:
                    unposted.append(t)

    if unposted:
        for text in unposted:
            if len(text) > 1900:
                text = text[:1897] + '...'
            payload = json.dumps({'content': text})
            subprocess.run(
                ['/usr/bin/curl', '-s', '-o', '/dev/null', '--max-time', '10',
                 '-X', 'POST', f'https://discord.com/api/v10/channels/{last_discord_chat_id}/messages',
                 '-H', f'Authorization: Bot {bot_token}',
                 '-H', 'Content-Type: application/json',
                 '-d', payload],
                check=False
            )
        try:
            with open(state_file, 'w') as f:
                f.write(str(len(entries)))
        except Exception:
            pass
        sys.exit(0)

    # --- Job 2: safety-net when Claude never used the reply tool this turn ---
    replied = False
    last_text = ''
    for entry in entries[last_discord_idx + 1:]:
        if entry.get('type') != 'assistant':
            continue
        content = entry.get('message', {}).get('content', [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use' and block.get('name') == 'mcp__plugin_discord_discord__reply':
                replied = True
            if block.get('type') == 'text':
                t = block.get('text', '').strip()
                if t:
                    last_text = t

    if replied:
        # Wait briefly for any in-flight background webhook posts (text extractor) to land
        # before sending the "done" ping — prevents ordering inversion in Discord.
        import time
        time.sleep(1.5)
        # Resolve the log channel: prefer per-session routing over the global env fallback.
        # Priority: session routechatid → session chatid → DISCORD_LOG_CHANNEL_ID env var.
        ping_channel = _resolve_log_channel(session_id) or os.environ.get('DISCORD_LOG_CHANNEL_ID', '') or last_discord_chat_id
        if alert_user_id and ping_channel:
            payload_dict = {
                'content': f'<@{alert_user_id}> done — waiting for your next message.',
                'allowed_mentions': {'users': [alert_user_id]},
            }
            subprocess.run(
                ['/usr/bin/curl', '-s', '-o', '/dev/null', '--max-time', '10',
                 '-X', 'POST',
                 f'https://discord.com/api/v10/channels/{ping_channel}/messages',
                 '-H', f'Authorization: Bot {bot_token}',
                 '-H', 'Content-Type: application/json',
                 '-d', json.dumps(payload_dict)],
                check=False
            )
        sys.exit(0)

    if not last_text:
        sys.exit(0)

    if len(last_text) > 1850:
        last_text = last_text[:1847] + '...'

    mention_prefix = ''
    if alert_user_id and is_question(last_text):
        mention_prefix = f'<@{alert_user_id}> '

    message_content = f'{mention_prefix}**[turn done]** {last_text}'

    payload_dict = {'content': message_content}
    if mention_prefix and alert_user_id:
        payload_dict['allowed_mentions'] = {'users': [alert_user_id]}

    payload = json.dumps(payload_dict)
    subprocess.run(
        ['/usr/bin/curl', '-s', '-o', '/dev/null', '--max-time', '10',
         '-X', 'POST', f'https://discord.com/api/v10/channels/{last_discord_chat_id}/messages',
         '-H', f'Authorization: Bot {bot_token}',
         '-H', 'Content-Type: application/json',
         '-d', payload],
        check=False
    )


if __name__ == '__main__':
    main()
