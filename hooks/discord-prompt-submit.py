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
_MESSAGE_ID_RE = re.compile(
    r'<channel[^>]+source="plugin:discord:discord"[^>]+message_id="(\d+)"'
)
_USER_ID_RE = re.compile(
    r'<channel[^>]+source="plugin:discord:discord"[^>]+user_id="(\d+)"'
)
_COMMAND_NAME_RE = re.compile(r'<command-name>(.*?)</command-name>', re.DOTALL)
_COMMAND_ARGS_RE = re.compile(r'<command-args>(.*?)</command-args>', re.DOTALL)

CONF_PATH = os.path.expanduser('~/.claude/hooks/discord-webhook.conf')
ROUTING_PATH = os.path.expanduser('~/.claude/hooks/discord-routing.json')
CHANNELS_PATH = os.path.expanduser('~/.claude/hooks/discord-channels.json')
LOG_CHANNELS_PATH = os.path.expanduser('~/.claude/hooks/discord-log-channels.json')
STATE_DIR = os.path.expanduser('~/.claude/hooks/state')
THREAD_MAP_PATH = os.path.expanduser('~/.claude/hooks/discord-thread-map.json')
ACTIVITY_LOG_PATH = os.path.expanduser('~/.claude/hooks/discord-activity.log')
ACTIVITY_LOG_MAX_BYTES = 500 * 1024  # 500 KB
ACTIVITY_LOG_TAIL_LINES = 200
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


