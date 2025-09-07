# Coverity Connect MCP Server 公開・接続手順レポート

## 概要

本レポートでは、独自に開発した **Coverity Connect MCP Server** を  
**HTTPブリッジ + ngrok** を利用して外部公開し、  
Copilot Studio から利用可能にするまでの手順を整理する。

---

## 手順の流れ

### 1. MCP ブリッジの準備

- MCP サーバーは標準で **stdio 通信**に対応している。
- 外部システム（Copilot Studioなど）から利用するために  
  **Node.js + Express** を用いて HTTP ブリッジを作成した。

ブリッジの役割：

- `/health` → `initialize` + `tools/list`
- `/tools` → `tools/list`
- `/tools/{name}/invoke` → `tools/call`

### 2. ブリッジ環境のセットアップ

- Bridge 実行用 PowerShell #1 で実行

作業ディレクトリ：`C:\Users\HP\mcp-servers\coverity-connect-mcp\mcp-bridge`

実施内容:

```powershell
# 依存ライブラリをインストール
npm init -y
npm i express body-parser uuid
```

環境変数設定例:

```powershell
$env:BRIDGE_TOKEN = "dev-token"
$env:MCP_CMD      = "python"
$env:PYTHONPATH   = "C:\Users\HP\mcp-servers\coverity-connect-mcp\src"
$env:MCP_ARGS     = "-m coverity_mcp_server"
$env:PORT         = "8080"
```

ブリッジ起動:

```powershell
node .\bridge.js
```

ログに `[bridge] listening on :8080` が表示されれば成功。

### 3. ローカルでの動作確認

- テスト実行用 PowerShell #2 で実行

`curl.exe` または `Invoke-RestMethod` を使用し、  
`/health` や `/tools` でツール一覧を取得できることを確認。

例:

```powershell
curl.exe -H "Authorization: Bearer dev-token" http://localhost:8080/health
```

返却されたツール一覧（抜粋）:

- search_defects  
- get_defect_details  
- list_projects  
- list_streams  
- get_project_summary  
- list_users  
- get_user_details  
- get_user_roles

さらに `/tools/<name>/invoke` で呼び出しが可能。
例: プロジェクト一覧を取得

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8080/tools/list_projects/invoke" `
  -Headers @{ Authorization = "Bearer dev-token" } `
  -ContentType "application/json" `
  -Body (@{ args = @{} } | ConvertTo-Json)
```

### 4. ngrok を利用した外部公開

- ngrok セッション用 PowerShell #3 で実行

1. ngrok をインストールし、アカウント登録・Authtoken を設定。

   ```powershell
   ngrok config add-authtoken <YOUR_AUTHTOKEN>
   ```

2. トンネルを作成。

   ```powershell
   ngrok http http://localhost:8080
   ```

3. 表示例:

   ```text
   Forwarding https://2bd93cac1f61.ngrok-free.app -> http://localhost:8080
   ```

この `https://2bd93cac1f61.ngrok-free.app` が外部から利用できるエンドポイントになる。

### 5. 外部経由での動作確認

- テスト実行用 PowerShell #2 で実行

```powershell
curl.exe -H "Authorization: Bearer dev-token" https://2bd93cac1f61.ngrok-free.app/health
```

結果：ローカル同様にツール一覧が取得でき、外部からも正常に利用可能であることを確認。

---

## 次のステップ

1. **Copilot Studio に MCP 登録**

- エージェント > ツール > 「Model Context Protocol (MCP)」を選択
- エンドポイントに ngrok の URL を指定
- 認証ヘッダに `Authorization: Bearer dev-token`
- 検出されたツールを有効化し保存

1. **Teams でエージェントを利用**

- Publish したエージェントを Teams に展開
- チャットで「プロジェクト一覧を表示して」などと入力すると  
  MCP 経由で Coverity Connect にアクセス可能となる。

---

## 注意点

- ngrok Free プランでは URL が再起動ごとに変わるため、  
Copilot Studio 側のエンドポイント設定を更新する必要がある。  
- 運用環境では固定URLを持つ **Azure App Service** 等で公開することが望ましい。  
- セキュリティを考慮すると、Bearer トークン固定ではなく  
Azure Entra ID 認証を導入するのが理想。

---

## まとめ

本手順により、Coverity Connect MCP サーバーを  
**ローカル環境 → HTTPブリッジ → ngrok公開 → Copilot Studio → Teams** の流れで  
実際に利用可能にできることを確認した。  

今後は Azure 環境への常設配置と認証強化を進めれば、協力会社を含む利用者が  
安全にアクセスできる仕組みを整備できる。

---
2025/09/06 keides2 初版
