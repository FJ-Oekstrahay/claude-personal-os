#!/usr/bin/env python3
"""
UserPromptSubmit hook: detect incoming Discord messages, write chatid state file
for log routing, and inject a reminder to reply via the Discord tool.
Called by Claude Code UserPromptSubmit hook with JSON payload on stdin.
Prints additionalContext JSON if the prompt is a Discord message; exits silently otherwise.
"""
import json
import os
import re
import subprocess
import sys

_CHANNEL_TAG_RE = re.compile(
    r'<channel[^>]+source="plugin:discord:discord"[^>]+chat_id="(\d+)"'
)
_COMMAND_NAME_RE = re.compile(r'<command-name>(.*?)</command-name>', re.DOTALL)
_COMMAND_ARGS_RE = re.compile(r'<command-args>(.*?)</command-args>', re.DOTALL)

CONF_PATH = os.path.expanduser('~/.claude/hooks/discord-webhook.conf')
ROUTING_PATH = os.path.expanduser('~/.claude/hooks/discord-routing.json')
STATE_DIR = os.path.expanduser('~/.claude/hooks/state')
DEFAULT_MODEL = 'claude-sonnet-4-6'
MODEL_STATE_SUFFIX = '.model'


def load_conf():
    conf = {}
    try:
        with open(CONF_PATH) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, _, v = line.partition('=')
                    conf[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return conf


def load_routing():
    try:
        with open(ROUTING_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def get_parent_channel_id(chat_id, bot_token, session_id):
    """Return parent channel ID for a thread channel, with per-session caching."""
    cache_file = os.path.join(STATE_DIR, f'{session_id}.parentchatid')
    if os.path.exists(cache_file):
        try:
            cached = open(cache_file).read().strip()
            if cached:
                return cached
        except Exception:
            pass

    if not bot_token:
        return None

    try:
        result = subprocess.run(
            ['/usr/bin/curl', '-s', '--max-time', '3',
             f'https://discord.com/api/v10/channels/{chat_id}',
             '-H', f'Authorization: Bot {bot_token}'],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        parent_id = data.get('parent_id')
        if parent_id:
            try:
                os.makedirs(STATE_DIR, exist_ok=True)
                with open(cache_file, 'w') as f:
                    f.write(parent_id)
            except Exception:
                pass
        return parent_id
    except Exception:
        return None


def resolve_route_chat_id(chat_id, routing, bot_token, session_id):
    """Return the chat_id to use for log routing.

    If chat_id is directly in routing, use it. Otherwise try parent channel
    (handles threads spawned from watched channels like droneteleo).
    """
    if chat_id in routing:
        return chat_id
    parent_id = get_parent_channel_id(chat_id, bot_token, session_id)
    if parent_id and parent_id in routing:
        return parent_id
    return chat_id


def get_current_model(transcript_path):
    """Scan transcript from end to find the model of the last assistant response."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    try:
        with open(transcript_path) as f:
            lines = f.readlines()
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get('type') == 'assistant':
                    model = entry.get('message', {}).get('model', '')
                    if model:
                        return model
            except Exception:
                pass
    except Exception:
        pass
    return None


def resolve_log_webhook(session_id, conf, routing):
    """Return the log webhook URL for this session, with per-channel routing."""
    logs_url = conf.get('LOGS_WEBHOOK_URL', '')
    state_dir = STATE_DIR
    chat_id = ''
    for suffix in ('routechatid', 'chatid'):
        try:
            candidate = open(os.path.join(state_dir, f'{session_id}.{suffix}')).read().strip()
            if candidate:
                chat_id = candidate
                break
        except Exception:
            pass
    if not chat_id:
        chat_id = os.environ.get('DISCORD_CHAT_ID', '')
    if not chat_id:
        return logs_url
    var_name = routing.get(chat_id, '')
    if var_name:
        url = conf.get(var_name, '')
        if url:
            return url
    return logs_url


def post_to_webhook(url, text):
    """Fire-and-forget POST to a webhook URL."""
    payload = json.dumps({'content': text})
    subprocess.Popen(
        ['/usr/bin/curl', '-s', '-o', '/dev/null', '--max-time', '5',
         '-X', 'POST', url,
         '-H', 'Content-Type: application/json',
         '-d', payload],
        close_fds=True,
    )


def post_to_discord(chat_id, text, bot_token):
    payload = json.dumps({'content': text})
    subprocess.Popen(
        ['/usr/bin/curl', '-s', '-o', '/dev/null', '--max-time', '5',
         '-X', 'POST', f'https://discord.com/api/v10/channels/{chat_id}/messages',
         '-H', f'Authorization: Bot {bot_token}',
         '-H', 'Content-Type: application/json',
         '-d', payload],
        close_fds=True,
    )


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = data.get('prompt', '')
    session_id = data.get('session_id', '')
    transcript_path = data.get('transcript_path', '')

    conf = load_conf()
    routing = load_routing()
    bot_token = conf.get('DISCORD_BOT_TOKEN', '')

    # --- Path A: slash command detection (unconditional) ---
    cmd_m = _COMMAND_NAME_RE.search(prompt)
    if cmd_m:
        cmd_name = cmd_m.group(1).strip()
        args_m = _COMMAND_ARGS_RE.search(prompt)
        args_str = args_m.group(1).strip() if args_m else ''
        if args_str and len(args_str) > 120:
            args_str = args_str[:117] + '...'
        log_msg = f'**/{cmd_name}**' + (f' {args_str}' if args_str else '')
        log_url = resolve_log_webhook(session_id, conf, routing)
        if log_url:
            post_to_webhook(log_url, log_msg)

    # --- Path B: Discord channel message detection ---
    m = _CHANNEL_TAG_RE.search(prompt)
    if not m:
        sys.exit(0)

    chat_id = m.group(1)

    if session_id:
        os.makedirs(STATE_DIR, exist_ok=True)
        # chatid: actual Discord channel (used by stop-check to send replies)
        try:
            with open(os.path.join(STATE_DIR, f'{session_id}.chatid'), 'w') as f:
                f.write(chat_id)
        except Exception:
            pass
        # routechatid: effective channel for log routing (parent if thread)
        route_id = resolve_route_chat_id(chat_id, routing, bot_token, session_id)
        if route_id != chat_id:
            try:
                with open(os.path.join(STATE_DIR, f'{session_id}.routechatid'), 'w') as f:
                    f.write(route_id)
            except Exception:
                pass

    # Model alert: post compact note to Discord when running non-default model.
    #
    # Source priority:
    # 1. Per-session state file written by stop hook after a confirmed model switch.
    #    This is accurate because it's written AFTER the switch completes, so the
    #    next UserPromptSubmit sees the correct model with zero lag.
    # 2. Hook payload 'model' field (fallback). This lags by 1 turn — it reflects
    #    the model used for the previous response, not the current session config.
    #    Used when no state file exists (new session, or stop hook hasn't run yet).
    if bot_token:
        model_state_file = os.path.join(STATE_DIR, f'{session_id}{MODEL_STATE_SUFFIX}')
        model = ''
        try:
            model = open(model_state_file).read().strip()
        except Exception:
            pass
        if not model:
            model = data.get('model', '') or ''
        if model and DEFAULT_MODEL not in model:
            short = model.replace('claude-', '')
            if '/' in short:
                short = short.split('/')[-1]
            post_to_discord(chat_id, f'`[model: {short}]`', bot_token)

    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': (
                'REMINDER: This message arrived from Discord. The user reads Discord only'
                ' — they cannot see your terminal output. You MUST reply using the'
                ' mcp__plugin_discord_discord__reply tool. Do not respond only in the terminal.'
            )
        }
    }))


if __name__ == '__main__':
    main()
