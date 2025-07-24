# Visual Studio Code での MCP サーバー設定手順

## 概要

Model Context Protocol (MCP) サーバーを Visual Studio Code に組み込み、GitHub Copilot の Agent Mode で外部ツールやサービスと連携する方法を説明します。

## 前提条件

- **Visual Studio Code 1.102 以降**
- **GitHub Copilot 拡張機能**がインストール済み
- **GitHub アカウント**でサインイン済み
- **Node.js** (MCPサーバーがNode.js製の場合)

## 1. Agent Mode の有効化

### 1.1 GitHub Copilot Chat の設定

1. **Chat ビューを開く**
   - ショートカット: `Ctrl+Alt+I` (Windows/Linux) または `⌃⌘I` (Mac)
   - またはサイドバーの「Chat」アイコンをクリック

2. **GitHub にサインイン**
   - GitHub Copilot の機能を使用するために必要

3. **Agent Mode を有効化**
   - 設定で `chat.agent.enabled` を `true` に設定
   - または設定 UI で「Chat: Agent Enabled」を有効化

4. **Agent モードに切り替え**
   - Chat ビューのモード選択ドロップダウンで「Agent」を選択

## 2. MCP サーバーの追加方法

### 方法1: コマンドパレット経由（推奨）

1. **コマンドパレットを開く**
   - `Ctrl+Shift+P` (Windows/Linux) または `Cmd+Shift+P` (Mac)

2. **MCP サーバーを追加**
   - `MCP: Add Server` コマンドを実行
   - サーバーの種類を選択：
     - **NPM パッケージ**: Node.js製のサーバー
     - **コマンド (stdio)**: 実行可能ファイル
     - **HTTP**: リモートサーバー
     - **Docker イメージ**: コンテナとして実行

3. **設定の保存先を選択**
   - **ワークスペース**: `.vscode/mcp.json` に保存（プロジェクト固有）
   - **グローバル**: ユーザー設定に保存（全プロジェクト共通）

### 方法2: 手動設定ファイル作成

#### ワークスペース設定の場合

1. **設定ファイルの作成**
   ```
   プロジェクトルート/
   ├── .vscode/
   │   └── mcp.json    ← ここに作成
   └── その他のファイル...
   ```

2. **設定ファイルの内容**
   ```json
   {
     "mcpServers": {
       "サーバー名": {
         "command": "実行コマンド",
         "args": ["引数1", "引数2"],
         "env": {
           "環境変数名": "値または${input:variable_name}"
         }
       }
     }
   }
   ```

## 3. 具体的な設定例

### 3.1 Roam Research MCP サーバー

```json
{
  "mcpServers": {
    "roam-research": {
      "type": "stdio",
      "command": "npx",
      "args": ["roam-research-mcp@0.30.2"],
      "env": {
        "ROAM_API_TOKEN": "${input:roam_api_token}",
        "ROAM_GRAPH_NAME": "${input:roam_graph_name}",
        "MEMORIES_TAG": "${input:memories_tag}"
      }
    }
  },
  "inputs": [
    {
      "id": "roam_api_token",
      "type": "promptString",
      "description": "Enter your Roam Research API token"
    },
    {
      "id": "roam_graph_name",
      "type": "promptString", 
      "description": "Enter your Roam Research graph name"
    },
    {
      "id": "memories_tag",
      "type": "promptString",
      "description": "Enter the tag to use for memories (default: #[[LLM/Memories]])"
    }
  ]
}
```

### 3.2 Coverity Connect MCP サーバー

```json
{
  "mcpServers": {
    "coverity-connect": {
      "type": "stdio",
      "command": "node",
      "args": ["C:\\path\\to\\coverity-connect-mcp\\dist\\index.js"],
      "env": {
        "COVERITY_URL": "${input:coverity_url}",
        "COVERITY_USERNAME": "${input:coverity_username}",
        "COVERITY_PASSWORD": "${input:coverity_password}"
      }
    }
  },
  "inputs": [
    {
      "id": "coverity_url",
      "type": "promptString",
      "description": "Enter Coverity Connect URL"
    },
    {
      "id": "coverity_username", 
      "type": "promptString",
      "description": "Enter Coverity username"
    },
    {
      "id": "coverity_password",
      "type": "promptString",
      "description": "Enter Coverity password"
    }
  ]
}
```

