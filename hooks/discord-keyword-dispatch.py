#!/usr/bin/env python3
"""
UserPromptSubmit hook: detect bare keyword commands typed in Discord and inject
additionalContext telling Claude to load and run the matching command file.

Only fires for Discord messages (prompt contains a channel tag with
source="plugin:discord:discord"). Terminal sessions exit silently.
"""
import json
import os
import re
import string
import sys

_CHANNEL_TAG_RE = re.compile(
    r'<channel[^>]+source="plugin:discord:discord"[^>]*>'
)

# Map keyword -> (local path relative to cwd, global path under ~/.claude)
KEYWORD_MAP = {
    'batchc':           'commands/batchc.md',
    'load-handoff':     'commands/load-handoff.md',
    'memory-health':    'commands/memory-health.md',
    'mmguns':           'commands/mmguns.md',
    'session-handoff':  'commands/session-handoff.md',
    'become-expert':    'commands/become-expert.md',
    'discussion-starter': 'commands/discussion-starter.md',
}

CLAUDE_DIR = os.path.expanduser('~/.claude')


def resolve_command_path(keyword):
    """Return the first existing path for keyword, checking local then global."""
    rel = KEYWORD_MAP.get(keyword)
    if not rel:
        return None
    local = os.path.join('.claude', rel)
    global_ = os.path.join(CLAUDE_DIR, rel)
    if os.path.exists(local):
        return os.path.abspath(local)
    if os.path.exists(global_):
        return global_
    return None


def extract_body(prompt):
    """Return the user message body from the prompt.

    The discord-prompt-submit hook may have already processed the prompt, but
    we handle both the raw channel-tag form and the plain-text form safely.
    The channel tag wraps the message content; grab text after '>'.
    """
    # Try to extract text inside the channel tag
    m = re.search(r'<channel[^>]*>(.*?)(?:</channel>|$)', prompt, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fall back to raw prompt
    return prompt.strip()


def first_token(text):
    """Return the first whitespace-delimited token, stripped of leading/trailing punctuation."""
    parts = text.split()
    if not parts:
        return ''
    token = parts[0]
    return token.strip(string.punctuation).lower()


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = data.get('prompt', '')

    # Only act on Discord messages
    if not _CHANNEL_TAG_RE.search(prompt):
        sys.exit(0)

    body = extract_body(prompt)
    keyword = first_token(body)

    if not keyword or keyword not in KEYWORD_MAP:
        sys.exit(0)

    path = resolve_command_path(keyword)
    if not path:
        sys.exit(0)

    # Everything after the first token is arguments
    parts = body.split(None, 1)
    args = parts[1].strip() if len(parts) > 1 else ''

    additional_context = (
        f"The user typed '{keyword}' which maps to the custom command at '{path}'. "
        f"Read that file now and execute it as if the user had typed /{keyword}. "
        f"Arguments (text after the keyword): '{args}'"
    )

    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': additional_context,
        }
    }))


if __name__ == '__main__':
    main()
