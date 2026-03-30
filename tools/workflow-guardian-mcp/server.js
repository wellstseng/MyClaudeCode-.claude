/**
 * Workflow Guardian MCP Server + HTTP Dashboard
 *
 * MCP stdio server (JSON-RPC): lets Claude query/update workflow state
 * HTTP server (port 3848): serves dashboard UI for the user
 *
 * Zero npm dependencies. Node.js 18+.
 */

const fs = require("fs");
const path = require("path");
const http = require("http");
const { exec } = require("child_process");

// ─── Crash protection & logging ─────────────────────────────────────────────

const CLAUDE_DIR = path.join(require("os").homedir(), ".claude");
const WORKFLOW_DIR = path.join(CLAUDE_DIR, "workflow");
const CRASH_LOG = path.join(WORKFLOW_DIR, "guardian-crash.log");

function crashLog(label, err) {
  const ts = new Date().toISOString();
  const msg = `[${ts}] ${label}: ${err?.stack || err}\n`;
  try { fs.appendFileSync(CRASH_LOG, msg); } catch {}
  process.stderr.write(`[workflow-guardian] ${label}: ${err?.message || err}\n`);
}

process.on("uncaughtException", (err) => {
  crashLog("UncaughtException", err);
});
process.on("unhandledRejection", (reason) => {
  crashLog("UnhandledRejection", reason);
});
process.on("SIGTERM", () => {
  crashLog("SIGTERM", "Process received SIGTERM");
});
process.on("SIGINT", () => {
  crashLog("SIGINT", "Process received SIGINT");
});
const MEMORY_DIR = path.join(CLAUDE_DIR, "memory");
const TOOLS_DIR = path.join(CLAUDE_DIR, "tools");
const CONFIG_PATH = path.join(WORKFLOW_DIR, "config.json");
const REGISTRY_PATH = path.join(MEMORY_DIR, "project-registry.json");
const VERSION_PATH = path.join(CLAUDE_DIR, "version.json");
const DASHBOARD_PORT = loadConfig().dashboard_port || 3848;

function loadVersions() {
  try { return JSON.parse(fs.readFileSync(VERSION_PATH, "utf-8")); }
  catch { return { guardian: "0.0.0", atom_memory: "?" }; }
}
const VERSIONS = loadVersions();

function loadRegistry() {
  try {
    return JSON.parse(fs.readFileSync(REGISTRY_PATH, "utf-8"));
  } catch {
    return { projects: {} };
  }
}

/** Returns [{slug, memDir}] for all registered projects that have .claude/memory/ */
function getRegistryMemDirs() {
  const reg = loadRegistry();
  const results = [];
  for (const [slug, info] of Object.entries(reg.projects || {})) {
    if (!info.root) continue;
    const newMem = path.join(info.root, ".claude", "memory");
    if (fs.existsSync(newMem)) {
      results.push({ slug, memDir: newMem });
    }
  }
  return results;
}

function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
  } catch {
    return {};
  }
}

// ─── State File I/O ─────────────────────────────────────────────────────────

function listStatePaths() {
  try {
    return fs
      .readdirSync(WORKFLOW_DIR)
      .filter((f) => f.startsWith("state-") && f.endsWith(".json"))
      .map((f) => path.join(WORKFLOW_DIR, f));
  } catch {
    return [];
  }
}

function resolveSessionId(prefix) {
  // Support prefix matching: "3c7a47d0" → full UUID
  // Direct hit: exact filename exists → fast path
  const directPath = path.join(WORKFLOW_DIR, `state-${prefix}.json`);
  try { if (fs.existsSync(directPath)) return prefix; } catch {}

  // Prefix search: enumerate state files
  const ids = listStatePaths().map((p) =>
    path.basename(p).replace("state-", "").replace(".json", "")
  );
  const matches = ids.filter((id) => id.startsWith(prefix));
  if (matches.length === 1) return matches[0];
  if (matches.length === 0) return null;
  // Ambiguous: return null (caller handles error)
  return null;
}

function readState(sessionId) {
  const p = path.join(WORKFLOW_DIR, `state-${sessionId}.json`);
  try {
    return JSON.parse(fs.readFileSync(p, "utf-8"));
  } catch {
    return null;
  }
}

function writeState(sessionId, state) {
  state.last_updated = new Date().toISOString();
  const p = path.join(WORKFLOW_DIR, `state-${sessionId}.json`);
  const tmp = p + ".tmp";
  try {
    fs.mkdirSync(WORKFLOW_DIR, { recursive: true });
    fs.writeFileSync(tmp, JSON.stringify(state, null, 2), "utf-8");
    fs.renameSync(tmp, p);
  } catch {
    try { fs.unlinkSync(tmp); } catch {}
  }
}

function deleteState(sessionId) {
  const p = path.join(WORKFLOW_DIR, `state-${sessionId}.json`);
  try {
    fs.unlinkSync(p);
    return true;
  } catch {
    return false;
  }
}

function deriveSessionName(cwd) {
  if (!cwd) return "unknown";
  // Normalize path separators and extract last meaningful directory
  const parts = cwd.replace(/\\/g, "/").replace(/\/+$/, "").split("/").filter(Boolean);
  return parts[parts.length - 1] || "unknown";
}

function listAllSessions() {
  const cfg = loadConfig().cleanup || {};
  const DONE_TTL_MS    = cfg.ended_ttl_ms          || 60 * 1000;          // 1 min
  const ORPHAN_DONE_MS = cfg.orphan_done_ttl_ms     || 30 * 60 * 1000;    // 30 min
  const ORPHAN_WORK_MS = cfg.orphan_working_ttl_ms  || 24 * 60 * 60 * 1000; // 24 hr

  return listStatePaths().map((p) => {
    try {
      const state = JSON.parse(fs.readFileSync(p, "utf-8"));
      const sid = state.session?.id || path.basename(p).replace("state-", "").replace(".json", "");
      const now = Date.now();

      // ── Auto-cleanup (3-tier) ─────────────────────────────────────
      const safeTs = (v) => { const t = new Date(v).getTime(); return isNaN(t) ? 0 : t; };

      // Tier 1: ended_at is set → clean after 1 min
      if (state.ended_at) {
        const endedAge = now - safeTs(state.ended_at);
        if (endedAge > DONE_TTL_MS) {
          process.stderr.write(`[guardian] cleanup: ended session ${sid.slice(0,8)} (${Math.round(endedAge/60000)}min)\n`);
          try { fs.unlinkSync(p); } catch {}
          return null;
        }
      }

      // Tier 2: phase=done but no ended_at (orphan) → clean after 30 min
      if (!state.ended_at && state.phase === "done") {
        const lu = safeTs(state.last_updated);
        if (lu && (now - lu) > ORPHAN_DONE_MS) {
          process.stderr.write(`[guardian] cleanup: orphan-done ${sid.slice(0,8)} (${Math.round((now-lu)/60000)}min idle)\n`);
          try { fs.unlinkSync(p); } catch {}
          return null;
        }
      }

      // Tier 3: not done, no ended_at, no activity for 24h → dead session
      if (!state.ended_at && state.phase !== "done") {
        const ref = safeTs(state.last_updated) || safeTs(state.session?.started_at);
        if (ref && (now - ref) > ORPHAN_WORK_MS) {
          process.stderr.write(`[guardian] cleanup: stale-working ${sid.slice(0,8)} (${Math.round((now-ref)/3600000)}h idle)\n`);
          try { fs.unlinkSync(p); } catch {}
          return null;
        }
      }

      // ── Build session info ────────────────────────────────────────
      const startedAt = state.session?.started_at || "";
      const ageMs = startedAt ? now - new Date(startedAt).getTime() : 0;
      return {
        session_id: sid,
        name: deriveSessionName(state.session?.cwd),
        phase: state.phase || "unknown",
        project: state.session?.cwd || "",
        started_at: startedAt,
        modified_files_count: (state.modified_files || []).length,
        knowledge_queue_count: (state.knowledge_queue || []).length,
        sync_pending: state.sync_pending || false,
        age_minutes: Math.round(ageMs / 60000),
        ended: !!state.ended_at,
        muted: !!state.muted,
      };
    } catch {
      return null;
    }
  }).filter(Boolean);
}

// ─── MCP Protocol ───────────────────────────────────────────────────────────

let buffer = "";

process.stdin.setEncoding("utf-8");
process.stdin.on("data", (chunk) => {
  buffer += chunk;
  processBuffer();
});

function processBuffer() {
  // Newline-delimited JSON (Claude Code 2.x transport format)
  let line;
  while ((line = extractLine()) !== null) {
    if (!line.trim()) continue;
    try {
      const parsed = JSON.parse(line);
      handleMessage(parsed);
    } catch (err) {
      crashLog("PARSE_ERROR", err);
      sendError(null, -32700, "Parse error");
    }
  }
}

function extractLine() {
  // Try newline-delimited first (what Claude Code actually sends)
  const nlIdx = buffer.indexOf("\n");
  if (nlIdx !== -1) {
    const line = buffer.slice(0, nlIdx);
    buffer = buffer.slice(nlIdx + 1);
    return line;
  }
  return null;
}

function sendResponse(id, result) {
  const msg = JSON.stringify({ jsonrpc: "2.0", id, result });
  process.stdout.write(msg + "\n");
}

function sendError(id, code, message) {
  const msg = JSON.stringify({ jsonrpc: "2.0", id, error: { code, message } });
  process.stdout.write(msg + "\n");
}

// ─── MCP Message Handler ────────────────────────────────────────────────────

function handleMessage(msg) {
  const { id, method, params } = msg;

  switch (method) {
    case "initialize":
      sendResponse(id, {
        protocolVersion: "2025-11-25",
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "workflow-guardian", version: VERSIONS.guardian },
      });
      break;

    case "notifications/initialized":
      break;

    case "tools/list":
      sendResponse(id, { tools: TOOL_DEFINITIONS });
      break;

    case "tools/call":
      handleToolCall(id, params?.name, params?.arguments || {});
      break;

    default:
      if (id !== undefined) {
        sendError(id, -32601, `Method not found: ${method}`);
      }
  }
}

