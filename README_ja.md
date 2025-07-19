# Coverity Connect MCP Server

<img src="top.png" alt="Coverity Connect MCP Server" width="700">

[![PyPI version](https://badge.fury.io/py/coverity-connect-mcp.svg)](https://badge.fury.io/py/coverity-connect-mcp)
[![Python Support](https://img.shields.io/pypi/pyversions/coverity-connect-mcp.svg)](https://pypi.org/project/coverity-connect-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/keides2/coverity-connect-mcp/workflows/Tests/badge.svg)](https://github.com/keides2/coverity-connect-mcp/actions)
[![Coverage](https://codecov.io/gh/keides2/coverity-connect-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/keides2/coverity-connect-mcp)

[English](README.md) | **日本語**

AIアシスタント（Claude Desktopなど）と**Black Duck Coverity Connect**静的解析プラットフォームを**シームレスに統合**する**Model Context Protocol (MCP) サーバー**です。

自然言語コマンドとAI駆動の自動解析により、Coverityワークフローを革新的に変革します。

## 🚀 機能

### 🔍 **包括的なCoverity統合**
- **プロジェクト管理**: Coverityプロジェクトとストリームの一覧・探索
- **スナップショット解析**: 詳細な欠陥分析と自動レポート生成
- **セキュリティ重視**: 専門的なセキュリティ脆弱性検出・分析
- **CI/CD自動化**: 継続的品質監視のための自動パイプライン統合
- **品質レポート**: エグゼクティブレベルの品質ダッシュボードと傾向分析

### 🤖 **AI駆動の解析**
- **自然言語クエリ**: 「プロジェクトXの重要なセキュリティ問題を表示して」
- **インテリジェントフィルタリング**: 高影響度欠陥の自動優先順位付け
- **コンテキスト推奨**: AI駆動の修正提案
- **傾向分析**: 履歴データ分析と品質メトリクス

### 🛠️ **エンタープライズ対応**
- **SOAP API統合**: Coverity Connect Webサービスの完全サポート
- **認証**: 安全な認証キーベース認証
- **プロキシサポート**: 企業ネットワークとプロキシ設定
- **マルチプラットフォーム**: Windows、macOS、Linux対応
- **Docker対応**: エンタープライズ環境向けコンテナ化デプロイメント

## 📦 インストール

### pipを使用（推奨）
```bash
pip install coverity-connect-mcp
```

### Dockerを使用
```bash
docker pull keides2/coverity-connect-mcp:latest
```

### ソースから
```bash
git clone https://github.com/keides2/coverity-connect-mcp.git
cd coverity-connect-mcp
pip install -e .
```

## ⚙️ 設定

### 1. 環境変数
`.env`ファイルを作成するか、環境変数を設定してください：

```bash
# 必須 - Coverity Connect認証
export COVAUTHUSER="coverityユーザー名"
export COVAUTHKEY="coverity認証キー"

# 必須 - Coverityサーバー
export COVERITY_HOST="your-coverity-server.com"
export COVERITY_PORT="443"
export COVERITY_SSL="True"

# オプション - ローカルワークスペース
export COVERITY_BASE_DIR="/path/to/coverity/workspace"

# オプション - 企業プロキシ（必要な場合）
export PROXY_HOST="proxy-server.com"
export PROXY_PORT="3128"
export PROXY_USER="プロキシユーザー名"  # 認証が必要な場合
export PROXY_PASS="プロキシパスワード"  # 認証が必要な場合
```

### 2. Claude Desktop統合
`claude_desktop_config.json`に追加：

```json
{
  "mcpServers": {
    "coverity-connect": {
      "command": "coverity-mcp-server",
      "env": {
        "COVAUTHUSER": "${COVAUTHUSER}",
        "COVAUTHKEY": "${COVAUTHKEY}",
        "COVERITY_HOST": "your-coverity-server.com"
      }
    }
  }
}
```

### 3. Docker設定
```yaml
# docker-compose.yml
version: '3.8'
services:
  coverity-mcp:
    image: keides2/coverity-connect-mcp:latest
    environment:
      - COVAUTHUSER=${COVAUTHUSER}
      - COVAUTHKEY=${COVAUTHKEY}
      - COVERITY_HOST=${COVERITY_HOST}
      # オプション：プロキシ設定
      - PROXY_HOST=${PROXY_HOST}
      - PROXY_PORT=${PROXY_PORT}
    ports:
      - "8000:8000"
```

## 🎯 使用例

### 基本的なプロジェクト解析
```
すべてのCoverityプロジェクトとその現在のステータスを表示してください
```

### セキュリティ重視の解析
```
プロジェクト「MyWebApp」の最新スナップショットを解析し、高重要度のセキュリティ脆弱性に焦点を当ててください。具体的な修正推奨事項を提供してください。
```

### 品質レポート
```
プロジェクト「MyProject」の過去30日間の傾向を含む包括的な品質レポートを生成してください
```

### CI/CD統合
```
グループ「web-team」、プロジェクト「frontend」、ブランチ「main」のCoverity自動解析を実行し、コミットメッセージ「セキュリティ修正」で実行してください
```

### 高度なフィルタリング
```
プロジェクト「EmbeddedSystem」のすべてのCERT-C違反で影響レベル「High」のものを表示し、修正のためのコード例を提供してください
```

## 🛠️ 利用可能なツール

| ツール | 説明 | 使用例 |
|------|-------------|---------------|
| `get_coverity_projects` | アクセス可能なCoverityプロジェクト一覧を取得 | プロジェクト棚卸しとアクセス確認 |
| `get_project_streams` | 特定プロジェクトのストリームを取得 | ストリームベース解析計画 |
| `get_stream_snapshots` | ストリームのスナップショット履歴を取得 | 履歴解析と傾向追跡 |
| `analyze_snapshot_defects` | スナップショットの詳細欠陥解析 | 詳細なセキュリティと品質解析 |
| `run_coverity_automation` | 自動CI/CDパイプライン実行 | 継続的統合ワークフロー |
| `parse_coverity_issues` | 解析結果の解析とフィルタリング | カスタムレポートとデータ抽出 |
| `generate_quality_report` | エグゼクティブ品質レポート作成 | 管理報告とKPI |

## 📚 ドキュメント

- **[インストールガイド](docs/ja/installation.md)** - 詳細なセットアップ手順
- **[設定リファレンス](docs/ja/configuration.md)** - 完全な設定オプション
- **[APIリファレンス](docs/ja/api.md)** - 包括的なAPIドキュメント
- **[使用例](docs/usage.md)** - 実際の使用シナリオ *(作成中)*
- **[トラブルシューティング](docs/troubleshooting.md)** - よくある問題と解決方法 *(作成中)*

> 📝 **注意**: 詳細なドキュメントは、実際の使用例とコミュニティフィードバックを基に作成中です。メインREADMEには、すぐに始めるための完全なセットアップと使用情報が提供されています。

## 🧪 テスト

```bash
# 単体テスト実行
pytest tests/

# 統合テスト実行
pytest tests/ -m integration

# カバレッジ付きテスト実行
pytest --cov=coverity_mcp_server tests/

# Dockerでテスト
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🤝 貢献

貢献を歓迎します！詳細は[貢献ガイド](CONTRIBUTING.md)をご覧ください。

### 開発環境セットアップ
```bash
git clone https://github.com/keides2/coverity-connect-mcp.git
cd coverity-connect-mcp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

### 変更の提出
1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを開く

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 🙏 謝辞

- **Black Duck Coverity** - 静的解析プラットフォームの提供
- **Anthropic** - Model Context ProtocolとClaude AIの提供
- **オープンソースコミュニティ** - 基盤となるライブラリとツールの提供

## 📞 サポート

- **GitHub Issues**: [バグ報告や機能要求](https://github.com/keides2/coverity-connect-mcp/issues)
- **Discussions**: [コミュニティサポートと質問](https://github.com/keides2/coverity-connect-mcp/discussions)
- **セキュリティ問題**: [セキュリティポリシー](SECURITY.md)をご確認ください

## 🗺️ ロードマップ

- [ ] **v1.1**: 高度なフィルタリングとカスタムビュー
- [ ] **v1.2**: マルチテナントサポートとユーザー管理
- [ ] **v1.3**: SOAPと並行したREST API
- [ ] **v1.4**: 機械学習による欠陥優先順位付け
- [ ] **v2.0**: プラグインアーキテクチャとサードパーティ統合

## 🌸 日本での活用

### **企業環境での実用性**
- **大手SIer**: エンタープライズ開発での品質管理
- **製造業**: 組み込みソフトウェアのセキュリティ強化
- **金融機関**: 高セキュリティ要件システムの品質保証
- **自動車業界**: 車載ソフトウェアの安全性確保

### **日本語サポート**
- 日本語での自然言語クエリ対応
- 日本の企業プロキシ環境に最適化
- 日本語ドキュメントとサポート

---

**❤️ ソフトウェアセキュリティコミュニティのために作られました**

*AIの力で静的解析ワークフローを変革しましょう*

## 💫 日本語での使用例

### セキュリティ解析
```
「WebアプリケーションプロジェクトでSQLインジェクションの脆弱性を確認して、修正方法も教えて」
```

### 品質管理
```
「今月のコード品質スコアと先月との比較、改善すべき点をレポートして」
```

### チーム管理
```
「開発チーム別の指摘件数と修正率を集計して、パフォーマンスを評価して」
```