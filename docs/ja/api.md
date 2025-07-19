# API ドキュメント - Coverity Connect MCP Server

## 🎯 概要

このドキュメントでは、Coverity Connect MCP Serverの包括的なAPIドキュメントを、利用可能なすべてのツール、リソース、および使用パターンを含めて説明します。

## 📋 API スキーマ

Coverity Connect MCP ServerはModel Context Protocol (MCP) 仕様を実装し、以下の機能を提供します：

- **ツール**: Coverity操作用の5つの利用可能ツール
- **リソース**: 設定とデータアクセス用の2つの利用可能リソース  
- **プロンプト**: 一般的なワークフロー用の組み込みプロンプト

## 🛠️ 利用可能ツール

### 1. search_defects

高度なフィルタリング機能を使用してCoverity Connectで欠陥を検索します。

#### シグネチャ
```python
async def search_defects(
    query: str = "",
    stream_id: str = "",
    checker: str = "",
    severity: str = "",
    status: str = "",
    limit: int = 50
) -> List[Dict[str, Any]]
```

#### パラメータ

| パラメータ | タイプ | 必須 | デフォルト | 説明 |
|-----------|------|------|----------|-----|
| `query` | 文字列 | いいえ | `""` | 欠陥内容の一般検索クエリ |
| `stream_id` | 文字列 | いいえ | `""` | 特定のストリームIDでフィルタ |
| `checker` | 文字列 | いいえ | `""` | チェッカー名でフィルタ（例："NULL_RETURNS"） |
| `severity` | 文字列 | いいえ | `""` | 重要度でフィルタ（High、Medium、Low） |
| `status` | 文字列 | いいえ | `""` | ステータスでフィルタ（New、Triaged、Fixed等） |
| `limit` | 整数 | いいえ | `50` | 返される結果の最大数 |

#### 使用例

**基本検索:**
```
メインストリームの欠陥を検索してください
```

**フィルタ検索:**
```
まだNewステータスの高重要度NULL_RETURNS欠陥をすべて見つけてください
```

**高度な検索:**
```
ユーザー認証モジュールで修正されていないメモリリークをすべて表示してください
```

### 2. get_defect_details

CID（Coverity Issue Identifier）による特定の欠陥の詳細情報を取得します。

#### シグネチャ
```python
async def get_defect_details(cid: str) -> Dict[str, Any]
```

#### パラメータ

| パラメータ | タイプ | 必須 | 説明 |
|-----------|------|------|-----|
| `cid` | 文字列 | はい | Coverity Issue Identifier (CID) |

#### 使用例

**特定欠陥の取得:**
```
欠陥CID 12345の詳細を表示してください
```

**欠陥分析:**
```
CID 98765の根本原因を分析し、修正手順を提案してください
```

### 3. list_projects

Coverity Connectで利用可能なすべてのプロジェクトをリストします。

#### 使用例

**全プロジェクトリスト:**
```
すべてのCoverityプロジェクトを表示してください
```

**プロジェクト概要:**
```
ストリーム数を含むすべてのプロジェクトの概要を教えてください
```

### 4. list_streams

ストリームをリストし、オプションでプロジェクトによりフィルタします。

#### 使用例

**全ストリーム:**
```
Coverityのすべてのストリームをリストしてください
```

**プロジェクト固有ストリーム:**
```
WebApplicationプロジェクトのすべてのストリームを表示してください
```

### 5. get_project_summary

欠陥統計を含むプロジェクトの包括的なサマリー情報を取得します。

#### 使用例

**プロジェクトサマリー:**
```
WebApplicationプロジェクトのサマリーを教えてください
```

**品質ダッシュボード:**
```
プロジェクトPROJ001の欠陥トレンドを表示する品質ダッシュボードを作成してください
```

## 📊 利用可能リソース

### 1. プロジェクト設定

プロジェクト設定情報にアクセスします。

#### URI パターン
```
coverity://projects/{project_id}/config
```

### 2. ストリーム欠陥

特定のストリームの欠陥にアクセスします。

#### URI パターン
```
coverity://streams/{stream_id}/defects
```

## 🔧 認証

### 環境変数

すべてのAPI呼び出しには環境変数による適切な認証が必要です：

```bash
export COVERITY_HOST="your-coverity-server.com"
export COVERITY_PORT="8080"
export COVERITY_SSL="True"
export COVAUTHUSER="your-username"
export COVAUTHKEY="your-auth-key"
```

### エラーコード

| コード | メッセージ | 説明 |
|--------|----------|-----|
| 401 | 認証に失敗しました | 無効な認証情報 |
| 404 | リソースが見つかりません | 無効なプロジェクト/ストリームID |
| 500 | サーバーエラー | 内部Coverity Connectエラー |
| 503 | サービス利用不可 | Coverity Connectに到達不可 |

## 🧪 API テスト

### Claude Desktop使用

#### 基本テスト
```
Coverity MCP接続をテストし、利用可能なツールをリストしてください
```

#### 機能テスト
```
高重要度欠陥を検索し、上位5件の結果を表示してください
```

#### 統合テスト
```
WebApplicationプロジェクトの完全な分析を提供してください：
1. プロジェクトサマリー
2. ストリームリスト
3. 高重要度欠陥トップ10
4. 修正の推奨事項
```

### Python使用（開発）

```python
import asyncio
from coverity_mcp_server.coverity_client import CoverityClient

async def test_api():
    client = CoverityClient(
        host="localhost",
        port=5000,
        use_ssl=False,
        username="dummy_user",
        password="dummy_key"
    )
    
    try:
        # すべてのエンドポイントをテスト
        projects = await client.get_projects()
        print(f"プロジェクト: {len(projects)}")
        
        streams = await client.get_streams()
        print(f"ストリーム: {len(streams)}")
        
        defects = await client.get_defects(limit=5)
        print(f"欠陥: {len(defects)}")
        
    finally:
        await client.close()

# テスト実行
asyncio.run(test_api())
```

## 🔄 APIバージョニング

### 現在のバージョン
- **APIバージョン**: 1.0
- **MCPプロトコル**: 1.0
- **互換性**: Coverity Connect 2023.x+

### バージョン履歴
- **1.0.0**: コア機能による初回リリース

### 将来のバージョン
- **1.1.0**: 拡張フィルタリングと検索
- **1.2.0**: 一括操作とバッチ処理
- **2.0.0**: GraphQL APIとリアルタイム購読

## 📊 レート制限とパフォーマンス

### 現在の制限
- **同時接続数**: 10 (設定可能)
- **リクエストタイムアウト**: 30秒 (設定可能)
- **バッチサイズ**: 100項目 (設定可能)

### パフォーマンスのヒント
1. **適切な制限を使用**: 必要以上のデータを要求しない
2. **バッチ操作**: 関連するリクエストをグループ化
3. **結果をキャッシュ**: クライアント側キャッシュを実装
4. **接続を監視**: 接続プール枯渇に注意

---

**最終更新**: 2025年7月19日  
**APIバージョン**: 1.0  
**MCPプロトコルバージョン**: 1.0