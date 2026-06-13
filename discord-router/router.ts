import {
  Client,
  GatewayIntentBits,
  Partials,
  type Message,
} from "discord.js";
import {
  existsSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
  renameSync,
  rmSync,
} from "fs";
import { join } from "path";
import { homedir } from "os";

const THREAD_MAP_PATH = join(homedir(), ".claude/hooks/discord-thread-map.json");

// --- Upsert thread map atomically ---
function upsertThreadMap(parentId: string, userId: string, threadId: string): void {
  try {
    let map: Record<string, { thread: string; ts: number }> = {};
    if (existsSync(THREAD_MAP_PATH)) {
      try {
        map = JSON.parse(readFileSync(THREAD_MAP_PATH, "utf8"));
      } catch {
        // corrupt or missing — start fresh
      }
    }
    map[`${parentId}:${userId}`] = { thread: threadId, ts: Math.floor(Date.now() / 1000) };
    const tmp = `${THREAD_MAP_PATH}.tmp`;
    writeFileSync(tmp, JSON.stringify(map), { mode: 0o600 });
    renameSync(tmp, THREAD_MAP_PATH);
  } catch {
    // best-effort; never crash the router over a map write
  }
}

// --- Config paths ---
const HOME = homedir();
const ENV_PATH = join(HOME, ".claude/channels/discord/.env");
const ROUTES_PATH = join(HOME, ".claude/discord-router/routes.json");
const PID_PATH = join(HOME, ".claude/discord-router/router.pid");
const CHANNELS_BASE = join(HOME, ".claude/channels");

// --- Load token from .env ---
function loadToken(): string {
  if (!existsSync(ENV_PATH)) {
    process.stderr.write(
      `discord-router: .env file not found at ${ENV_PATH}. Copy .env.example if available.\n`
    );
    process.exit(1);
  }
  const raw = readFileSync(ENV_PATH, "utf8");
  for (const line of raw.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    const val = trimmed.slice(eq + 1).trim();
    if (key === "DISCORD_BOT_TOKEN") return val;
  }
  throw new Error(`DISCORD_BOT_TOKEN not found in ${ENV_PATH}`);
}

// --- Load routes ---
function loadRoutes(): Record<string, string> {
  const raw = readFileSync(ROUTES_PATH, "utf8");
  return JSON.parse(raw);
}

// --- Load access.json for a state dir ---
interface AccessPolicy {
  allowFrom: string[];
  requireMention?: boolean;
  ackReaction?: string;
}
interface AccessJson {
  groups?: Record<string, AccessPolicy>;
  ackReaction?: string;
  dmPolicy?: string;
  allowFrom?: string[];
}

function loadAccess(stateDirName: string): AccessJson | null {
  const path = join(CHANNELS_BASE, stateDirName, "access.json");
  if (!existsSync(path)) return null;
  try {
    return JSON.parse(readFileSync(path, "utf8")) as AccessJson;
  } catch {
    return null;
  }
}

// --- Gate check for guild channel messages ---
function passesGate(
  msg: Message,
  channelId: string,
  access: AccessJson,
  botUserId: string
): boolean {
  const groups = access.groups ?? {};
  const policy = groups[channelId];
  if (!policy) return false;

  if (policy.allowFrom.length > 0 && !policy.allowFrom.includes(msg.author.id)) {
    return false;
  }

  const requireMention = policy.requireMention ?? true;
  if (requireMention) {
    const mentionedBot = msg.mentions.users.has(botUserId);
    if (!mentionedBot) {
      // Reference check (reply to bot) handled after async fetch — gate fails here
      // If msg.reference is set, caller does the async check and calls a variant
      return false;
    }
  }

  return true;
}

async function passesGateAsync(
  msg: Message,
  channelId: string,
  access: AccessJson,
  botUserId: string
): Promise<boolean> {
  const groups = access.groups ?? {};
  const policy = groups[channelId];
  if (!policy) return false;

  if (policy.allowFrom.length > 0 && !policy.allowFrom.includes(msg.author.id)) {
    return false;
  }

  const requireMention = policy.requireMention ?? true;
  if (!requireMention) return true;

  // Check direct mention
  if (msg.mentions.users.has(botUserId)) return true;

  // Check if this is a reply to a bot message
  if (msg.reference?.messageId) {
    try {
      const referenced = await msg.channel.messages.fetch(msg.reference.messageId);
      if (referenced.author.id === botUserId) return true;
    } catch {
      // Could not fetch referenced message — treat as not a reply to bot
    }
  }

  return false;
}

