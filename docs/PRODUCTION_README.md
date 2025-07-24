# Coverity Connect MCP Server - Production Deployment

## 概要

本番環境用のCoverity Connect MCPサーバーです。認証情報やプロキシ設定は環境変数から読み込まれ、コード内にハードコーディングされていません。

## 必要な環境変数

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
export HTTPS_PROXY="http://your-proxy-server.com:3128"
export HTTP_PROXY="http://your-proxy-server.com:3128"

# または、カスタムプロキシ設定
export PROXY_HOST="your-proxy-server.com"
export PROXY_PORT="3128"
```

## ファイル構成

- `main_production.py` - 本番環境用メインファイル（環境変数のみ使用）
- `coverity_client_production.py` - 本番環境用APIクライアント（環境変数のみ使用）
- `main.py` - 開発/テスト用（ハードコーディング含む）
- `coverity_client.py` - 開発/テスト用（ハードコーディング含む）

## 本番環境への移行手順

### 1. 現在のファイルをバックアップ

```bash
# 現在のファイルを_dev.pyとしてバックアップ
mv main.py main_dev.py
mv coverity_client.py coverity_client_dev.py
```

### 2. 本番用ファイルをメインファイルに変更

```bash
# 本番用ファイルをメインファイルとして使用
cp main_production.py main.py
cp coverity_client_production.py coverity_client.py
```

### 3. 環境変数の設定

PowerShell (Windows):
```powershell
$env:COVERITY_HOST = "https://your-coverity-server.com"
$env:COVAUTHUSER = "your_username"
$env:COVAUTHKEY = "your_password"
$env:HTTPS_PROXY = "http://your-proxy-server.com:3128"
$env:HTTP_PROXY = "http://your-proxy-server.com:3128"
```

Bash (Linux/macOS):
```bash
export COVERITY_HOST="https://your-coverity-server.com"
export COVAUTHUSER="your_username"
export COVAUTHKEY="your_password"
export HTTPS_PROXY="http://your-proxy-server.com:3128"
export HTTP_PROXY="http://your-proxy-server.com:3128"
```

### 4. 動作確認

```bash
# テスト実行
python -m src.coverity_mcp_server.main_production --help

# サーバー起動
python -m src.coverity_mcp_server.main_production
```

## セキュリティ考慮事項

- **認証情報の保護**: パスワードや認証キーは環境変数またはセキュアなシークレット管理システムを使用
- **ログ出力**: パスワードはログに出力されず、マスクされます
- **プロキシ設定**: プロキシ設定も環境変数から読み込まれ、コードに埋め込まれていません

## エラーハンドリング

### 環境変数が設定されていない場合

サーバー起動時に必要な環境変数が設定されていない場合、明確なエラーメッセージが表示されます：

```
Missing required environment variables: COVERITY_HOST, COVAUTHUSER, COVAUTHKEY
Please set the following environment variables:
  COVERITY_HOST - Coverity Connect server URL (e.g., https://your-coverity-server.com)
  COVAUTHUSER - Coverity Connect username
  COVAUTHKEY - Coverity Connect password/token
```

### 接続エラーの場合

接続に失敗した場合、詳細なエラー情報が提供され、設定の確認方法が示されます。

## GitHub統合

本番用ファイルは以下の手順でGitHubにプッシュできます：

1. 現在の開発用ファイルを削除またはリネーム
2. 本番用ファイルをメインファイル名に変更
3. コミット＆プッシュ

これにより、GitHubリポジトリには機密情報が含まれない安全なコードのみが保存されます。
