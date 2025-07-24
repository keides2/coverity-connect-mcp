# Coverity Connect MCP Server - セットアップガイド

## 概要

このガイドでは、Coverity Connect MCP Serverを本番環境で立ち上げるための完全な手順を説明します。

本MCPサーバーは以下の特徴があります：
- 認証情報やプロキシ設定は環境変数から読み込み（ハードコーディングなし）
- GitHub Copilot Chatとの統合
- セキュアな本番環境デプロイメント

## 前提条件

### 必要なソフトウェア
- Python 3.8以上
- Visual Studio Code
- GitHub Copilot拡張機能

### 必要な情報
- Coverity Connect サーバーのURL
- Coverity Connect のユーザー名とパスワード
- プロキシサーバー情報（必要な場合）

## インストール手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/keides2/coverity-connect-mcp
cd coverity-connect-mcp
```

### 2. Python仮想環境のセットアップ

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 環境変数の設定

### 必須環境変数

```bash
# Coverity Connect サーバーのURL
export COVERITY_HOST="https://your-coverity-server.com"

# Coverity Connect 認証情報
export COVAUTHUSER="your_username"
export COVAUTHKEY="your_password"
```

### オプション環境変数

```bash
# プロキシ設定（標準的な環境変数）
export HTTPS_PROXY="http://your-proxy-server.com:PORT"
export HTTP_PROXY="http://your-proxy-server.com:PORT"

# または、カスタムプロキシ設定
export PROXY_HOST="your-proxy-server.com"
export PROXY_PORT="PORT"
```

### 便利な設定方法

環境変数設定用のテンプレートファイルを使用できます：

```bash
# テンプレートファイルをコピーして編集
cp setup_env_template.bat setup_env.bat
# setup_env.batを編集して実際の値を設定
# 実行
setup_env.bat
```

## GitHub Copilot Chatとの連携設定

### VS Code設定ファイルの編集

VS Code の settings.json に以下を追加してください：

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
        "PROXY_PORT": "PORT",
        "LOG_LEVEL": "INFO",
        "SSL_VERIFY": "false",
        "TIMEOUT_SECONDS": "30"
      }
    }
  }
}
```

### settings.jsonの場所

- **Windows**: `%APPDATA%\Code\User\settings.json`
- **VS Code内**: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"

### 重要なポイント

1. **COVERITY_HOST**: 実際のCoverityサーバーURLに置き換えてください（`https://` プロトコルを含める）
2. **COVAUTHUSER**: 実際のCoverityユーザー名に置き換えてください
3. **COVAUTHKEY**: 実際のCoverityパスワードまたはトークンに置き換えてください
4. **cwd**: プロジェクトの実際のパスに置き換えてください
5. **プロキシ設定**: 必要に応じて `PROXY_HOST` と `PROXY_PORT` を実際の値に設定してください

⚠️ **セキュリティ注意**: settings.jsonを編集する際は、実際の認証情報をGitHubにプッシュしないよう注意してください。

💡 **重要なヒント**: 環境変数が正しく読み込まれない場合があります。その場合は、VS Code settings.jsonの`env`セクションに直接値を記述することで確実に動作します。

## 本番環境デプロイメント

### 自動デプロイメント（推奨）

本番環境への切り替えは自動化されています：

```bash
# 本番用ファイルに切り替え
deploy_production.bat
```

このスクリプトは以下を実行します：
1. 現在のファイルをバックアップ
2. 本番用ファイルをメインファイルに変更
3. 環境変数の設定指示を表示

### 手動デプロイメント

手動で行う場合：

```bash
# 1. 現在のファイルをバックアップ
mv src/coverity_mcp_server/main.py src/coverity_mcp_server/main_dev.py
mv src/coverity_mcp_server/coverity_client.py src/coverity_mcp_server/coverity_client_dev.py

# 2. 本番用ファイルをメインファイルに変更
cp src/coverity_mcp_server/main_production.py src/coverity_mcp_server/main.py
cp src/coverity_mcp_server/coverity_client_production.py src/coverity_mcp_server/coverity_client.py
```

## 起動と動作確認

