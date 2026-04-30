#!/usr/bin/env python3
"""
PostToolUse text extractor for discord-notify.sh
Reads new assistant text blocks from the session JSONL and posts them to Discord.
Called with: session_id transcript_path logs_webhook_url
"""
import json
import os
import re
import subprocess
import sys


_CHANNEL_ID_RE = re.compile(r'\b(\d{17,19})\b')

def load_channels() -> dict:
    path = os.path.expanduser('~/.claude/hooks/discord-channels.json')
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

def substitute_channel_ids(text: str, channels: dict) -> str:
    def replace(m):
        cid = m.group(1)
        return channels.get(cid, cid)
    return _CHANNEL_ID_RE.sub(replace, text)


def main():
    if len(sys.argv) < 4:
        sys.exit(0)

    session_id = sys.argv[1]
    jsonl_path = sys.argv[2]
    logs_url = sys.argv[3]

    if not os.path.exists(jsonl_path):
        sys.exit(0)

    state_dir = os.path.expanduser('~/.claude/hooks/state')
    os.makedirs(state_dir, exist_ok=True)
    state_file = os.path.join(state_dir, f'{session_id}.txt')

    last_line = 0
    if os.path.exists(state_file):
        try:
            last_line = int(open(state_file).read().strip())
        except Exception:
            last_line = 0

    new_texts = []
    current_line = 0
    with open(jsonl_path) as f:
        for i, line in enumerate(f):
            current_line = i + 1
            if i < last_line:
                continue
            try:
                entry = json.loads(line)
                if entry.get('type') == 'assistant':
                    content = entry.get('message', {}).get('content', [])
                    if isinstance(content, list):
                        for block in content:
                            if block.get('type') == 'text':
                                text = block.get('text', '').strip()
                                if text:
                                    new_texts.append(text)
            except Exception:
                pass

    with open(state_file, 'w') as f:
        f.write(str(current_line))

    channels = load_channels()
    for text in new_texts:
        text = substitute_channel_ids(text, channels)
        if len(text) > 400:
            text = text[:397] + '...'
        text = text.replace('`', "'")
        msg = f'> {text}'
        payload = json.dumps({'content': msg})
        subprocess.run(
            ['/usr/bin/curl', '-s', '-o', '/dev/null', '--max-time', '5',
             '-X', 'POST', logs_url,
             '-H', 'Content-Type: application/json',
             '-d', payload],
            check=False
        )


if __name__ == '__main__':
    main()