// ─── Tool Definitions ───────────────────────────────────────────────────────

const TOOL_DEFINITIONS = [
  {
    name: "workflow_status",
    description:
      "Query the current workflow guardian state. " +
      "Shows modified files, knowledge queue, sync status, and phase. " +
      "Omit session_id to list all active sessions.",
    inputSchema: {
      type: "object",
      properties: {
        session_id: {
          type: "string",
          description: "Session ID to query. Omit for all sessions.",
        },
      },
    },
  },
  {
    name: "workflow_signal",
    description:
      "Send a workflow signal to update session state. " +
      "Use sync_started when beginning sync, sync_completed when done, " +
      "reset to clear a stuck state.",
    inputSchema: {
      type: "object",
      properties: {
        session_id: { type: "string", description: "Target session ID" },
        signal: {
          type: "string",
          enum: ["sync_started", "sync_completed", "reset", "mute"],
          description: "Signal to send. Use 'mute' to silence Guardian reminders for this session.",
        },
      },
      required: ["session_id", "signal"],
    },
  },
  {
    name: "memory_queue_add",
    description:
      "Add a knowledge item to the session's pending memory queue. " +
      "Items will be written to atom files during end-of-session sync.",
    inputSchema: {
      type: "object",
      properties: {
        session_id: { type: "string" },
        content: {
          type: "string",
          description: "The knowledge to remember",
        },
        classification: {
          type: "string",
          enum: ["[固]", "[觀]", "[臨]"],
          description: "Memory classification level",
        },
        trigger_context: {
          type: "string",
          description: "What triggered this knowledge discovery",
        },
      },
      required: ["session_id", "content", "classification"],
    },
  },
  {
    name: "memory_queue_flush",
    description:
      "Mark all pending knowledge queue items as flushed (written to atoms). " +
      "Call this after successfully writing atom files.",
    inputSchema: {
      type: "object",
      properties: {
        session_id: { type: "string" },
      },
      required: ["session_id"],
    },
  },
];

// ─── Tool Handlers ──────────────────────────────────────────────────────────

function handleToolCall(id, toolName, args) {
  switch (toolName) {
    case "workflow_status":
      return toolWorkflowStatus(id, args);
    case "workflow_signal":
      return toolWorkflowSignal(id, args);
    case "memory_queue_add":
      return toolMemoryQueueAdd(id, args);
    case "memory_queue_flush":
      return toolMemoryQueueFlush(id, args);
    default:
      sendError(id, -32601, `Unknown tool: ${toolName}`);
  }
}

function toolWorkflowStatus(id, args) {
  if (args.session_id) {
    const resolved = resolveSessionId(args.session_id);
    if (!resolved) {
      return sendToolResult(id, `No state found for session ${args.session_id}`);
    }
    const state = readState(resolved);
    if (!state) {
      return sendToolResult(id, `No state found for session ${args.session_id}`);
    }
    const modFiles = (state.modified_files || [])
      .map((m) => `  - ${m.path} (${m.tool} @ ${m.at})`)
      .join("\n");
    const kqItems = (state.knowledge_queue || [])
      .map((q) => `  - ${q.classification} ${q.content}`)
      .join("\n");
    const text = [
      `## Session ${args.session_id}`,
      `- Phase: ${state.phase}`,
      `- CWD: ${state.session?.cwd || "?"}`,
      `- Started: ${state.session?.started_at || "?"}`,
      `- Sync pending: ${state.sync_pending}`,
      `- Stop blocked: ${state.stop_blocked_count || 0}x`,
      "",
      `### Modified files (${(state.modified_files || []).length})`,
      modFiles || "  (none)",
      "",
      `### Knowledge queue (${(state.knowledge_queue || []).length})`,
      kqItems || "  (none)",
    ].join("\n");
    return sendToolResult(id, text);
  }

  // List all sessions
  const sessions = listAllSessions();
  if (sessions.length === 0) {
    return sendToolResult(id, "No active workflow sessions.");
  }
  const lines = sessions.map(
    (s) =>
      `- **${s.session_id.slice(0, 8)}** | ${s.phase} | files: ${s.modified_files_count} | knowledge: ${s.knowledge_queue_count} | ${s.age_minutes}min${s.ended ? " (ended)" : ""}`
  );
  return sendToolResult(id, "## Active Sessions\n" + lines.join("\n"));
}

function toolWorkflowSignal(id, args) {
  const { session_id, signal } = args;
  const resolved = resolveSessionId(session_id);
  if (!resolved) {
    return sendToolResult(id, `No state found for session ${session_id}`, true);
  }
  const state = readState(resolved);
  if (!state) {
    return sendToolResult(id, `No state found for session ${session_id}`, true);
  }

  switch (signal) {
    case "sync_started":
      state.phase = "syncing";
      break;
    case "sync_completed":
      state.phase = "done";
      state.sync_pending = false;
      state.knowledge_queue = [];
      state.modified_files = [];
      state.ended_at = new Date().toISOString();
      break;
    case "reset":
      state.phase = "working";
      state.sync_pending = false;
      state.stop_blocked_count = 0;
      state.remind_count = 0;
      state.muted = false;
      break;
    case "mute":
      state.muted = true;
      break;
  }

  writeState(resolved, state);
  return sendToolResult(id, `Signal '${signal}' applied. Phase: ${state.phase}`);
}

function toolMemoryQueueAdd(id, args) {
  const { session_id, content, classification, trigger_context } = args;
  const resolved = resolveSessionId(session_id);
  if (!resolved) {
    return sendToolResult(id, `No state found for session ${session_id}`, true);
  }
  const state = readState(resolved);
  if (!state) {
    return sendToolResult(id, `No state found for session ${session_id}`, true);
  }

  state.knowledge_queue = state.knowledge_queue || [];
  state.knowledge_queue.push({
    content,
    classification: classification || "[臨]",
    context: trigger_context || "",
    at: new Date().toISOString(),
  });
  state.sync_pending = true;
  writeState(resolved, state);

  return sendToolResult(
    id,
    `Added to knowledge queue (${state.knowledge_queue.length} items): ${classification} ${content.slice(0, 60)}`
  );
}

function toolMemoryQueueFlush(id, args) {
  const { session_id } = args;
  const resolved = resolveSessionId(session_id);
  if (!resolved) {
    return sendToolResult(id, `No state found for session ${session_id}`, true);
  }
  const state = readState(resolved);
  if (!state) {
    return sendToolResult(id, `No state found for session ${session_id}`, true);
  }

  const count = (state.knowledge_queue || []).length;
  state.knowledge_queue = [];
  writeState(resolved, state);

  return sendToolResult(id, `Flushed ${count} knowledge queue items.`);
}

function sendToolResult(id, text, isError = false) {
  sendResponse(id, {
    content: [{ type: "text", text }],
    ...(isError && { isError: true }),
  });
}

// ─── v2.1 API Handlers ──────────────────────────────────────────────────────

