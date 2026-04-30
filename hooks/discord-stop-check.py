#!/usr/bin/env python3
"""
Stop hook: if the last turn had an incoming Discord message but no reply was sent,
post the assistant's text to that Discord channel via the bot API.

Called with: session_id transcript_path
Reads DISCORD_BOT_TOKEN from discord-webhook.conf.
"""
import json
import os
import re
import subprocess
import sys

CONF_PATH = os.path.expanduser('~/.claude/hooks/discord-webhook.conf')
CHANNEL_TAG_RE = re.compile(r'<channel[^>]+source="plugin:discord:discord"[^>]+chat_id="(\d+)"')


def load_bot_token():
    try:
        with open(CONF_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith('DISCORD_BOT_TOKEN=') and not line.startswith('#'):
                    return line.partition('=')[2].strip().strip('"').strip("'")
    except Exception:
        pass
    return ''


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


def main():
    if len(sys.argv) < 3:
        sys.exit(0)

    session_id = sys.argv[1]
    jsonl_path = sys.argv[2]

    bot_token = load_bot_token()
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

    # Scan assistant entries after the last Discord user message
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

    if len(last_text) > 1900:
        last_text = last_text[:1897] + '...'

    payload = json.dumps({'content': last_text})
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
