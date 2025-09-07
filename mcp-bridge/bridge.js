// bridge.js (initialize + notifications/initialized 対応版)
const express = require("express");
const bodyParser = require("body-parser");
const { spawn } = require("child_process");
const { v4: uuid } = require("uuid");

const PORT = process.env.PORT || 8080;
const BRIDGE_TOKEN = process.env.BRIDGE_TOKEN || "change-me";
const MCP_CMD = process.env.MCP_CMD || "node";
const MCP_ARGS = (process.env.MCP_ARGS || "coverity-mcp-server.js").split(" ");

class JsonRpcViaStdio {
  constructor(cmd, args) {
    this.proc = spawn(cmd, args, { stdio: ["pipe", "pipe", "pipe"] });
    this.buf = "";
    this.pending = new Map();
    this.initialized = false;
    this.initPromise = null;

    this.proc.stdout.setEncoding("utf8");
    this.proc.stdout.on("data", (chunk) => this._onData(chunk));
    this.proc.stderr.on("data", (d) => console.error("[MCP stderr]", d.toString()));
    this.proc.on("exit", (code) => {
      console.error(`[MCP exited] code=${code}`);
      for (const [, { reject }] of this.pending) reject(new Error("MCP exited"));
      this.pending.clear();
      this.initialized = false;
      this.initPromise = null;
    });
  }

  _onData(chunk) {
    this.buf += chunk;
    let idx;
    while ((idx = this.buf.indexOf("\n")) >= 0) {
      const line = this.buf.slice(0, idx).trim();
      this.buf = this.buf.slice(idx + 1);
      if (!line) continue;
      try {
        const msg = JSON.parse(line);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message || "MCP error"));
          else resolve(msg.result);
        }
      } catch (e) {
        console.error("JSON parse error:", e, "input=", line);
      }
    }
  }

  call(method, params, timeoutMs = 15000) {
    const id = uuid();
    const payload = { jsonrpc: "2.0", id, method, params };
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.proc.stdin.write(JSON.stringify(payload) + "\n", "utf8");
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error("timeout"));
        }
      }, timeoutMs);
    });
  }

  // JSON-RPC Notification（id無し）
  notify(method, params) {
    const payload = { jsonrpc: "2.0", method, params };
    this.proc.stdin.write(JSON.stringify(payload) + "\n", "utf8");
  }

  async ensureInitialized() {
    if (this.initialized) return;
    if (this.initPromise) return this.initPromise;

    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

    this.initPromise = (async () => {
      // 1) initialize
      await this.call("initialize", {
        protocolVersion: "2025-06-18",
        capabilities: {},
        clientInfo: { name: "copilot-bridge", version: "1.0.0" },
      });

      // 2) notifications/initialized（多くの実装がこれを期待）
      this.notify("notifications/initialized", {});

      // 3) サーバー側が内部初期化を完了するのを少し待つ
      await sleep(300);

      this.initialized = true;
    })();

    return this.initPromise;
  }
}

const app = express();
app.use(bodyParser.json({ limit: "1mb" }));

// 認証（PoC最小）
app.use((req, res, next) => {
  const hdr = req.headers.authorization || "";
  if (!hdr.startsWith("Bearer ") || hdr.slice(7) !== BRIDGE_TOKEN) {
    return res.status(401).json({ error: "unauthorized" });
  }
  next();
});

const mcp = new JsonRpcViaStdio(MCP_CMD, MCP_ARGS);

// health: initialize → tools/list
app.get("/health", async (_req, res) => {
  try {
    await mcp.ensureInitialized();
    const tools = await mcp.call("tools/list", {});
    res.json({ ok: true, tools });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

// tools: initialize → tools/list
app.get("/tools", async (_req, res) => {
  try {
    await mcp.ensureInitialized();
    const tools = await mcp.call("tools/list", {});
    res.json(tools);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// invoke: initialize → tools/call
app.post("/tools/:name/invoke", async (req, res) => {
  try {
    await mcp.ensureInitialized();
    const result = await mcp.call("tools/call", {
      name: req.params.name,
      arguments: req.body?.args || {},
    });
    res.json({ ok: true, result });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.listen(PORT, () => {
  console.log(`[bridge] listening on :${PORT}`);
  console.log(`[bridge] auth header: Authorization: Bearer <BRIDGE_TOKEN>`);
});