function jsonRes(res, code, data) {
  res.writeHead(code, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

// Build a safe python command (Windows path backslashes must be forward-slashed for exec)
function pyCmd(scriptPath, args) {
  return 'python "' + scriptPath.replace(/\\/g, "/") + '" ' + args;
}

// --- Episodic Atom Parser & API ---

function parseEpisodicAtom(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  const atom = {
    filename: path.basename(filePath),
    title: "", confidence: "", type: "", triggers: [],
    last_used: "", created: "", ttl: "", expires_at: "",
    days_until_expiry: null, knowledge_lines: [], full_content: content,
  };
  const titleMatch = content.match(/^#\s+(.+)$/m);
  if (titleMatch) atom.title = titleMatch[1];
  const metaRe = /^-\s+([\w-]+):\s*(.+)$/gm;
  let m;
  while ((m = metaRe.exec(content)) !== null) {
    const key = m[1].toLowerCase(), val = m[2].trim();
    switch (key) {
      case "confidence": atom.confidence = val; break;
      case "type": atom.type = val; break;
      case "trigger": atom.triggers = val.split(",").map(t => t.trim()); break;
      case "last-used": atom.last_used = val; break;
      case "created": atom.created = val; break;
      case "ttl": atom.ttl = val; break;
      case "expires-at":
        atom.expires_at = val;
        const expDate = new Date(val);
        atom.days_until_expiry = Math.ceil((expDate - new Date()) / 86400000);
        break;
    }
  }
  let inKnowledge = false;
  for (const line of content.split("\n")) {
    if (/^##\s+知識/.test(line)) { inKnowledge = true; continue; }
    if (/^##\s+/.test(line) && inKnowledge) break;
    if (inKnowledge && line.trim().startsWith("-")) {
      atom.knowledge_lines.push(line.trim().replace(/^-\s*/, ""));
    }
  }
  return atom;
}

function apiEpisodic(req, res) {
  try {
    const dirsToScan = [MEMORY_DIR];
    // V2.21: scan registry project dirs (new path)
    for (const { memDir } of getRegistryMemDirs()) {
      if (!dirsToScan.includes(memDir)) dirsToScan.push(memDir);
    }
    // Also scan old project-level episodic dirs (fallback for unregistered projects)
    const projectsDir = path.join(CLAUDE_DIR, "projects");
    if (fs.existsSync(projectsDir)) {
      for (const proj of fs.readdirSync(projectsDir)) {
        const projMemDir = path.join(projectsDir, proj, "memory");
        if (fs.existsSync(projMemDir) && !dirsToScan.includes(projMemDir)) dirsToScan.push(projMemDir);
      }
    }
    const atoms = [];
    for (const dir of dirsToScan) {
      const epicDir = path.join(dir, "episodic");
      if (!fs.existsSync(epicDir)) continue;
      try {
        const files = fs.readdirSync(epicDir)
          .filter(f => f.startsWith("episodic-") && f.endsWith(".md"));
        for (const f of files) {
          try { atoms.push(parseEpisodicAtom(path.join(epicDir, f))); }
          catch {}
        }
      } catch {}
    }
    atoms.sort((a, b) => (b.created || "").localeCompare(a.created || ""));
    jsonRes(res, 200, atoms);
  } catch { jsonRes(res, 200, []); }
}

// --- Memory Health API (cached) ---

let healthCache = { data: null, timestamp: 0 };
const HEALTH_CACHE_TTL_MS = 60000;

function apiHealth(req, res, forceRefresh) {
  const now = Date.now();
  if (!forceRefresh && healthCache.data && (now - healthCache.timestamp) < HEALTH_CACHE_TTL_MS) {
    return jsonRes(res, 200, healthCache.data);
  }
  const auditScript = path.join(TOOLS_DIR, "memory-audit.py");
  const healthScript = path.join(TOOLS_DIR, "atom-health-check.py");
  // Run both tools in parallel
  let auditDone = false, healthDone = false;
  let auditData = null, healthData = null;
  let responded = false;
  const tryMerge = () => {
    if (!auditDone || !healthDone || responded) return;
    responded = true;
    const merged = auditData || {};
    if (healthData) {
      merged.broken_refs = healthData.broken_refs || [];
      merged.missing_reverse_refs = healthData.missing_reverse_refs || [];
      merged.stale_atoms = healthData.stale_atoms || [];
    }
    healthCache = { data: merged, timestamp: Date.now() };
    jsonRes(res, 200, merged);
  };
  exec(pyCmd(auditScript, "--json"), { timeout: 30000 }, (err, stdout) => {
    if (stdout) { try { auditData = JSON.parse(stdout); } catch {} }
    auditDone = true;
    tryMerge();
  });
  exec(pyCmd(healthScript, "--report --json"), { timeout: 30000 }, (err, stdout) => {
    if (stdout) { try { healthData = JSON.parse(stdout); } catch {} }
    healthDone = true;
    tryMerge();
  });
}

// --- E2E Test Runner (async jobs) ---

const testJobs = new Map();

function apiTestRunStart(req, res) {
  // Only one running test at a time
  for (const [, j] of testJobs) {
    if (j.status === "running") return jsonRes(res, 409, { error: "test already running", job_id: j.id });
  }
  const jobId = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  const job = { id: jobId, status: "running", result: null, startedAt: Date.now(), finishedAt: null };
  testJobs.set(jobId, job);

  const scriptPath = path.join(TOOLS_DIR, "test-memory-v21.py");
  exec(pyCmd(scriptPath, "--json"), { timeout: 120000 }, (err, stdout, stderr) => {
    if (!testJobs.has(jobId)) return;
    // Script exits non-zero when tests fail — still parse stdout
    if (stdout) {
      try { job.result = JSON.parse(stdout); job.status = "completed"; }
      catch { /* fall through to error handling */ }
    }
    if (!job.result) {
      if (err) { job.status = "error"; job.result = { error: err.message, stderr: (stderr || "").slice(0, 1000) }; }
      else { job.status = "error"; job.result = { error: "empty output" }; }
    }
    job.finishedAt = Date.now();
    setTimeout(() => testJobs.delete(jobId), 300000);
  });

  jsonRes(res, 202, { job_id: jobId, status: "running" });
}

function apiTestRunStatus(req, res, jobId) {
  const job = testJobs.get(jobId);
  if (!job) return jsonRes(res, 404, { error: "job not found" });
  jsonRes(res, 200, {
    job_id: jobId, status: job.status,
    elapsed_ms: (job.finishedAt || Date.now()) - job.startedAt,
    result: job.result,
  });
}

// --- Vector Status Proxy ---

function apiVectorStatus(req, res) {
  const cfg = loadConfig();
  const port = cfg.vector_search?.service_port || 3849;
  const proxyReq = http.request(
    { hostname: "127.0.0.1", port, path: "/status", method: "GET", timeout: 5000 },
    (proxyRes) => {
      let body = "";
      proxyRes.on("data", chunk => body += chunk);
      proxyRes.on("end", () => {
        try { jsonRes(res, 200, JSON.parse(body)); }
        catch { jsonRes(res, 502, { error: "invalid response from vector service" }); }
      });
    }
  );
  proxyReq.on("error", () => jsonRes(res, 503, { error: "vector service unreachable", port }));
  proxyReq.on("timeout", () => { proxyReq.destroy(); jsonRes(res, 504, { error: "vector service timeout" }); });
  proxyReq.end();
}

// --- Knowledge Queue Aggregation ---

function apiKnowledgeQueue(req, res) {
  const sessions = listAllSessions();
  const items = [];
  for (const s of sessions) {
    if (s.ended) continue;
    const state = readState(s.session_id);
    if (!state) continue;
    for (const kq of (state.knowledge_queue || [])) {
      items.push({ session_id: s.session_id, session_name: s.name, ...kq });
    }
  }
  jsonRes(res, 200, items);
}

// --- Atoms Browser API ---

function apiProjects(req, res) {
  const reg = loadRegistry();
  const projects = [];
  for (const [slug, info] of Object.entries(reg.projects || {})) {
    const proj = {
      slug,
      root: info.root || "",
      last_seen: info.last_seen || "",
      aliases: info.aliases || [],
      has_memory: false,
      atom_count: 0,
      failure_count: 0,
      episodic_count: 0,
    };
    // V2.21: if root itself is the .claude dir, memory is at root/memory/ directly
    const rootNorm = path.resolve(info.root || "");
    const isClaudeDir = rootNorm.toLowerCase() === path.resolve(CLAUDE_DIR).toLowerCase();
    const memDir = isClaudeDir
      ? path.join(rootNorm, "memory")
      : path.join(rootNorm, ".claude", "memory");
    if (fs.existsSync(memDir) && fs.existsSync(path.join(memDir, "MEMORY.md"))) {
      proj.has_memory = true;
      try {
        proj.atom_count = fs.readdirSync(memDir).filter(f =>
          f.endsWith(".md") && f !== "MEMORY.md" && !f.startsWith("_") && !f.startsWith("SPEC_")
        ).length;
      } catch {}
      try {
        const failDir = path.join(memDir, "failures");
        if (fs.existsSync(failDir)) {
          proj.failure_count = fs.readdirSync(failDir).filter(f => f.endsWith(".md") && f !== "_INDEX.md").length;
        }
      } catch {}
      try {
        const epicDir = path.join(memDir, "episodic");
        if (fs.existsSync(epicDir)) {
          proj.episodic_count = fs.readdirSync(epicDir).filter(f => f.endsWith(".md")).length;
        }
      } catch {}
    }
    projects.push(proj);
  }
  projects.sort((a, b) => (b.last_seen || "").localeCompare(a.last_seen || ""));
  jsonRes(res, 200, projects);
}

function apiAtoms(req, res) {
  const atoms = [];
  const scanDirs = [
    { dir: MEMORY_DIR, layer: "global" },
    { dir: path.join(MEMORY_DIR, "failures"), layer: "failures" },
    { dir: path.join(MEMORY_DIR, "unity"), layer: "unity" },
  ];

  for (const { dir, layer } of scanDirs) {
    if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir)) {
      if (!f.endsWith(".md")) continue;
      if (f === "MEMORY.md" || f.startsWith("SPEC_") || f.startsWith("_")) continue;

      const filePath = path.join(dir, f);
      try {
        const content = fs.readFileSync(filePath, "utf-8");
        const atom = { name: f.replace(".md", ""), layer, file: f };

        // Parse metadata
        const metaRe = /^-\s+([\w-]+):\s*(.+)$/gm;
        let m;
        while ((m = metaRe.exec(content)) !== null) {
          const key = m[1].toLowerCase(), val = m[2].trim();
          switch (key) {
            case "confidence": atom.confidence = val; break;
            case "last-used": atom.last_used = val; break;
            case "confirmations": atom.confirmations = parseInt(val) || 0; break;
            case "trigger": atom.triggers = val.split(",").map(t => t.trim()); break;
            case "related": atom.related = val.split(",").map(t => t.trim()); break;
            case "created": atom.created = val; break;
            case "type": atom.type = val; break;
            case "tags": atom.tags = val.split(",").map(t => t.trim()); break;
          }
        }

        // Count knowledge items
        let knowledgeCount = 0;
        let inKnowledge = false;
        for (const line of content.split("\n")) {
          if (/^##\s+知識/.test(line)) { inKnowledge = true; continue; }
          if (/^##\s+/.test(line) && inKnowledge) break;
          if (inKnowledge && /^- \[/.test(line)) knowledgeCount++;
        }
        atom.knowledge_count = knowledgeCount;

        // Line count
        atom.line_count = content.split("\n").length;

        // Days since last used
        if (atom.last_used) {
          const lu = new Date(atom.last_used);
          atom.days_since_used = Math.floor((Date.now() - lu.getTime()) / 86400000);
        }

        // Full content for detail view
        atom.content = content;

        atoms.push(atom);
      } catch {}
    }
  }

  // Helper: scan a project memory dir and push atoms
  function scanProjMemDir(projMemDir, layerLabel) {
    if (!fs.existsSync(projMemDir)) return;
    for (const f of fs.readdirSync(projMemDir)) {
      if (!f.endsWith(".md")) continue;
      if (f === "MEMORY.md" || f.startsWith("_")) continue;
      try {
        const content = fs.readFileSync(path.join(projMemDir, f), "utf-8");
        // Skip pointer-type MEMORY.md redirects
        if (content.includes("Status: migrated-v2.21")) continue;
        const atom = { name: f.replace(".md", ""), layer: layerLabel, file: f, content };
        const metaRe = /^-\s+([\w-]+):\s*(.+)$/gm;
        let m2;
        while ((m2 = metaRe.exec(content)) !== null) {
          const key = m2[1].toLowerCase(), val = m2[2].trim();
          switch (key) {
            case "confidence": atom.confidence = val; break;
            case "last-used": atom.last_used = val; break;
            case "confirmations": atom.confirmations = parseInt(val) || 0; break;
            case "related": atom.related = val.split(",").map(t => t.trim()); break;
          }
        }
        atom.line_count = content.split("\n").length;
        atoms.push(atom);
      } catch {}
    }
  }

  // V2.21: scan registry project dirs (new path)
  const seenProjDirs = new Set();
  for (const { slug, memDir } of getRegistryMemDirs()) {
    scanProjMemDir(memDir, "project:" + slug);
    seenProjDirs.add(memDir);
  }

  // Also scan old project memory dirs (fallback for unregistered projects)
  const projectsDir = path.join(CLAUDE_DIR, "projects");
  if (fs.existsSync(projectsDir)) {
    for (const proj of fs.readdirSync(projectsDir)) {
      const projMemDir = path.join(projectsDir, proj, "memory");
      if (seenProjDirs.has(projMemDir)) continue;
      scanProjMemDir(projMemDir, "project:" + proj);
    }
  }

  atoms.sort((a, b) => (b.last_used || "").localeCompare(a.last_used || ""));
  jsonRes(res, 200, atoms);
}

// ─── HTTP Dashboard ─────────────────────────────────────────────────────────

const DASHBOARD_HTML = `<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>工作流守衛 v${VERSIONS.guardian}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, "Segoe UI", sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }
  h1 { color: #58a6ff; margin-bottom: 4px; font-size: 1.4em; }
  .subtitle { color: #8b949e; font-size: 0.85em; margin-bottom: 12px; }
  .stats { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
  .stat { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 10px 14px; min-width: 100px; }
  .stat-value { font-size: 1.4em; font-weight: bold; color: #58a6ff; }
  .stat-label { font-size: 0.75em; color: #8b949e; }
  .tab-nav { display: flex; gap: 0; border-bottom: 1px solid #30363d; margin-bottom: 16px; }
  .tab-btn { padding: 8px 16px; border: none; background: none; color: #8b949e; cursor: pointer; border-bottom: 2px solid transparent; font-size: 0.9em; font-family: inherit; }
  .tab-btn:hover { color: #c9d1d9; }
  .tab-btn.active { color: #58a6ff; border-bottom-color: #58a6ff; }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }
  .sessions { display: flex; flex-direction: column; gap: 12px; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; }
  .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .card-name { font-weight: 600; color: #e6edf3; font-size: 1.05em; }
  .card-id { font-family: monospace; color: #79c0ff; font-size: 0.85em; }
  .badge { padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600; }
  .badge-init { background: #1f6feb33; color: #58a6ff; }
  .badge-working { background: #f0883e33; color: #f0883e; }
  .badge-syncing { background: #d2a82633; color: #d2a826; }
  .badge-done { background: #23863633; color: #3fb950; }
  .card-meta { font-size: 0.8em; color: #8b949e; margin-bottom: 8px; }
  .card-stats { display: flex; gap: 16px; font-size: 0.85em; }
  .card-stats span { color: #8b949e; }
  .card-stats strong { color: #c9d1d9; }
  .details { margin-top: 10px; padding-top: 10px; border-top: 1px solid #30363d; font-size: 0.82em; }
  .details summary { cursor: pointer; color: #58a6ff; margin-bottom: 6px; }
  .file-list, .kq-list { list-style: none; padding-left: 8px; }
  .file-list li, .kq-list li { padding: 2px 0; color: #8b949e; font-family: monospace; font-size: 0.9em; }
  .kq-badge { font-weight: bold; }
  .kq-badge-fixed { color: #3fb950; }
  .kq-badge-observe { color: #d2a826; }
  .kq-badge-temp { color: #f0883e; }
  .actions { margin-top: 10px; display: flex; gap: 8px; }
  .btn { padding: 4px 12px; border-radius: 4px; border: 1px solid #30363d; background: #21262d; color: #c9d1d9; cursor: pointer; font-size: 0.8em; font-family: inherit; }
  .btn:hover { background: #30363d; }
  .btn-primary { border-color: #388bfd66; color: #58a6ff; }
  .btn-primary:hover { background: #388bfd22; }
  .btn-success { border-color: #3fb95066; color: #3fb950; }
  .btn-success:hover { background: #3fb95022; }
  .btn-danger { border-color: #f8514966; color: #f85149; }
  .btn-danger:hover { background: #f8514922; }
  .empty { text-align: center; color: #8b949e; padding: 40px; }
  .auto-refresh { font-size: 0.8em; color: #8b949e; }
  .auto-refresh label { cursor: pointer; }
  /* Timeline */
  .timeline { position: relative; padding-left: 28px; border-left: 2px solid #30363d; margin-left: 8px; }
  .timeline-item { position: relative; margin-bottom: 16px; }
  .timeline-dot { position: absolute; left: -35px; top: 10px; width: 12px; height: 12px; border-radius: 50%; border: 2px solid #0d1117; }
  .ttl-green { background: #3fb950; }
  .ttl-yellow { background: #d2a826; }
  .ttl-red { background: #f85149; }
  .ttl-critical { background: #f85149; animation: pulse 1s infinite; }
  .ttl-expired { background: #484f58; }
  @keyframes pulse { 50% { opacity: 0.4; } }
  .timeline-card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px; }
  .timeline-date { font-size: 0.75em; color: #8b949e; }
  .timeline-title { font-weight: 600; color: #e6edf3; margin: 4px 0; }
  .timeline-ttl { font-size: 0.8em; padding: 1px 6px; border-radius: 8px; font-weight: 600; }
  .timeline-knowledge { margin-top: 8px; font-size: 0.82em; color: #8b949e; }
  .timeline-knowledge li { padding: 2px 0; list-style: none; }
  .timeline-full { margin-top: 8px; padding-top: 8px; border-top: 1px solid #30363d; white-space: pre-wrap; font-family: monospace; font-size: 0.78em; color: #8b949e; max-height: 300px; overflow-y: auto; }
  /* Health */
  .health-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; margin-bottom: 16px; }
  .health-stat { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px; text-align: center; }
  .health-stat .val { font-size: 1.5em; font-weight: bold; }
  .health-stat .lbl { font-size: 0.75em; color: #8b949e; }
  .issue-table { width: 100%; border-collapse: collapse; font-size: 0.82em; margin-bottom: 16px; }
  .issue-table th { text-align: left; color: #8b949e; padding: 6px 8px; border-bottom: 1px solid #30363d; }
  .issue-table td { padding: 6px 8px; border-bottom: 1px solid #21262d; }
  .level-error { color: #f85149; }
  .level-warning { color: #d2a826; }
  .level-info { color: #58a6ff; }
  .suggest-list { list-style: none; margin-bottom: 16px; }
  .suggest-list li { padding: 6px 0; border-bottom: 1px solid #21262d; font-size: 0.85em; }
  .suggest-arrow { color: #58a6ff; font-weight: bold; }
  .cache-info { font-size: 0.75em; color: #484f58; margin-top: 8px; }
  /* Tests */
  .test-card { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 6px; margin-bottom: 6px; background: #161b22; border: 1px solid #30363d; }
  .test-pass { border-left: 3px solid #3fb950; }
  .test-fail { border-left: 3px solid #f85149; }
  .test-skip { border-left: 3px solid #8b949e; }
  .test-icon { font-size: 1.1em; width: 22px; text-align: center; }
  .test-name { font-weight: 600; color: #e6edf3; flex: 1; }
  .test-duration { font-size: 0.8em; color: #8b949e; }
  .test-msg { font-size: 0.78em; color: #8b949e; font-family: monospace; }
  .test-summary { display: flex; gap: 16px; padding: 12px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 12px; font-size: 0.9em; }
  .spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid #30363d; border-top-color: #58a6ff; border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 8px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .run-btn { padding: 10px 24px; font-size: 1em; border-radius: 6px; border: 1px solid #3fb95066; background: #23863622; color: #3fb950; cursor: pointer; font-weight: 600; font-family: inherit; }
  .run-btn:hover { background: #23863644; }
  .run-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  /* Vector */
  .vec-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .vec-section { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 14px; }
  .vec-section h3 { font-size: 0.9em; color: #58a6ff; margin-bottom: 8px; }
  .vec-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 0.85em; }
  .vec-row .k { color: #8b949e; }
  .vec-row .v { color: #e6edf3; font-family: monospace; }
  .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
  .status-online { background: #3fb950; }
  .status-offline { background: #f85149; }
  .section-title { font-size: 1em; font-weight: 600; color: #e6edf3; margin-bottom: 10px; }
  /* Atoms */
  .atom-table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
  .atom-table th { text-align: left; color: #8b949e; padding: 8px; border-bottom: 2px solid #30363d; cursor: pointer; user-select: none; }
  .atom-table th:hover { color: #58a6ff; }
  .atom-table td { padding: 8px; border-bottom: 1px solid #21262d; }
  .atom-table tr:hover { background: #161b2288; }
  .atom-name { color: #58a6ff; font-weight: 600; cursor: pointer; }
  .atom-name:hover { text-decoration: underline; }
  .atom-layer { font-size: 0.8em; padding: 1px 6px; border-radius: 8px; background: #30363d; color: #8b949e; }
  .atom-conf { font-weight: bold; }
  .conf-fixed { color: #3fb950; }
  .conf-observe { color: #d2a826; }
  .conf-temp { color: #f0883e; }
  .atom-detail { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin: 12px 0; white-space: pre-wrap; font-family: monospace; font-size: 0.82em; max-height: 500px; overflow-y: auto; }
  .atom-filter { padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 0.9em; margin-bottom: 12px; width: 300px; font-family: inherit; }
  .atom-filter::placeholder { color: #484f58; }
  .atom-stats { display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
  .proj-table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
  .proj-table th { text-align: left; color: #8b949e; padding: 8px; border-bottom: 2px solid #30363d; }
  .proj-table td { padding: 8px; border-bottom: 1px solid #21262d; vertical-align: top; }
  .proj-table tr:hover { background: #161b2288; }
  .proj-root { font-family: monospace; font-size: 0.85em; color: #79c0ff; word-break: break-all; }
  .proj-badge-mem { background: #23863622; color: #3fb950; padding: 2px 6px; border-radius: 4px; font-size: 0.75em; }
  .proj-badge-nomem { background: #30363d; color: #8b949e; padding: 2px 6px; border-radius: 4px; font-size: 0.75em; }
  .proj-alias { font-size: 0.8em; color: #8b949e; }
  .proj-filter-btn { background: none; border: 1px solid #30363d; color: #58a6ff; padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8em; font-family: inherit; }
  .proj-filter-btn:hover { background: #58a6ff22; }
</style>
</head>
<body>
<div style="display:flex;justify-content:space-between;align-items:baseline;">
  <div><h1>工作流守衛 v${VERSIONS.guardian}</h1><p class="subtitle">記憶與對話監控</p></div>
  <div class="auto-refresh"><label><input type="checkbox" id="autoRefresh" checked> 自動重整 (5秒)</label></div>
</div>

<div class="stats" id="statsBar"></div>

<nav class="tab-nav">
  <button class="tab-btn active" data-tab="sessions">對話</button>
  <button class="tab-btn" data-tab="episodic">情境記憶</button>
  <button class="tab-btn" data-tab="health">健康檢查</button>
  <button class="tab-btn" data-tab="atoms">原子記憶 v${VERSIONS.atom_memory}</button>
  <button class="tab-btn" data-tab="projects">已知專案</button>
  <button class="tab-btn" data-tab="tests">測試</button>
  <button class="tab-btn" data-tab="vector">向量服務</button>
</nav>

<div id="panelSessions" class="tab-panel active">
  <div class="sessions" id="sessionList"></div>
</div>

<div id="panelEpisodic" class="tab-panel">
  <div id="episodicContent"></div>
</div>

<div id="panelHealth" class="tab-panel">
  <div id="healthContent"><div class="empty">載入健康資料中...</div></div>
</div>

<div id="panelAtoms" class="tab-panel">
  <div id="atomsContent"><div class="empty">載入原子記憶中...</div></div>
</div>

<div id="panelProjects" class="tab-panel">
  <div id="projectsContent"><div class="empty">載入已知專案中...</div></div>
</div>

<div id="panelTests" class="tab-panel">
  <div id="testsContent">
    <div style="text-align:center;padding:20px;">
      <button class="run-btn" id="runTestsBtn" onclick="startTestRun()">執行端對端測試</button>
    </div>
    <div id="testResults"></div>
  </div>
</div>

<div id="panelVector" class="tab-panel">
  <div id="vectorContent"><div class="empty">載入向量服務狀態中...</div></div>
</div>

<script>
let refreshTimer;
let currentTab = "sessions";
let testJobId = null;
let testPollTimer = null;

// ─── Tab Switching ───

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    currentTab = btn.dataset.tab;
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    document.getElementById("panel" + currentTab.charAt(0).toUpperCase() + currentTab.slice(1)).classList.add("active");
    refreshCurrentTab();
  });
});

async function refreshCurrentTab() {
  const prevScroll = window.scrollY;
  switch (currentTab) {
    case "sessions": await renderSessions(); break;
    case "episodic": await renderEpisodic(); break;
    case "health": await renderHealth(false); break;
    case "atoms": await renderAtoms(); break;
    case "projects": await renderProjects(); break;
    case "tests": break;
    case "vector": await renderVector(); break;
  }
  window.scrollTo(0, prevScroll);
}

// ─── Sessions Panel (existing logic) ───

async function fetchSessions() {
  try { const r = await fetch("/api/sessions"); return await r.json(); }
  catch { return []; }
}

async function sendSignal(sid, signal) {
  await fetch("/api/sessions/" + sid + "/signal", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ signal })
  });
  renderSessions();
}

async function deleteSession(sid) {
  if (!confirm("確定要刪除對話 " + sid.slice(0,8) + "?")) return;
  await fetch("/api/sessions/" + sid, { method: "DELETE" });
  renderSessions();
}

function badgeClass(phase) { return "badge badge-" + (phase || "init"); }

function clsBadge(c) {
  if (c === "[固]") return '<span class="kq-badge kq-badge-fixed">[固]</span>';
  if (c === "[觀]") return '<span class="kq-badge kq-badge-observe">[觀]</span>';
  return '<span class="kq-badge kq-badge-temp">[臨]</span>';
}

function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

async function renderSessions() {
  const sessions = await fetchSessions();
  const active = sessions.filter(s => !s.ended);
  const pending = sessions.filter(s => s.sync_pending && !s.ended);
  updateStats(sessions.length, active.length, pending.length);

  if (sessions.length === 0) {
    document.getElementById("sessionList").innerHTML = '<div class="empty">無進行中的對話。</div>';
    return;
  }

  const cards = await Promise.all(sessions.map(async (s) => {
    let detail;
    try { const r = await fetch("/api/sessions/" + s.session_id); detail = await r.json(); }
    catch { detail = {}; }
    const files = detail.modified_files || [];
    const kq = detail.knowledge_queue || [];
    const uniqueFiles = [...new Set(files.map(f => f.path))];
    let fileHtml = "";
    if (uniqueFiles.length > 0) {
      fileHtml = '<details><summary>修改檔案 (' + uniqueFiles.length + ')</summary><ul class="file-list">' +
        uniqueFiles.map(f => "<li>" + esc(f.split(/[\\\\/]/).pop()) + ' <span style="color:#484f58">' + esc(f) + "</span></li>").join("") + "</ul></details>";
    }
    let kqHtml = "";
    if (kq.length > 0) {
      kqHtml = '<details><summary>知識佇列 (' + kq.length + ')</summary><ul class="kq-list">' +
        kq.map(q => "<li>" + clsBadge(q.classification) + " " + esc((q.content||"").slice(0,80)) + "</li>").join("") + "</ul></details>";
    }
    return '<div class="card">' +
      '<div class="card-header"><span class="card-name">' + esc(s.name||"?") + '</span><span class="' + badgeClass(s.phase) + '">' + s.phase + (s.muted?" (已靜音)":"") + '</span></div>' +
      '<div class="card-meta"><span class="card-id">' + s.session_id.slice(0,8) + '</span> &middot; ' + esc(s.project||"?") + ' &middot; ' + s.age_minutes + ' 分鐘' + (s.ended?" &middot; 已結束":"") + '</div>' +
      '<div class="card-stats"><span>檔案：<strong>' + s.modified_files_count + '</strong></span><span>知識：<strong>' + s.knowledge_queue_count + '</strong></span><span>同步：<strong>' + (s.sync_pending?"待處理":"完成") + '</strong></span></div>' +
      (fileHtml||kqHtml ? '<div class="details">' + fileHtml + kqHtml + '</div>' : '') +
      '<div class="actions">' +
        '<button class="btn" onclick="sendSignal(\\'' + s.session_id + '\\',\\'sync_completed\\')">標記已同步</button>' +
        '<button class="btn" onclick="sendSignal(\\'' + s.session_id + '\\',\\'reset\\')">重置</button>' +
        (s.muted ? '' : '<button class="btn" onclick="sendSignal(\\'' + s.session_id + '\\',\\'mute\\')">靜音</button>') +
        '<button class="btn btn-danger" onclick="deleteSession(\\'' + s.session_id + '\\')">刪除</button>' +
      '</div></div>';
  }));
  document.getElementById("sessionList").innerHTML = cards.join("");
}

// ─── Stats Bar ───

function updateStats(total, active, pending, extra) {
  let html = '<div class="stat"><div class="stat-value">' + total + '</div><div class="stat-label">對話數</div></div>' +
    '<div class="stat"><div class="stat-value">' + active + '</div><div class="stat-label">進行中</div></div>' +
    '<div class="stat"><div class="stat-value">' + pending + '</div><div class="stat-label">待同步</div></div>';
  if (extra) html += extra;
  document.getElementById("statsBar").innerHTML = html;
}

// ─── Episodic Timeline ───

async function renderEpisodic() {
  const el = document.getElementById("episodicContent");
  try {
    const atoms = await (await fetch("/api/episodic")).json();
    if (!atoms.length) {
      el.innerHTML = '<div class="empty">無情境記憶紀錄。<br><span style="font-size:0.85em">情境記憶在對話結束時自動生成。</span></div>';
      return;
    }
    let html = '<div class="timeline">';
    for (const a of atoms) {
      const d = a.days_until_expiry;
      let dotCls = "ttl-green";
      let ttlLabel = d + "天剩餘";
      let ttlStyle = "background:#3fb95022;color:#3fb950";
      if (d !== null && d <= 0) { dotCls = "ttl-expired"; ttlLabel = "已過期"; ttlStyle = "background:#484f5822;color:#484f58"; }
      else if (d !== null && d <= 3) { dotCls = "ttl-critical"; ttlLabel = d + "天剩餘"; ttlStyle = "background:#f8514922;color:#f85149"; }
      else if (d !== null && d <= 7) { dotCls = "ttl-red"; ttlStyle = "background:#f8514922;color:#f85149"; }
      else if (d !== null && d <= 14) { dotCls = "ttl-yellow"; ttlStyle = "background:#d2a82622;color:#d2a826"; }

      const knLines = (a.knowledge_lines || []).slice(0, 5).map(l => "<li>" + esc(l) + "</li>").join("");
      const moreCount = (a.knowledge_lines||[]).length - 5;
      const hasMore = moreCount > 0;

      html += '<div class="timeline-item"><div class="timeline-dot ' + dotCls + '"></div><div class="timeline-card">' +
        '<div style="display:flex;justify-content:space-between;align-items:center">' +
          '<span class="timeline-date">' + esc(a.created || "?") + '</span>' +
          '<span class="timeline-ttl" style="' + ttlStyle + '">' + ttlLabel + '</span>' +
        '</div>' +
        '<div class="timeline-title">' + esc(a.title) + '</div>' +
        '<div style="font-size:0.78em;color:#8b949e">' + esc(a.triggers.join(", ")) + '</div>' +
        (knLines ? '<ul class="timeline-knowledge">' + knLines + (hasMore ? '<li style="color:#58a6ff">... +' + moreCount + ' 更多</li>' : '') + '</ul>' : '') +
        '<details><summary style="font-size:0.8em;color:#58a6ff;cursor:pointer;margin-top:6px">完整內容</summary>' +
          '<div class="timeline-full">' + esc(a.full_content) + '</div></details>' +
      '</div></div>';
    }
    html += '</div>';
    el.innerHTML = html;
  } catch (e) {
    el.innerHTML = '<div class="empty">載入情境記憶失敗：' + esc(e.message) + '</div>';
  }
}

// ─── Memory Health ───

let lastHealthData = null;

function toggleHealthInfo() {
  document.querySelectorAll('.health-info-row').forEach(r => {
    r.style.display = r.style.display === 'none' ? '' : 'none';
  });
}

async function renderHealth(force) {
  const el = document.getElementById("healthContent");
  try {
    const url = "/api/health" + (force ? "?force=1" : "");
    el.innerHTML = '<div class="empty"><span class="spinner"></span> 載入健康報告中...</div>';
    const data = await (await fetch(url)).json();
    if (data.error) { el.innerHTML = '<div class="empty">健康檢查失敗：' + esc(data.error) + '</div>'; return; }
    lastHealthData = data;

    const cc = data.confidence_counts || {};
    let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">' +
      '<span class="section-title">記憶健康報告</span>' +
      '<button class="btn btn-primary" onclick="renderHealth(true)">立即重整</button></div>';

    // Confidence counts
    html += '<div class="health-grid">';
    html += '<div class="health-stat"><div class="val" style="color:#3fb950">' + (cc["[固]"]||0) + '</div><div class="lbl">[固] 確定</div></div>';
    html += '<div class="health-stat"><div class="val" style="color:#d2a826">' + (cc["[觀]"]||0) + '</div><div class="lbl">[觀] 觀察</div></div>';
    html += '<div class="health-stat"><div class="val" style="color:#f0883e">' + (cc["[臨]"]||0) + '</div><div class="lbl">[臨] 臨時</div></div>';
    html += '<div class="health-stat"><div class="val">' + (data.total_atoms||0) + '</div><div class="lbl">原子總數</div></div>';
    html += '<div class="health-stat"><div class="val">' + (data.distant_count||0) + '</div><div class="lbl">疏遠區</div></div>';
    html += '</div>';

    // Issues — grouped by severity
    const issues = data.issues || [];
    const errCount = issues.filter(i => i.level === "error").length;
    const warnCount = issues.filter(i => i.level === "warning").length;
    const infoCount = issues.filter(i => i.level === "info").length;
    if (issues.length) {
      html += '<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">' +
        '<span class="section-title">問題</span>' +
        (errCount ? '<span style="color:#f85149;font-weight:bold">' + errCount + ' error</span>' : '') +
        (warnCount ? '<span style="color:#d2a826;font-weight:bold">' + warnCount + ' warning</span>' : '') +
        (infoCount ? '<span style="color:#8b949e">' + infoCount + ' info</span>' : '') +
        '<button class="btn" style="font-size:0.75em;padding:2px 8px" onclick="toggleHealthInfo()">顯示/隱藏 info</button>' +
        '</div>';
      html += '<table class="issue-table"><tr><th>等級</th><th>分類</th><th>檔案</th><th>訊息</th></tr>';
      for (const i of issues) {
        const hideClass = i.level === "info" ? ' class="health-info-row" style="display:none"' : '';
        html += '<tr' + hideClass + '><td class="level-' + i.level + '">' + i.level + '</td><td>' + esc(i.category) + '</td><td style="font-family:monospace;font-size:0.85em">' + esc(i.file) + '</td><td>' + esc(i.message) + '</td></tr>';
      }
      html += '</table>';
    } else {
      html += '<div style="color:#3fb950;margin-bottom:12px">✓ 無任何問題</div>';
    }

    // Promotions
    const promos = data.promotions || [];
    if (promos.length) {
      html += '<div class="section-title">晉升候選</div><ul class="suggest-list">';
      for (const p of promos) {
        html += '<li><span style="font-family:monospace">' + esc(p.file) + '</span> ' + p.current + ' <span class="suggest-arrow">&rarr;</span> ' + p.suggested + '<br><span style="color:#8b949e;font-size:0.82em">' + esc(p.reason) + '</span></li>';
      }
      html += '</ul>';
    }

    // Demotions
    const demos = data.demotions || [];
    if (demos.length) {
      html += '<div class="section-title">降級 / 過期警告</div><ul class="suggest-list">';
      for (const d of demos) {
        html += '<li><span style="font-family:monospace">' + esc(d.file) + '</span> ' + d.current + ' <span class="suggest-arrow">&rarr;</span> ' + d.suggested + '<br><span style="color:#8b949e;font-size:0.82em">' + esc(d.reason) + '</span></li>';
      }
      html += '</ul>';
    }

    // Reference integrity
    const brokenRefs = data.broken_refs || [];
    const missingRev = data.missing_reverse_refs || [];
    const staleAtoms = data.stale_atoms || [];
    html += '<div class="section-title">參照完整性</div>';
    if (!brokenRefs.length && !missingRev.length && !staleAtoms.length) {
      html += '<div style="color:#3fb950;margin-bottom:12px">✓ 所有參照完整、無過期 atom</div>';
    } else {
      if (brokenRefs.length) {
        html += '<div style="margin-bottom:8px"><strong style="color:#f85149">斷裂參照 (' + brokenRefs.length + ')</strong></div>';
        html += '<table class="issue-table"><tr><th>來源 Atom</th><th>指向（不存在）</th></tr>';
        for (const r of brokenRefs) { html += '<tr><td>' + esc(r.atom || "") + '</td><td style="color:#f85149">' + esc(r.missing_ref || "") + '</td></tr>'; }
        html += '</table>';
      }
      if (missingRev.length) {
        html += '<div style="margin-bottom:8px"><strong style="color:#d2a826">缺反向參照 (' + missingRev.length + ')</strong></div>';
        html += '<table class="issue-table"><tr><th>說明</th></tr>';
        for (const r of missingRev) { html += '<tr><td style="color:#d2a826">' + esc(r.direction || (r.atom_a + " → " + r.atom_b)) + '</td></tr>'; }
        html += '</table>';
      }
      if (staleAtoms.length) {
        html += '<div style="margin-bottom:8px"><strong style="color:#f0883e">過期 Atom (' + staleAtoms.length + ')</strong></div><ul>';
        for (const s of staleAtoms) { html += '<li>' + esc(s.name || s) + ' — Last-used: ' + esc(s.last_used || "?") + '</li>'; }
        html += '</ul>';
      }
    }

    // Audit stats
    const as = data.audit_stats || {};
    if (as.total_entries) {
      html += '<div class="section-title">審計摘要</div><div class="health-grid">';
      const ba = as.by_action || {};
      for (const [k, v] of Object.entries(ba)) {
        html += '<div class="health-stat"><div class="val">' + v + '</div><div class="lbl">' + k + '</div></div>';
      }
      html += '<div class="health-stat"><div class="val">' + as.total_entries + '</div><div class="lbl">總筆數</div></div>';
      html += '</div>';
    }

    html += '<div class="cache-info">掃描時間：' + esc(data.scan_date || "?") + ' | 層級：' + (data.layers||[]).join(", ") + '</div>';
    el.innerHTML = html;
  } catch (e) {
    el.innerHTML = '<div class="empty">載入健康資料失敗：' + esc(e.message) + '</div>';
  }
}

// ─── E2E Test Runner ───

async function startTestRun() {
  const btn = document.getElementById("runTestsBtn");
  const el = document.getElementById("testResults");
  btn.disabled = true;
  el.innerHTML = '<div style="text-align:center;padding:16px"><span class="spinner"></span> 測試執行中... <span id="testElapsed">0s</span></div>';
  const startTime = Date.now();
  const elapsedTimer = setInterval(() => {
    const s = ((Date.now() - startTime) / 1000).toFixed(0);
    const te = document.getElementById("testElapsed");
    if (te) te.textContent = s + "s";
  }, 500);

  try {
    const r = await fetch("/api/test-run", { method: "POST" });
    const d = await r.json();
    if (d.error) { el.innerHTML = '<div class="empty">' + esc(d.error) + '</div>'; btn.disabled = false; clearInterval(elapsedTimer); return; }
    testJobId = d.job_id;
    testPollTimer = setInterval(async () => {
      try {
        const sr = await fetch("/api/test-run/" + testJobId);
        const sd = await sr.json();
        if (sd.status !== "running") {
          clearInterval(testPollTimer);
          clearInterval(elapsedTimer);
          testPollTimer = null;
          btn.disabled = false;
          renderTestResults(sd);
        }
      } catch {}
    }, 2000);
  } catch (e) {
    el.innerHTML = '<div class="empty">測試執行失敗：' + esc(e.message) + '</div>';
    btn.disabled = false;
    clearInterval(elapsedTimer);
  }
}

function renderTestResults(job) {
  const el = document.getElementById("testResults");
  if (job.status === "error") {
    const err = job.result || {};
    el.innerHTML = '<div class="empty" style="color:#f85149">測試失敗：' + esc(err.error || "unknown") + (err.stderr ? '<br><pre style="text-align:left;font-size:0.8em;margin-top:8px">' + esc(err.stderr) + '</pre>' : '') + '</div>';
    return;
  }
  const r = job.result || {};
  const results = r.results || [];
  let html = '<div class="test-summary">' +
    '<span style="color:#3fb950;font-weight:600">通過：' + (r.passed||0) + '</span>' +
    '<span style="color:#f85149;font-weight:600">失敗：' + (r.failed||0) + '</span>' +
    '<span style="color:#8b949e">略過：' + (r.skipped||0) + '</span>' +
    '<span style="color:#8b949e">總計：' + (r.total||0) + '</span>' +
    '<span style="color:#8b949e">耗時：' + ((job.elapsed_ms||0)/1000).toFixed(1) + 's</span>' +
  '</div>';
  for (const t of results) {
    const cls = t.skipped ? "test-skip" : (t.passed ? "test-pass" : "test-fail");
    const icon = t.skipped ? "&#9711;" : (t.passed ? "&#10003;" : "&#10007;");
    const iconColor = t.skipped ? "#8b949e" : (t.passed ? "#3fb950" : "#f85149");
    html += '<div class="test-card ' + cls + '">' +
      '<span class="test-icon" style="color:' + iconColor + '">' + icon + '</span>' +
      '<span class="test-name">' + esc(t.name) + '</span>' +
      '<span class="test-duration">' + (t.duration_ms||0).toFixed(0) + 'ms</span>' +
    '</div>';
    if (t.message) {
      html += '<div style="padding:0 14px 6px 48px"><span class="test-msg">' + esc(t.message) + '</span></div>';
    }
  }
  el.innerHTML = html;
}

// ─── Vector Status ───

async function renderVector() {
  const el = document.getElementById("vectorContent");
  try {
    const r = await fetch("/api/vector-status");
    const d = await r.json();
    if (d.error) {
      el.innerHTML = '<div class="card" style="text-align:center;padding:24px"><span class="status-dot status-offline"></span><strong style="color:#f85149">離線</strong><br><span style="color:#8b949e;font-size:0.85em">' + esc(d.error) + '</span></div>';
      return;
    }
    const svc = d.service || {};
    const idx = d.index || {};
    const cfg = d.config || {};
    const job = d.index_job || {};
    const upH = Math.floor((svc.uptime_seconds||0)/3600);
    const upM = Math.floor(((svc.uptime_seconds||0)%3600)/60);

    let html = '<div style="margin-bottom:12px"><span class="status-dot status-online"></span><strong style="color:#3fb950">線上</strong> <span style="color:#8b949e;font-size:0.85em">(' + esc(svc.embedder||"?") + ' on port ' + (svc.port||3849) + ')</span></div>';
    html += '<div class="vec-grid">';

    // Service info
    html += '<div class="vec-section"><h3>服務</h3>';
    html += '<div class="vec-row"><span class="k">運行時間</span><span class="v">' + upH + 'h ' + upM + 'm</span></div>';
    html += '<div class="vec-row"><span class="k">請求次數</span><span class="v">' + (svc.requests_served||0) + '</span></div>';
    html += '<div class="vec-row"><span class="k">嵌入模型</span><span class="v">' + esc(svc.embedder||"?") + '</span></div>';
    html += '</div>';

    // Index info
    html += '<div class="vec-section"><h3>索引</h3>';
    html += '<div class="vec-row"><span class="k">總區塊數</span><span class="v">' + (idx.total_chunks||0) + '</span></div>';
    html += '<div class="vec-row"><span class="k">獨立原子</span><span class="v">' + (idx.unique_atoms||0) + '</span></div>';
    html += '<div class="vec-row"><span class="k">層級數</span><span class="v">' + (idx.layers||[]).length + '</span></div>';
    html += '</div>';

    // Config
    html += '<div class="vec-section"><h3>設定</h3>';
    html += '<div class="vec-row"><span class="k">後端</span><span class="v">' + esc(cfg.embedding_backend||"?") + '</span></div>';
    html += '<div class="vec-row"><span class="k">模型</span><span class="v">' + esc(cfg.embedding_model||"?") + '</span></div>';
    html += '<div class="vec-row"><span class="k">搜尋上限</span><span class="v">' + (cfg.search_top_k||5) + '</span></div>';
    html += '<div class="vec-row"><span class="k">最低分數</span><span class="v">' + (cfg.search_min_score||0.5) + '</span></div>';
    html += '</div>';

    // Index job
    html += '<div class="vec-section"><h3>最近索引任務</h3>';
    if (job.running) {
      html += '<div style="color:#d2a826"><span class="spinner"></span> 索引建立中...</div>';
    } else if (job.result) {
      const jr = job.result;
      html += '<div class="vec-row"><span class="k">發現原子</span><span class="v">' + (jr.atoms_found||0) + '</span></div>';
      html += '<div class="vec-row"><span class="k">已索引原子</span><span class="v">' + (jr.atoms_indexed||0) + '</span></div>';
      html += '<div class="vec-row"><span class="k">區塊數</span><span class="v">' + (jr.total_chunks||0) + '</span></div>';
      html += '<div class="vec-row"><span class="k">耗時</span><span class="v">' + ((jr.elapsed_seconds||0)).toFixed(1) + 's</span></div>';
      html += '<div class="vec-row"><span class="k">類型</span><span class="v">' + (jr.incremental?"增量":"全量") + '</span></div>';
      if (job.finished_at) {
        const fin = new Date(job.finished_at * 1000);
        html += '<div class="vec-row"><span class="k">完成時間</span><span class="v">' + fin.toLocaleString() + '</span></div>';
      }
    } else {
      html += '<div style="color:#8b949e">無近期索引紀錄</div>';
    }
    html += '</div>';

    html += '</div>';
    el.innerHTML = html;
  } catch (e) {
    el.innerHTML = '<div class="empty">載入向量服務狀態失敗：' + esc(e.message) + '</div>';
  }
}

// ─── Projects Panel ───

async function renderProjects() {
  const el = document.getElementById("projectsContent");
  try {
    const projects = await (await fetch("/api/projects")).json();
    if (!projects.length) {
      el.innerHTML = '<div class="empty">project-registry.json 中無已知專案。</div>';
      return;
    }
    let html = '<p style="color:#8b949e;font-size:0.85em;margin-bottom:12px">來源：project-registry.json（共 ' + projects.length + ' 個專案，動態更新）</p>';
    html += '<table class="proj-table"><thead><tr>';
    html += '<th>Slug / 別名</th><th>根路徑</th><th>記憶層</th><th>Atoms</th><th>Failures</th><th>Episodic</th><th>最後活動</th><th>操作</th>';
    html += '</tr></thead><tbody>';
    for (const p of projects) {
      const memBadge = p.has_memory
        ? '<span class="proj-badge-mem">✓ .claude/memory</span>'
        : '<span class="proj-badge-nomem">未初始化</span>';
      const aliases = (p.aliases || []).length
        ? '<div class="proj-alias">' + p.aliases.map(a => esc(a)).join(', ') + '</div>'
        : '';
      const filterBtn = p.has_memory
        ? '<button class="proj-filter-btn" onclick="filterAtomsByProject(&#39;project:' + p.slug + '&#39;)">查看 Atoms</button>'
        : '';
      html += '<tr>';
      html += '<td><strong>' + esc(p.slug) + '</strong>' + aliases + '</td>';
      html += '<td><span class="proj-root">' + esc(p.root) + '</span></td>';
      html += '<td>' + memBadge + '</td>';
      html += '<td>' + (p.atom_count || 0) + '</td>';
      html += '<td>' + (p.failure_count || 0) + '</td>';
      html += '<td>' + (p.episodic_count || 0) + '</td>';
      html += '<td>' + esc(p.last_seen || '-') + '</td>';
      html += '<td>' + filterBtn + '</td>';
      html += '</tr>';
    }
    html += '</tbody></table>';
    el.innerHTML = html;
  } catch (e) {
    el.innerHTML = '<div class="empty">載入專案清單失敗：' + esc(e.message) + '</div>';
  }
}

function filterAtomsByProject(layerPrefix) {
  // Switch to atoms tab and filter by project layer
  currentTab = "atoms";
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelector('[data-tab="atoms"]').classList.add("active");
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.getElementById("panelAtoms").classList.add("active");
  renderAtoms().then(() => {
    const filterInput = document.getElementById("atomFilter");
    if (filterInput) {
      filterInput.value = layerPrefix;
      filterInput.dispatchEvent(new Event("input"));
    }
  });
}

// ─── Atoms Browser ───

let atomsData = [];
const expandedAtoms = new Set();  // track expanded detail rows across refreshes

async function renderAtoms() {
  const el = document.getElementById("atomsContent");
  const prevFilter = document.getElementById("atomFilter");
  const savedFilter = prevFilter ? prevFilter.value : "";
  try {
    atomsData = await (await fetch("/api/atoms")).json();
    if (!atomsData.length) {
      el.innerHTML = '<div class="empty">無原子記憶。</div>';
      return;
    }
    renderAtomsTable(atomsData);
    if (savedFilter) {
      const fi = document.getElementById("atomFilter");
      if (fi) { fi.value = savedFilter; filterAtoms(savedFilter); }
    } else if (atomSortKey) {
      reapplySort();
    }
  } catch (e) {
    el.innerHTML = '<div class="empty">載入原子記憶失敗：' + esc(e.message) + '</div>';
  }
}

function renderAtomsTable(atoms) {
  const el = document.getElementById("atomsContent");
  const confCounts = {};
  for (const a of atoms) { confCounts[a.confidence] = (confCounts[a.confidence]||0) + 1; }

  let html = '<div class="atom-stats">';
  html += '<div class="stat"><div class="stat-value">' + atoms.length + '</div><div class="stat-label">原子總數</div></div>';
  if (confCounts["[固]"]) html += '<div class="stat"><div class="stat-value" style="color:#3fb950">' + confCounts["[固]"] + '</div><div class="stat-label">[固] 確定</div></div>';
  if (confCounts["[觀]"]) html += '<div class="stat"><div class="stat-value" style="color:#d2a826">' + confCounts["[觀]"] + '</div><div class="stat-label">[觀] 觀察</div></div>';
  if (confCounts["[臨]"]) html += '<div class="stat"><div class="stat-value" style="color:#f0883e">' + confCounts["[臨]"] + '</div><div class="stat-label">[臨] 臨時</div></div>';
  html += '</div>';

  html += '<input id="atomFilter" class="atom-filter" type="text" placeholder="搜尋原子名稱、觸發詞..." oninput="filterAtoms(this.value)">';

  html += '<table class="atom-table" id="atomTable">';
  html += '<thead><tr>' +
    '<th onclick="sortAtoms(\\'name\\')">名稱 &#8597;</th>' +
    '<th onclick="sortAtoms(\\'layer\\')">層級 &#8597;</th>' +
    '<th onclick="sortAtoms(\\'confidence\\')">信心 &#8597;</th>' +
    '<th onclick="sortAtoms(\\'confirmations\\')">確認數 &#8597;</th>' +
    '<th onclick="sortAtoms(\\'last_used\\')">最後使用 &#8597;</th>' +
    '<th onclick="sortAtoms(\\'knowledge_count\\')">知識數 &#8597;</th>' +
    '<th>行數</th>' +
  '</tr></thead>';
  html += '<tbody id="atomTableBody">';
  html += buildAtomRows(atoms);
  html += '</tbody></table>';
  el.innerHTML = html;
}

function buildAtomRows(atoms) {
  let html = '';
  for (const a of atoms) {
    const confClass = a.confidence === "[固]" ? "conf-fixed" : a.confidence === "[觀]" ? "conf-observe" : "conf-temp";
    const daysAgo = a.days_since_used != null ? a.days_since_used + ' 天前' : '-';
    html += '<tr data-name="' + esc(a.name) + '">' +
      '<td><span class="atom-name" onclick="toggleAtomDetail(\\'' + esc(a.name) + '\\')">' + esc(a.name) + '</span></td>' +
      '<td><span class="atom-layer">' + esc(a.layer) + '</span></td>' +
      '<td><span class="atom-conf ' + confClass + '">' + esc(a.confidence||"-") + '</span></td>' +
      '<td>' + (a.confirmations||0) + '</td>' +
      '<td title="' + esc(a.last_used||"") + '">' + daysAgo + '</td>' +
      '<td>' + (a.knowledge_count||'-') + '</td>' +
      '<td>' + (a.line_count||'-') + '</td>' +
    '</tr>';
    const detailVis = expandedAtoms.has(a.name) ? '' : 'none';
    html += '<tr id="detail-' + esc(a.name) + '" style="display:' + detailVis + '"><td colspan="7"><div class="atom-detail">' + esc(a.content||"") + '</div></td></tr>';
  }
  return html;
}

function toggleAtomDetail(name) {
  const row = document.getElementById("detail-" + name);
  if (!row) return;
  if (row.style.display === "none") {
    row.style.display = "";
    expandedAtoms.add(name);
  } else {
    row.style.display = "none";
    expandedAtoms.delete(name);
  }
}

let atomSortKey = "last_used";
let atomSortAsc = false;

function applySortToBody(data) {
  const sorted = [...data].sort((a, b) => {
    let va = a[atomSortKey] ?? "", vb = b[atomSortKey] ?? "";
    if (typeof va === "number" && typeof vb === "number") return atomSortAsc ? va - vb : vb - va;
    va = String(va); vb = String(vb);
    return atomSortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
  });
  document.getElementById("atomTableBody").innerHTML = buildAtomRows(sorted);
}

function reapplySort() { applySortToBody(atomsData); }

function sortAtoms(key) {
  if (atomSortKey === key) atomSortAsc = !atomSortAsc;
  else { atomSortKey = key; atomSortAsc = key === "name"; }
  applySortToBody(atomsData);
}

function filterAtoms(query) {
  const q = query.toLowerCase();
  const filtered = atomsData.filter(a => {
    if (a.name.toLowerCase().includes(q)) return true;
    if ((a.triggers||[]).some(t => t.toLowerCase().includes(q))) return true;
    if ((a.related||[]).some(r => r.toLowerCase().includes(q))) return true;
    if ((a.layer||"").toLowerCase().includes(q)) return true;
    return false;
  });
  applySortToBody(filtered);
}

// ─── Auto Refresh ───

function startAutoRefresh() {
  clearInterval(refreshTimer);
  if (document.getElementById("autoRefresh").checked) {
    refreshTimer = setInterval(refreshCurrentTab, 5000);
  }
}

document.getElementById("autoRefresh").addEventListener("change", startAutoRefresh);
renderSessions();
startAutoRefresh();
</script>
</body>
</html>`;

const httpServer = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${DASHBOARD_PORT}`);
  const pathname = url.pathname;

  // CORS for local dev
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  // Dashboard
  if (pathname === "/" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    return res.end(DASHBOARD_HTML);
  }

  // API: list sessions
  if (pathname === "/api/sessions" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(listAllSessions()));
  }

  // API: get/delete single session
  const sessionMatch = pathname.match(/^\/api\/sessions\/([^/]+)$/);
  if (sessionMatch) {
    const sid = resolveSessionId(sessionMatch[1]) || sessionMatch[1];
    if (req.method === "GET") {
      const state = readState(sid);
      if (!state) {
        res.writeHead(404, { "Content-Type": "application/json" });
        return res.end(JSON.stringify({ error: "not found" }));
      }
      res.writeHead(200, { "Content-Type": "application/json" });
      return res.end(JSON.stringify(state));
    }
    if (req.method === "DELETE") {
      const ok = deleteState(sid);
      res.writeHead(ok ? 200 : 404, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ ok, deleted: `state-${sid}.json` }));
    }
  }

  // API: send signal
  const signalMatch = pathname.match(/^\/api\/sessions\/([^/]+)\/signal$/);
  if (signalMatch && req.method === "POST") {
    const sid = resolveSessionId(signalMatch[1]) || signalMatch[1];
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        const { signal } = JSON.parse(body);
        const state = readState(sid);
        if (!state) {
          res.writeHead(404, { "Content-Type": "application/json" });
          return res.end(JSON.stringify({ error: "not found" }));
        }
        switch (signal) {
          case "sync_started":
            state.phase = "syncing";
            break;
          case "sync_completed":
            state.phase = "done";
            state.sync_pending = false;
            state.knowledge_queue = [];
            state.modified_files = [];
            state.ended_at = new Date().toISOString();
            break;
          case "reset":
            state.phase = "working";
            state.sync_pending = false;
            state.stop_blocked_count = 0;
            state.remind_count = 0;
            state.muted = false;
            break;
          case "mute":
            state.muted = true;
            break;
        }
        writeState(sid, state);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: true, state }));
      } catch {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "invalid body" }));
      }
    });
    return;
  }

  // v2.1 API routes
  if (pathname === "/api/episodic" && req.method === "GET") {
    return apiEpisodic(req, res);
  }
  if (pathname === "/api/health" && req.method === "GET") {
    const force = url.searchParams.get("force") === "1";
    return apiHealth(req, res, force);
  }
  if (pathname === "/api/test-run" && req.method === "POST") {
    return apiTestRunStart(req, res);
  }
  const testJobMatch = pathname.match(/^\/api\/test-run\/([^/]+)$/);
  if (testJobMatch && req.method === "GET") {
    return apiTestRunStatus(req, res, testJobMatch[1]);
  }
  if (pathname === "/api/vector-status" && req.method === "GET") {
    return apiVectorStatus(req, res);
  }
  if (pathname === "/api/knowledge-queue" && req.method === "GET") {
    return apiKnowledgeQueue(req, res);
  }
  if (pathname === "/api/atoms" && req.method === "GET") {
    return apiAtoms(req, res);
  }
  if (pathname === "/api/projects" && req.method === "GET") {
    return apiProjects(req, res);
  }

  res.writeHead(404);
  res.end("Not found");
});

// ─── Dashboard port binding with recovery heartbeat ─────────────────────────
// When multiple Claude Code instances exist, only one binds port 3848.
// If that instance dies, a surviving instance must reclaim the port.
const HEARTBEAT_INTERVAL_MS = 15000;
let dashboardHeartbeat = null;

function tryBindDashboard() {
  if (httpServer.listening) return;

  const probe = http.request(
    { hostname: "127.0.0.1", port: DASHBOARD_PORT, path: "/", method: "HEAD", timeout: 500 },
    () => {
      // Port occupied by another instance — keep heartbeat running
      probe.destroy();
    }
  );

  probe.on("error", () => {
    // Connection refused → port is free, attempt to bind
    if (httpServer.listening) return;
    httpServer.listen(DASHBOARD_PORT, "127.0.0.1", () => {
      process.stderr.write(`[workflow-guardian] Dashboard: http://127.0.0.1:${DASHBOARD_PORT}\n`);
      if (dashboardHeartbeat) {
        clearInterval(dashboardHeartbeat);
        dashboardHeartbeat = null;
      }
    });
  });

  probe.on("timeout", () => probe.destroy());
  probe.end();
}

httpServer.on("error", (err) => {
  if (err.code === "EADDRINUSE") {
    process.stderr.write(`[workflow-guardian] Dashboard port ${DASHBOARD_PORT} taken (race), will retry.\n`);
    if (!dashboardHeartbeat) {
      dashboardHeartbeat = setInterval(tryBindDashboard, HEARTBEAT_INTERVAL_MS);
      dashboardHeartbeat.unref();
    }
  } else {
    process.stderr.write(`[workflow-guardian] Dashboard failed: ${err.message}\n`);
  }
});

tryBindDashboard();
setImmediate(() => {
  if (!httpServer.listening && !dashboardHeartbeat) {
    dashboardHeartbeat = setInterval(tryBindDashboard, HEARTBEAT_INTERVAL_MS);
    dashboardHeartbeat.unref();
  }
});

// Keep MCP alive
process.stdin.resume();