### サーバーの起動

```bash
# 本番環境用起動スクリプト
start_production.bat

# または手動起動
python -m src.coverity_mcp_server
```

### VS Codeでの確認

1. settings.json を保存
2. VS Code を完全終了
3. VS Code を再起動
4. GitHub Copilot Chat で接続テスト

### 動作確認コマンド

GitHub Copilot Chatで以下を実行：

```
Coverity MCPサーバーの現在の設定を教えてください
```

期待される出力例：
```
COVERITY_HOST: https://your-coverity-server.com
Using HTTP proxy: http://your-proxy-server.com:PORT
```

## トラブルシューティング

### ⚠️ 重要：環境変数が既定値に上書きされる問題

**症状**: 環境変数を正しく設定しているにも関わらず、サーバーが既定値やハードコーディングされた値を使用してしまう。

**原因**: 
- コード内の既定値の設定順序の問題
- 環境変数の読み込みタイミングの問題
- Python仮想環境やプロセスの環境変数継承の問題

**解決方法**:

1. **環境変数の優先順位確認**: 
   ```bash
   # 実行前に環境変数が正しく設定されているか確認
   echo $COVERITY_HOST        # Linux/macOS
   echo %COVERITY_HOST%       # Windows
   ```

2. **VS Code設定での直接指定**（推奨）:
   settings.jsonの`env`セクションで直接値を指定することで、確実に設定値が使用されます。

3. **最終手段 - 直書き対応**:
   環境変数が機能しない場合は、一時的に以下のファイルに直接値を記述：
   ```
   src/coverity_mcp_server/main.py
   src/coverity_mcp_server/coverity_client.py
   ```
   
   ⚠️ **注意**: 直書きした場合は、GitHubプッシュ前に必ず値を削除またはテンプレート化してください。
   
   ⚠️ **重要**: プロジェクトのルートディレクトリ（coverity-connect-mcp/）から実行してください。

4. **デバッグ方法**:
   サーバー起動時のログで実際に使用されている値を確認：
   ```
   COVERITY_HOST: [実際の値]
   Using HTTP proxy: [実際のプロキシ設定]
   ```

### 環境変数が設定されていない場合

エラーメッセージ例：
```
Missing required environment variables: COVERITY_HOST, COVAUTHUSER, COVAUTHKEY
Please set the following environment variables:
  COVERITY_HOST - Coverity Connect server URL
  COVAUTHUSER - Coverity Connect username
  COVAUTHKEY - Coverity Connect password/token
```

**解決方法**: 上記の環境変数設定セクションを参照してください。

### 接続エラーの場合

1. **プロキシ設定の確認**: プロキシサーバーのURLとポートが正しいか確認
2. **認証情報の確認**: ユーザー名とパスワードが正しいか確認
3. **サーバーURL確認**: CoverityサーバーのURLが正しく、`https://`プロトコルが含まれているか確認

### VS Code設定の問題

1. settings.jsonの構文が正しいか確認（JSONフォーマット）
2. パスの区切り文字が正しいか確認（Windowsの場合は`\\`）
3. VS Codeの完全再起動

## セキュリティ考慮事項

- **認証情報の保護**: パスワードや認証キーは環境変数またはセキュアなシークレット管理システムを使用
- **ログ出力**: パスワードはログに出力されず、マスクされます
- **プロキシ設定**: プロキシ設定も環境変数から読み込まれ、コードに埋め込まれていません
- **GitHub統合**: 本番用ファイルをGitHubにプッシュすることで、機密情報が含まれない安全なコードのみが保存されます

## 参考資料

### 詳細ドキュメント
- `docs/system_architecture_design.md` - システムアーキテクチャ
- `docs/function_specifications.md` - 関数仕様書
- `docs/api.md` - API仕様

### 開発者向け
- `docs/Contributing Guide.pdf` - 開発貢献ガイド
- `docs/project_completion_plan.md` - プロジェクト計画

### トラブルシューティング
- 問題が解決しない場合は、プロジェクトのIssueページで報告してください
- `test/`フォルダ内の実際の設定ファイルも参考にしてください
