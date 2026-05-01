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

    if replied or not last_text:
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
