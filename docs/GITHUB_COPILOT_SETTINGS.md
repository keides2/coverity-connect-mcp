# GitHub Copilot MCP Server 設定方法

## 確実に動作させるための設定

### VS Code の settings.json に以下を追加してください：

```json
{
  "github.copilot.chat.experimental.mcpServers": {
    "coverity-connect": {
      "command": "python",
      "args": ["-m", "src.coverity_mcp_server"],
      "cwd": "C:\\path\\to\\your\\coverity-connect-mcp",
      "env": {
        "COVERITY_HOST": "https://your-coverity-server.com",
        "COVERITY_PORT": "443",
        "COVERITY_SSL": "true",
        "COVAUTHUSER": "your_username",
        "COVAUTHKEY": "your_password_or_token",
        "PROXY_HOST": "your-proxy-server.com",
        "PROXY_PORT": "3128",
        "LOG_LEVEL": "INFO",
        "SSL_VERIFY": "false",
        "TIMEOUT_SECONDS": "30"
      }
    }
  }
}
```

## settings.json の場所

- Windows: `%APPDATA%\Code\User\settings.json`
- または VS Code で: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"

## 重要なポイント

1. **COVERITY_HOST**: 実際のCoverityサーバーURLに置き換えてください（`https://` プロトコルを含める）
2. **COVAUTHUSER**: 実際のCoverityユーザー名に置き換えてください
3. **COVAUTHKEY**: 実際のCoverityパスワードまたはトークンに置き換えてください
4. **cwd**: プロジェクトの実際のパスに置き換えてください
5. **プロキシ設定**: 必要に応じて `PROXY_HOST` と `PROXY_PORT` を実際の値に設定してください

⚠️ **セキュリティ注意**: このファイルを編集する際は、実際の認証情報をGitHubにプッシュしないよう注意してください。

## 再起動手順

1. settings.json を保存
2. VS Code を完全終了
3. VS Code を再起動
4. GitHub Copilot Chat で接続テスト
