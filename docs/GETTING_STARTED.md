# Coverity Connect MCP Server - VSCode統合セットアップガイド

## 概要

このガイドでは、Coverity Connect MCP ServerをVSCode GitHub Copilot Agentと統合するための完全な手順を説明します。

本MCPサーバーは以下の特徴があります：
- VSCodeによる自動管理（ターミナル占有なし）
- GitHub Copilot Agentとの直接統合
- 環境変数による設定管理（ハードコーディングなし）

## 前提条件

### 必要なソフトウェア
- Python 3.8以上
- Visual Studio Code
- GitHub Copilot拡張機能

### 必要な情報
- Coverity Connect サーバーのURL
- Coverity Connect のユーザー名とパスワード
- プロキシサーバー情報（必要な場合）

## セットアップ構成

セットアップは**サーバー側**（MCPサーバー環境構築）と**クライアント側**（VSCode統合設定）に分かれます。

### Python仮想環境の必要性

**VSCodeターミナルで起動するMCPサーバーには仮想環境が必要です。**

理由：
- **依存関係の分離**: MCPサーバーの依存パッケージを他のPythonプロジェクトと分離
- **VSCodeの実行環境**: VSCodeがMCPサーバーを起動する際、指定されたPythonインタープリターを使用
- **パッケージバージョン管理**: プロジェクト固有のパッケージバージョンを保証

## サーバー側セットアップ（MCPサーバー環境構築）

### 1. リポジトリのクローンと環境準備

```bash
git clone https://github.com/keides2/coverity-connect-mcp.git
cd coverity-connect-mcp

# Python仮想環境のセットアップ
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 2. パッケージインストール

```bash
# 依存関係のインストール
pip install -r requirements.txt

# パッケージのインストール
pip install -e .
```

### 3. インストール確認

```bash
# 正常にインストールされたか確認
python -c "from src.coverity_mcp_server import create_server; print('Import successful')"

# CLIが動作するか確認
python -m src.coverity_mcp_server.main --help
```

### 4. 環境変数の設定

#### 方法1: .envファイル作成（推奨）

プロジェクトルートに`.env`ファイルを手作業で作成：

1. **ファイル作成**: プロジェクトルートフォルダで新しいファイルを作成
2. **ファイル名**: `.env` （ドット付き、拡張子なし）
3. **内容**: 以下のテンプレートをコピーして実際の値に変更

```bash
# Coverity Connect MCP Server - Environment Variables
# 本番環境用設定

# 必須: Coverity Connect サーバー設定
COVERITY_HOST=https://your-coverity-server.com
COVAUTHUSER=your_username
COVAUTHKEY=your_actual_password_or_token

# オプション: その他の設定
COVERITY_PORT=443
COVERITY_SSL=true
LOG_LEVEL=INFO

# プロキシ設定（必要に応じて）
PROXY_HOST=your-proxy-server.com
PROXY_PORT=your-port
```

**重要**: 
- すべての `your_xxx` 部分を実際の値に置き換えてください
- `COVAUTHKEY`は実際のCoverity Connect**認証キー**または**パスワード**です

#### 方法2: setup_env_template.batを使用（Windows）

プロジェクトに`setup_env_template.bat`がある場合：

```bash
# 1. テンプレートファイルをコピー
copy setup_env_template.bat setup_env.bat

# 2. setup_env.batファイルを編集
# テキストエディタでsetup_env.batを開き、以下の箇所を実際の値に変更：
# - your_coverity_username → 実際のユーザー名
# - your_password_here → 実際のパスワード/認証キー
# - your-coverity-server.com → 実際のCoverityサーバーURL
# - your-proxy-server.com → 実際のプロキシサーバー（必要な場合）