def load_channels():
    try:
        with open(CHANNELS_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def load_log_channels():
    try:
        with open(LOG_CHANNELS_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def load_channel_context(context_json_path):
    try:
        with open(context_json_path) as f:
            return json.load(f)
    except Exception:
        return {}


def get_channel_hint(chat_id, channel_context, channels_map):
    if chat_id in channel_context:
        entry = channel_context[chat_id]
        name = entry.get('name', 'unknown')
        hint = entry.get('context_hint', '')
        return f"This session is from Discord channel: **{name}**. {hint}"
    elif chat_id in channels_map:
        name = channels_map.get(chat_id, 'unknown')
        return f"This session is from Discord channel: **{name}**."
    else:
        return f"This session is from Discord channel ID: {chat_id} (unknown channel — ask Geoff for a name if relevant)."


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


THREAD_MAP_TTL = 48 * 3600  # entries older than 48 hours are ignored


def get_mapped_thread(parent_id, user_id):
    """Return the last known thread for user_id in parent_id from the cross-session map.

    Supports both old string format and new dict format {"thread": "...", "ts": <epoch>}.
    Entries older than THREAD_MAP_TTL seconds are skipped.
    """
    try:
        import time
        mapping = json.load(open(THREAD_MAP_PATH))
        value = mapping.get(f'{parent_id}:{user_id}', '')
        if not value:
            return ''
        # New dict format
        if isinstance(value, dict):
            ts = value.get('ts', 0)
            if time.time() - ts > THREAD_MAP_TTL:
                return ''
            return value.get('thread', '')
        # Old plain-string format — treat as valid (no timestamp available)
        return value
    except Exception:
        return ''


def set_mapped_thread(parent_id, user_id, thread_id):
    """Record that user_id's current thread in parent_id is thread_id."""
    try:
        import time
        try:
            mapping = json.load(open(THREAD_MAP_PATH))
        except Exception:
            mapping = {}
        mapping[f'{parent_id}:{user_id}'] = {'thread': thread_id, 'ts': int(time.time())}
        with open(THREAD_MAP_PATH, 'w') as f:
            json.dump(mapping, f)
    except Exception:
        pass


def detect_thread_via_api(message_id, expected_parent_id, bot_token, session_id):
    """Detect a Discord thread from a message_id using two strategies.

    Attempt 1: Fetch the message from the parent channel via
    GET /channels/{expected_parent_id}/messages/{message_id}. If the message
    type is 21 (ThreadCreatedMessage) and has a 'thread' key, extract the thread
    ID from data['thread']['id']. This is the correct approach for thread-creation
    events where the starter message lives in the parent channel.

    Attempt 2 (fallback): GET /channels/{message_id} and check if it is itself a
    thread channel (type in 10/11/12) whose parent_id matches expected_parent_id.

    On success from either attempt, caches the thread ID in {session_id}.threadid
    to avoid repeated API calls this session.

    Returns the thread channel ID if confirmed, else empty string.
    """
    if not message_id or not bot_token:
        return ''

    def _cache(thread_id):
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(os.path.join(STATE_DIR, f'{session_id}.threadid'), 'w') as f:
                f.write(thread_id)
        except Exception:
            pass

    # Attempt 1: fetch the starter message from the parent channel
    try:
        result = subprocess.run(
            ['/usr/bin/curl', '-s', '--max-time', '3',
             f'https://discord.com/api/v10/channels/{expected_parent_id}/messages/{message_id}',
             '-H', f'Authorization: Bot {bot_token}'],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        # Message type 21 = ThreadCreatedMessage; 'thread' key holds the new thread's info
        if data.get('type') == 21 and 'thread' in data:
            thread_id = data['thread']['id']
            _cache(thread_id)
            return thread_id
    except Exception:
        pass

    # Attempt 2: check if message_id is itself a thread channel ID
    try:
        result = subprocess.run(
            ['/usr/bin/curl', '-s', '--max-time', '3',
             f'https://discord.com/api/v10/channels/{message_id}',
             '-H', f'Authorization: Bot {bot_token}'],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        # Discord thread types: 10 (news thread), 11 (public thread), 12 (private thread)
        if data.get('type') in (10, 11, 12) and data.get('parent_id') == expected_parent_id:
            _cache(message_id)
            return message_id
    except Exception:
        pass

    return ''


def resolve_thread_id(chat_id, message_id, user_id, bot_token, session_id):
    """Return a tuple (thread_id, method) when chat_id is a routing parent channel.

    Priority:
    1. Per-session .threadid cache (set earlier this session)
    2. API detection via detect_thread_via_api (catches new threads before map is updated)
    3. Cross-session thread map keyed by parent:user (fallback when API yields nothing)

    method is one of: 'session_cache', 'api_detection', 'thread_map', 'none'.
    Returns ('', 'none') if no thread is found.
    """
    # 1. Session cache
    try:
        cached = open(os.path.join(STATE_DIR, f'{session_id}.threadid')).read().strip()
        if cached:
            return cached, 'session_cache'
    except Exception:
        pass

    # 2. API detection — runs BEFORE the map so a new thread is found immediately
    api_thread = detect_thread_via_api(message_id, chat_id, bot_token, session_id)
    if api_thread:
        return api_thread, 'api_detection'

    # 3. Cross-session map (fallback when API yields nothing)
    if user_id:
        mapped = get_mapped_thread(chat_id, user_id)
        if mapped:
            # Write to session cache so future messages this session skip steps 2+3
            try:
                os.makedirs(STATE_DIR, exist_ok=True)
                with open(os.path.join(STATE_DIR, f'{session_id}.threadid'), 'w') as f:
                    f.write(mapped)
            except Exception:
                pass
            return mapped, 'thread_map'

    return '', 'none'


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


def write_activity_log(entry):
    """Append a JSON entry to the activity log. Cap file at ACTIVITY_LOG_MAX_BYTES."""
    try:
        import datetime
        log_path = ACTIVITY_LOG_PATH
        # Size cap: if over limit, truncate to last ACTIVITY_LOG_TAIL_LINES lines
        try:
            if os.path.exists(log_path) and os.path.getsize(log_path) > ACTIVITY_LOG_MAX_BYTES:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                lines = lines[-ACTIVITY_LOG_TAIL_LINES:]
                with open(log_path, 'w') as f:
                    f.writelines(lines)
        except Exception:
            pass
        line = json.dumps(entry, separators=(',', ':')) + '\n'
        with open(log_path, 'a') as f:
            f.write(line)
    except Exception:
        pass


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
    channels = load_channels()
    log_channels = load_log_channels()
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
    msg_m = _MESSAGE_ID_RE.search(prompt)
    message_id = msg_m.group(1) if msg_m else ''
    uid_m = _USER_ID_RE.search(prompt)
    user_id = uid_m.group(1) if uid_m else ''

    # Thread redirect: the Discord plugin sometimes delivers thread messages with the
    # parent channel's chat_id instead of the thread's channel ID.
    #
    # When chat_id is a known routing (parent) channel, look for the real thread using
    # three escalating strategies (session cache → cross-session map → API call).
    #
    # When chat_id is correctly the thread channel, record it in the cross-session map
    # so future sessions can find it without an API call.
    effective_chat_id = chat_id
    thread_redirect = ''
    resolution_method = 'none'

    if chat_id in routing:
        # chat_id is a parent/routing channel — look for thread override
        thread_id, resolution_method = resolve_thread_id(chat_id, message_id, user_id, bot_token, session_id)
        if thread_id:
            effective_chat_id = thread_id
            thread_redirect = (
                f'IMPORTANT: Although this message arrived tagged chat_id={chat_id} (the parent '
                f'channel), the actual conversation thread is {thread_id}. You MUST reply using '
                f'chat_id={thread_id}, NOT {chat_id}.'
            )
            # Update cross-session map so the next session finds this without an API call
            if user_id:
                set_mapped_thread(chat_id, user_id, thread_id)
    else:
        # chat_id is already the thread channel — record it for future sessions
        if user_id and session_id and bot_token:
            parent_id = get_parent_channel_id(chat_id, bot_token, session_id)
            if parent_id and parent_id in routing:
                set_mapped_thread(parent_id, user_id, chat_id)

    # Load channel context and build hint
    context_json_path = os.path.expanduser('~/.claude/hooks/discord-channel-context.json')
    channel_context = load_channel_context(context_json_path)
    channel_hint = get_channel_hint(effective_chat_id, channel_context, channels)

    route_id = resolve_route_chat_id(effective_chat_id, routing, bot_token, session_id)

    if session_id:
        os.makedirs(STATE_DIR, exist_ok=True)
        # chatid: effective reply channel (thread ID when thread detected, else raw chat_id)
        try:
            with open(os.path.join(STATE_DIR, f'{session_id}.chatid'), 'w') as f:
                f.write(effective_chat_id)
        except Exception:
            pass
        # routechatid: effective channel for log routing (parent if thread)
        if route_id != effective_chat_id:
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
            post_to_discord(effective_chat_id, f'`[model: {short}]`', bot_token)

    # --- Activity log ---
    import datetime
    log_channel_id = log_channels.get(route_id, '')
    write_activity_log({
        'ts': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'session_id': session_id,
        'event': 'message_received',
        'raw_chat_id': chat_id,
        'raw_chat_name': channels.get(chat_id, 'unknown'),
        'effective_chat_id': effective_chat_id,
        'effective_chat_name': channels.get(effective_chat_id, f'thread:{effective_chat_id}'),
        'route_chat_id': route_id,
        'route_chat_name': channels.get(route_id, 'unknown'),
        'log_channel_id': log_channel_id,
        'log_channel_name': channels.get(log_channel_id, 'unknown') if log_channel_id else 'unknown',
        'resolution_method': resolution_method,
        'transcript_path': transcript_path,
    })

    base_reminder = (
        'REMINDER: This message arrived from Discord. The user reads Discord only'
        ' — they cannot see your terminal output. You MUST reply using the'
        ' mcp__plugin_discord_discord__reply tool. Do not respond only in the terminal.'
    )
    additional_context = f'{channel_hint}\n\n{thread_redirect} {base_reminder}'.strip() if thread_redirect else f'{channel_hint}\n\n{base_reminder}'.strip()

    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': additional_context
        }
    }))


if __name__ == '__main__':
    main()
