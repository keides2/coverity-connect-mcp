# ============================
# Windows PowerShell 用セットアップ
# ============================

# --- 0) Node.js 18+ が未導入なら（管理者PowerShellで実行） ---
# winget が使える環境なら以下でLTS版を導入（既にある場合はスキップ）
# winget install -e --id OpenJS.NodeJS.LTS

# --- 1) 作業フォルダ作成 ---
$proj = "$HOME\mcp-bridge-poc"
New-Item -ItemType Directory -Force -Path $proj | Out-Null
Set-Location $proj

# --- 2) Node プロジェクト作成＆依存導入 ---
npm init -y | Out-Null
npm i express body-parser uuid | Out-Null

# --- 3) 最小HTTPブリッジ（bridge.js）を作成 ---
@'
const express = require("express");
const bodyParser = require("body-parser");
const { spawn } = require("child_process");
const { v4: uuid } = require("uuid");

const PORT = process.env.PORT || 8080;
const BRIDGE_TOKEN = process.env.BRIDGE_TOKEN || "change-me";
const MCP_CMD = process.env.MCP_CMD || "node";
// 例: coverity-connect-mcp のエントリに合わせて変更してください
const MCP_ARGS = (process.env.MCP_ARGS || "coverity-mcp-server.js").split(" ");

// ---- stdio JSON-RPC client (JSON per line) ----
class JsonRpcViaStdio {
  constructor(cmd, args) {
    this.proc = spawn(cmd, args, { stdio: ["pipe", "pipe", "pipe"] });
    this.buf = "";
    this.pending = new Map();

    this.proc.stdout.setEncoding("utf8");
    this.proc.stdout.on("data", (chunk) => this._onData(chunk));
    this.proc.stderr.on("data", (d) => console.error("[MCP stderr]", d.toString()));
    this.proc.on("exit", (code) => {
      console.error(`[MCP exited] code=${code}`);
      for (const [, { reject }] of this.pending) reject(new Error("MCP exited"));
      this.pending.clear();
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
}

const app = express();
app.use(bodyParser.json({ limit: "1mb" }));

// Bearer 認証（PoC最小）
app.use((req, res, next) => {
  const hdr = req.headers.authorization || "";
  if (!hdr.startsWith("Bearer ") || hdr.slice(7) !== BRIDGE_TOKEN) {
    return res.status(401).json({ error: "unauthorized" });
  }
  next();
});

const mcp = new JsonRpcViaStdio(MCP_CMD, MCP_ARGS);

// 生存確認 + tools/list
app.get("/health", async (_req, res) => {
  try {
    const tools = await mcp.call("tools/list", {});
    res.json({ ok: true, tools });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

// ツール一覧
app.get("/tools", async (_req, res) => {
  try {
    const tools = await mcp.call("tools/list", {});
    res.json(tools);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ツール実行: POST /tools/{name}/invoke  body: { args: {...} }
app.post("/tools/:name/invoke", async (req, res) => {
  try {
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
'@ | Set-Content -Path "$proj\bridge.js" -Encoding UTF8

# --- 4) 実行用の環境変数（PowerShellセッション内のみ有効）---
# トークンはお好みで
$env:BRIDGE_TOKEN = "dev-token"

# coverity-connect-mcp の実行エントリに合わせて指定
# 例: Node版なら
$env:MCP_CMD  = "node"
$env:MCP_ARGS = "path\to\coverity-connect-mcp-entry.js"

# 例: Python版なら
# $env:MCP_CMD  = "python"
# $env:MCP_ARGS = "path\to\coverity_mcp_server\__main__.py"

$env:PORT = "8080"

# --- 5) ブリッジ起動 ---
node .\bridge.js

# ===== 以降は別のPowerShellで実施 =====
# --- 6-A) ngrok を使う場合 ---
# 1) https://ngrok.com/download から Windows 用を導入し、authtoken を設定
#    ngrok config add-authtoken <YOUR_NGROK_TOKEN>
# 2) 公開
#    ngrok http http://localhost:8080
# 3) 表示された https://*.ngrok.io をメモ

# --- 6-B) Dev Tunnels を使う場合（VS/DevTunnels導入済なら） ---
# devtunnel host -p 8080 --allow-anonymous
# 表示された Public URL をメモ

# --- 7) 疎通テスト（<PUBLIC_HTTPS> は ngrok などのURLに置換） ---
# health
# curl.exe -H "Authorization: Bearer dev-token" "<PUBLIC_HTTPS>/health"
# tools
# curl.exe -H "Authorization: Bearer dev-token" "<PUBLIC_HTTPS>/tools"
# invoke例
# $body = '{"args":{"project":"demo","id":"123"}}'
# curl.exe -H "Authorization: Bearer dev-token" -H "Content-Type: application/json" -d $body `
#   "<PUBLIC_HTTPS>/tools/get_issue/invoke"

# --- 8) Copilot Studio 設定 ---
# エージェント > ツール > Model Context Protocol > エンドポイント = <PUBLIC_HTTPS>
# 認証ヘッダ = "Authorization: Bearer dev-token"
# ツールを有効化 → Publish → Teams で確認
