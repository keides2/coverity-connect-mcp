# 開発環境セットアップガイド

このディレクトリには、Coverity Connect MCP Serverの開発・テスト環境用設定が含まれています。

## 🎯 概要

開発環境では、実際のCoverity Connectサーバーの代わりにダミーサーバーを使用してテストできます。

## 📁 ファイル構成

```
development/
├── mock_server.py                 # ダミーCoverity Connect サーバー
├── .env.development              # 開発環境変数
├── claude_desktop_config.json   # Claude Desktop設定（開発用）
└── README_dev.md                 # このファイル
```

## 🚀 クイックスタート

### 1. ダミーサーバーの起動

```bash
# プロジェクトルートから
python examples/development/mock_server.py

# または便利スクリプトを使用
.\scripts\start_mock_server.bat
```

ダミーサーバーが http://localhost:5000 で起動します。

### 2. MCPサーバーの起動

新しいターミナルで：

```bash
# 環境変数設定
$env:COVERITY_HOST="localhost"
$env:COVERITY_PORT="5000"
$env:COVERITY_SSL="False"
$env:COVAUTHUSER="dummy_user"
$env:COVAUTHKEY="dummy_key"

# MCPサーバー起動
python -m coverity_mcp_server

# または便利スクリプトを使用
.\scripts\start_dev.bat
```

### 3. Claude Desktop設定

`claude_desktop_config.json`の内容をClaude Desktopの設定ファイルにコピーします：

**Windows設定ファイル場所：**
- `%APPDATA%\Claude\claude_desktop_config.json`
- または `%LOCALAPPDATA%\Claude\claude_desktop_config.json`

## 🔧 設定詳細

### 環境変数

| 変数名 | 値 | 説明 |
|--------|-------|------|
| `COVERITY_HOST` | `localhost` | ダミーサーバーのホスト |
| `COVERITY_PORT` | `5000` | ダミーサーバーのポート |
| `COVERITY_SSL` | `False` | SSL無効（テスト用） |
| `COVAUTHUSER` | `dummy_user` | テスト用ユーザー |
| `COVAUTHKEY` | `dummy_key` | テスト用キー |

### ダミーサーバー機能

- **プロジェクト管理**: 3つのサンプルプロジェクト
- **ストリーム管理**: プロジェクトごとの開発ストリーム
- **欠陥管理**: ダミー欠陥データ
- **SOAP API**: Coverity ConnectのSOAPエンドポイントをモック

## 🧪 テスト方法

### 1. 基本接続テスト

Claude Desktopで以下を実行：

```
Coverity MCPサーバーに接続できていますか？
```

### 2. プロジェクト取得テスト

```
Coverityのプロジェクト一覧を取得してください
```

### 3. 欠陥検索テスト

```
Coverityで重要度がHighの欠陥を検索してください
```

## 📊 ダミーデータ

### プロジェクト
- **PROJ001**: WebApplication
- **PROJ002**: MobileApp  
- **PROJ003**: APIService

### ストリーム
- main, develop, release (WebApplication)
- main, feature (MobileApp)
- main (APIService)

### 欠陥
- CID 1001-1003のサンプル欠陥データ

## 🔍 トラブルシューティング

### ダミーサーバーが起動しない
```bash
# Flaskのインストール確認
pip install flask

# ポート使用状況確認
netstat -an | findstr :5000
```

### MCPサーバー接続エラー
```bash
# パッケージ再インストール
pip install -e .

# 環境変数確認
echo $env:COVERITY_HOST
```

### Claude Desktop接続失敗
1. 設定ファイルのパスを確認
2. JSON構文エラーチェック
3. Claude Desktopの再起動

## 📝 開発メモ

- ダミーサーバーはデバッグ情報を出力します
- MCPサーバーは`DEBUG`ログレベルで動作します
- すべての通信は非暗号化（開発用）

## 🚀 本番環境への移行

開発が完了したら、`../production/`の設定を使用して本番環境にデプロイしてください。