// --- Write inbox file atomically ---
function writeInbox(stateDirName: string, msg: Message): void {
  const inboxDir = join(CHANNELS_BASE, stateDirName, "inbox");
  mkdirSync(inboxDir, { recursive: true, mode: 0o700 });

  const hasAttachments = msg.attachments.size > 0;
  const content =
    msg.content.trim() === "" && hasAttachments
      ? "(attachment)"
      : msg.content;

  const meta: Record<string, string> = {
    chat_id: msg.channelId,
    message_id: msg.id,
    user: msg.author.username,
    user_id: msg.author.id,
    ts: msg.createdAt.toISOString(),
  };

  if (hasAttachments) {
    meta.attachment_count = String(msg.attachments.size);
    const attachmentList = [...msg.attachments.values()]
      .map((a) => {
        const sizeKb = (a.size / 1024).toFixed(1);
        return `${a.name} (${a.contentType ?? "unknown"}, ${sizeKb}KB)`;
      })
      .join("; ");
    meta.attachments = attachmentList;
  }

  const payload = JSON.stringify({ content, meta }, null, 2);
  const filename = `${Date.now()}-${msg.id}.json`;
  const tmpPath = join(inboxDir, `${filename}.tmp`);
  const finalPath = join(inboxDir, filename);

  writeFileSync(tmpPath, payload, { mode: 0o600 });
  renameSync(tmpPath, finalPath);
}

// --- Main ---
async function main(): Promise<void> {
  const token = loadToken();
  const routes = loadRoutes();

  // Write PID
  writeFileSync(PID_PATH, String(process.pid), "utf8");

  // Clean up PID on exit
  const cleanup = (): void => {
    try {
      if (existsSync(PID_PATH)) {
        const pidInFile = readFileSync(PID_PATH, "utf8").trim();
        if (pidInFile === String(process.pid)) {
          rmSync(PID_PATH, { force: true });
        }
      }
    } catch {
      // best-effort
    }
    process.exit(0);
  };

  process.on("SIGTERM", cleanup);
  process.on("SIGINT", cleanup);

  process.on("unhandledRejection", (reason) => {
    process.stderr.write(`discord-router: unhandledRejection: ${reason}\n`);
  });

  process.on("uncaughtException", (err) => {
    process.stderr.write(`discord-router: uncaughtException: ${err.message}\n${err.stack}\n`);
  });

  const client = new Client({
    intents: [
      GatewayIntentBits.DirectMessages,
      GatewayIntentBits.Guilds,
      GatewayIntentBits.GuildMessages,
      GatewayIntentBits.MessageContent,
    ],
    partials: [Partials.Channel],
  });

  client.on("ready", () => {
    process.stderr.write(
      `discord-router: gateway connected as ${client.user?.tag ?? "unknown"}\n`
    );
  });

  client.on("messageCreate", async (msg: Message) => {
    try {
      // Skip bot messages to prevent feedback loops
      if (msg.author.bot) return;

      // Route DMs via "_dm" entry in routes.json
      if (!msg.guild) {
        const dmStateDirName = routes["_dm"];
        if (!dmStateDirName) return;
        const dmAccess = loadAccess(dmStateDirName);
        if (!dmAccess) return;
        if (dmAccess.dmPolicy === "allowlist") {
          const allowed = dmAccess.allowFrom ?? [];
          if (allowed.length > 0 && !allowed.includes(msg.author.id)) return;
        }
        writeInbox(dmStateDirName, msg);
        if (dmAccess.ackReaction && dmAccess.ackReaction.trim() !== "") {
          msg.react(dmAccess.ackReaction).catch(() => {});
        }
        return;
      }

      // Determine effective channel ID (use parent for threads)
      let channelId: string;
      if (msg.channel.isThread()) {
        channelId = msg.channel.parentId ?? msg.channelId;
      } else {
        channelId = msg.channelId;
      }

      // Route lookup
      const stateDirName = routes[channelId];
      if (!stateDirName) return;

      // Load access config
      const access = loadAccess(stateDirName);
      if (!access) return;

      // Gate check (async to support reply-to-bot detection)
      const botUserId = client.user!.id;
      const passes = await passesGateAsync(msg, channelId, access, botUserId);
      if (!passes) return;

      // Write inbox
      writeInbox(stateDirName, msg);

      // Keep thread map fresh: whenever the actual message channel is a thread,
      // immediately record parentId → userId → threadId so future hook lookups
      // see the current thread and not a stale one.
      if (msg.channel.isThread()) {
        const parentId = msg.channel.parentId;
        if (parentId) {
          upsertThreadMap(parentId, msg.author.id, msg.channelId);
        }
      }

      // Ack reaction
      if (access.ackReaction && access.ackReaction.trim() !== "") {
        msg.react(access.ackReaction).catch(() => {});
      }
    } catch (err) {
      process.stderr.write(
        `discord-router: messageCreate error: ${err instanceof Error ? err.message : String(err)}\n`
      );
    }
  });

  await client.login(token);
}

main().catch((err) => {
  process.stderr.write(
    `discord-router: fatal: ${err instanceof Error ? err.message : String(err)}\n`
  );
  process.exit(1);
});