## 4. MCP サーバーの管理

### 4.1 サーバー一覧の確認

```
コマンドパレット → MCP: List Servers
```

表示される情報：
- サーバー名
- 実行状態（実行中/停止中）
- 設定ファイルの場所

### 4.2 サーバーの操作

各サーバーで利用可能な操作：

- **Start/Stop/Restart**: サーバーの開始・停止・再起動
- **Show Output**: サーバーログの表示（デバッグ用）
- **Show Configuration**: 設定内容の表示
- **Browse Resources**: サーバーが提供するリソースの閲覧
- **Uninstall**: サーバーのアンインストール

## 5. Agent Mode での使用方法

### 5.1 ツールの有効化

1. **GitHub Copilot Chat を開く**
2. **Agent モードに切り替え**
3. **「Select Tools」ボタンをクリック**
4. **使用したいMCPツールを選択**

### 5.2 使用例

#### Roam Research の操作
```
Roam Researchの今日のデイリーページに「MCPサーバーのテスト」というメモを追加してください
```

```
Roam Researchで「プロジェクト管理」というタイトルのページを検索して内容を教えてください
```

#### Coverity Connect の操作
```
Coverityで重要度の高い欠陥を検索して、その詳細を教えてください
```

```
プロジェクトのセキュリティ関連の欠陥を調べて、修正の優先順位を教えてください
```

### 5.3 ツールの明示的な指定

プロンプト内で `#` を使ってツールを明示的に指定することも可能：

```
#roam_create_page を使って新しいページを作成してください
```

## 6. セキュリティとベストプラクティス

### 6.1 セキュリティ注意事項

⚠️ **重要**: MCP サーバーはマシン上で任意のコードを実行する可能性があります。
- 信頼できるソースからのサーバーのみを追加
- 公開者とサーバー設定を事前に確認
- 本番環境では十分な検証を実施

### 6.2 認証情報の管理

**❌ 避けるべき方法:**
```json
{
  "env": {
    "API_TOKEN": "sk-1234567890abcdef"  // ハードコーディング
  }
}
```

**✅ 推奨する方法:**
```json
{
  "env": {
    "API_TOKEN": "${input:api_token}",     // 入力変数
    "API_TOKEN": "${env:MY_API_TOKEN}"     // 環境変数
  }
}
```

### 6.3 チーム開発での共有

- `.vscode/mcp.json` をバージョン管理に含める
- 機密情報は環境変数または入力変数を使用
- `README.md` に必要な環境変数を文書化

## 7. トラブルシューティング

### 7.1 よくある問題

**サーバーが起動しない**
- パスが正しいか確認
- 依存関係（Node.js、npm パッケージ）がインストールされているか確認
- `MCP: List Servers` → `Show Output` でログを確認

**ツールが表示されない**
- サーバーが正常に起動しているか確認
- Agent Mode が有効になっているか確認
- VS Code を再起動してみる

**認証エラー**
- 環境変数や入力変数の値が正しいか確認
- API トークンの有効期限を確認

### 7.2 ログの確認方法

```
MCP: List Servers → 対象サーバーを選択 → Show Output
```

## 8. 参考リンク

- [VS Code MCP サーバー公式ドキュメント](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
- [Model Context Protocol 仕様](https://modelcontextprotocol.io/)
- [公式 MCP サーバーリポジトリ](https://github.com/modelcontextprotocol/servers)
- [VS Code MCP サーバー一覧](https://code.visualstudio.com/mcp)

---

この手順に従うことで、Visual Studio Code で MCP サーバーを効果的に活用し、GitHub Copilot の Agent Mode を拡張できます。