# 3. バッチファイル実行
setup_env.bat
```

### 5. サーバー動作確認（推奨）

VSCode統合前に、MCPサーバーが正常に動作することを確認：

```bash
# 仮想環境内で実際の設定で起動テスト
python -m src.coverity_mcp_server.main
```

**期待される正常起動ログ例**:
```
Starting Coverity Connect MCP Server...
=== Configuration Loading ===
COVERITY_HOST: https://your-coverity-server.com
COVAUTHUSER: your_username
COVAUTHKEY: ***
Parsed URL - Host: your-server, Port: 443, SSL: True
Coverity client initialized successfully
```

**※ 確認後、`Ctrl+C`でサーバーを停止してください。**
VSCode クライアント側がMCPサーバーを自動起動します。

## クライアント側セットアップ（VSCode統合設定）

### 1. VSCode設定ファイルの場所

**Windows:**
- `%APPDATA%\Code\User\settings.json`
- または VSCode内で: `Ctrl+Shift+P` → `Preferences: Open User Settings (JSON)`

### 2. MCP設定の追加

`settings.json`に以下を追加してください：

#### Option A: フルパス指定（推奨）

```json
{
  "github.copilot.chat.experimental.mcpServers": {
    "coverity-connect": {
      "command": "C:/path/to/your/coverity-connect-mcp/venv/Scripts/python.exe",
      "args": ["-m", "src.coverity_mcp_server.main"],
      "cwd": "C:/path/to/your/coverity-connect-mcp",
      "env": {
        "COVERITY_HOST": "https://your-coverity-server.com",
        "COVAUTHUSER": "your_username",
        "COVAUTHKEY": "your_actual_password_or_token",
        "COVERITY_PORT": "443",
        "COVERITY_SSL": "true",
        "PROXY_HOST": "your-proxy-server.com",
        "PROXY_PORT": "your-port",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Option B: 環境変数活用

```json
{
  "github.copilot.chat.experimental.mcpServers": {
    "coverity-connect": {
      "command": "python",
      "args": ["-m", "src.coverity_mcp_server.main"],
      "cwd": "C:/path/to/your/coverity-connect-mcp",
      "env": {
        "PATH": "C:/path/to/your/coverity-connect-mcp/venv/Scripts;${env:PATH}",
        "VIRTUAL_ENV": "C:/path/to/your/coverity-connect-mcp/venv",
        "COVERITY_HOST": "https://your-coverity-server.com",
        "COVAUTHUSER": "your_username",
        "COVAUTHKEY": "your_actual_password_or_token",
        "COVERITY_PORT": "443",
        "COVERITY_SSL": "true",
        "PROXY_HOST": "your-proxy-server.com",
        "PROXY_PORT": "your-port",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**重要なポイント**:
1. **Pythonパス**: 仮想環境のPythonを正確に指定
2. `cwd`パスを実際のプロジェクトディレクトリパスに変更
3. `COVERITY_HOST`を実際のCoverityサーバーURLに変更
4. `COVAUTHUSER`を実際のユーザー名に変更
5. `COVAUTHKEY`を実際の認証情報に変更
6. プロキシ設定を環境に合わせて調整（不要な場合は削除）

※環境変数を読み込めない場合があります

### 3. VSCodeの再起動

1. `settings.json`を保存
2. VSCodeを完全終了（タスクマネージャーから終了）
3. VSCodeを再起動

## 推奨セットアップフロー

### ステップ1: サーバー側準備

```bash
# 1. 環境構築
git clone https://github.com/keides2/coverity-connect-mcp.git
cd coverity-connect-mcp
python -m venv venv
venv\Scripts\activate  # Windows

# 2. パッケージインストール  
pip install -r requirements.txt
pip install -e .

# 3. 環境設定
# .envファイル作成・編集

# 4. 動作テスト
python -m src.coverity_mcp_server.main
```

### ステップ2: クライアント側設定

```bash
# 1. VSCode settings.json編集
# - 仮想環境のPythonパスを正確に指定
# - cwdパスを正確に指定

# 2. VSCode再起動

# 3. 統合テスト
# GitHub Copilot Chatで接続確認
```

## 動作確認

### 1. GitHub Copilot Chatでの接続確認

VSCode内でGitHub Copilot Chatを開き、以下をテストしてください：

```
Coverity MCPサーバーに接続できていますか？利用可能なツールとリソースを教えてください
```

**期待される応答**:

- MCPサーバーへの接続確認
- 利用可能なツール一覧（search_defects、list_projects等）
- 利用可能なリソース一覧


**補足**:

- VSCodeの自動管理について
  - VSCodeが自動的に行うこと:
  - MCPサーバーの自動起動: `GitHub Copilot Chat`を使用する際に、設定されたMCPサーバーを自動的にバックグラウンドで起動
  - プロセス管理: MCPサーバーのプロセスをVSCode内で管理
  - 自動停止: `VSCode`を終了すると、MCPサーバーも自動的に停止

- あなたが手動でやる必要がないこと:
  - ターミナルでMCPサーバーを起動する
  - MCPサーバーを手動で停止する
  - 仮想環境を手動で有効化する（VSCodeが設定に従って実行）

- 具体的な接続フロー:

  1. VSCode再起動後
  `VSCode`起動 → `settings.json`読み込み → MCP設定認識
  1. GitHub Copilot Chat使用時
  `Copilot Chat`開く → MCPサーバー自動起動 → Coverity接続確立
  1. バックグラウンドで実行されるコマンド
  
  ```bash
  # VSCodeが内部的に実行（ユーザーには見えない）
  cd C:/path/to/your/coverity-connect-mcp
  C:/path/to/your/coverity-connect-mcp/venv/Scripts/python.exe -m src.coverity_mcp_server.main
  ```

- 環境変数は、`VSCode` `settings.json`の環境変数をサーバー側`.env`ファイルと完全に一致させてください。
- AIモデルは、ChatGPT 4.1で問題ありません。 MCPプロトコルは言語モデルに依存しません。


### 2. 実際のCoverityデータアクセステスト

```
Coverityのプロジェクト一覧を取得してください
```

```
Coverityで重要度がHighの欠陥を検索してください
```

## VSCode統合の利点

### ターミナル管理
- **ターミナル占有なし**: VSCodeがバックグラウンドでMCPサーバーを管理
- **自動開始/停止**: 必要な時だけサーバーが動作
- **複数ターミナル利用可能**: 開発作業用のターミナルは自由に使用可能

### 開発効率
- **シームレス統合**: GitHub Copilot Chatから直接Coverityにアクセス
- **設定管理**: settings.jsonで集中管理
- **デバッグ**: VSCode Output パネルでMCPサーバーのログ確認可能

## トラブルシューティング

### サーバー側準備段階でのエラー

#### インポートエラーの場合
```bash
# パッケージの再インストール
pip install -e . --force-reinstall
```

#### 依存関係エラーの場合  
```bash
# 依存関係の更新
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

#### 環境変数エラーの場合
```bash
# PowerShellで環境変数確認（Windows）
Get-Content .env
# .envファイルの内容と実際の値を確認
```

### MCP接続エラーの場合

1. **VSCode Output パネル確認**
   - `View` → `Output` → `GitHub Copilot Chat` を選択
   - MCPサーバーのエラーログを確認

2. **設定確認**
   - settings.jsonの構文が正しいか確認
   - Pythonパス設定が正確か確認（仮想環境のpython.exe）
   - cwdパス設定が正確か確認
   - 環境変数の値が正しいか確認

3. **VSCode完全再起動**
   - 設定変更後は必ず完全再起動

### 認証エラーの場合

```
Coverity Connect への認証に失敗しました
```

- `COVAUTHKEY`が正しく設定されているか確認
- Coverity Connect サーバーへの接続可能性を確認

### プロキシエラーの場合

- `PROXY_HOST`と`PROXY_PORT`の設定を確認
- 企業ネットワークの設定を確認

## セキュリティ考慮事項

- **認証情報の保護**: settings.jsonは個人設定ファイルのため、チーム共有しない
- **バージョン管理**: `.env`ファイルは`.gitignore`に含まれており、GitHubにプッシュされない
- **ログ出力**: パスワードはログに出力されず、マスクされる

## 利用可能なMCPツール

| ツール | 説明 | 使用例 |
|--------|------|-------|
| `search_defects` | 欠陥の高度検索 | 高重要度セキュリティ脆弱性の検索 |
| `get_defect_details` | 特定欠陥の詳細分析 | 欠陥の根本原因分析と修正手順 |
| `list_projects` | プロジェクト一覧取得 | プロジェクトインベントリとアクセス確認 |
| `list_streams` | ストリーム一覧取得 | ストリームベースの分析計画 |
| `get_project_summary` | プロジェクト包括分析 | エグゼクティブレベルの品質レポート |
| `list_users` | ユーザー一覧取得 | ユーザー管理とアクセス制御 |
| `get_user_details` | ユーザー詳細情報 | 個別ユーザーの権限確認 |
| `get_user_roles` | ユーザー権限分析 | セキュリティ監査とアクセス制御レビュー |

---

**このガイドにより、VSCodeとGitHub Copilot Agentを使用してCoverity Connectに自然言語でアクセスできるようになります。ターミナルを占有せず、シームレスな開発体験を提供します。**

---
2025/07/24 keides2 初版
