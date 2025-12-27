# coverity-connect-mcp 統合作業計画

## 作業完了済み

### 1. バージョン比較 ✅
- Security側: 1.0.0 (独自のSecurity固有ファイルあり)
- mcp-servers側: 1.0.0 (標準版)

### 2. バックアップ完了 ✅
バックアップ場所: `backup_20250810_092555/`
- logs/ (実行ログ)
- evac/ (機能比較分析文書)
- deploy_production.bat
- setup_env_template.bat
- security_src/ (Security固有ソースコード)

## Security側独自ファイル

以下のファイルはSecurity環境で独自に開発/カスタマイズされたもの：

### Production運用関連
- `deploy_production.bat` - 本番デプロイスクリプト
- `setup_env_template.bat` - 環境設定テンプレート
- `logs/coverity_mcp_server.log` - 実行ログ

### ドキュメントと分析
- `evac/cov_auto cov_snap vs mcp 機能比較分析.pdf`
- `evac/feature_comparison_analysis_covauto_covsnap.md`
- `evac/main-readme.md`

### Security固有ソースコード
- `src/coverity_mcp_server/coverity_client_production_security_fixed.py`
- `src/coverity_mcp_server/coverity_client_security_fixed.py`
- `src/coverity_mcp_server/main_security_fixed.py`

## 統合戦略

### 推奨アクション
1. **Security側を主Version**として保持
2. **mcp-servers側**に統合移動
3. **重複解消**により統一管理を実現

### 移動手順 (ユーザー実行)
```bash
# 1. mcp-servers側の既存ディレクトリをリネーム
cd "C:\Users\HP\mcp-servers"
mv coverity-connect-mcp coverity-connect-mcp-original

# 2. Security側を移動
mv "C:\Users\HP\Docs\Security\coverity-connect-mcp" "C:\Users\HP\mcp-servers\coverity-connect-mcp"

# 3. 必要に応じてoriginalから不足ファイルを統合
# (例: claude_desktop_config.lnk など)
```

## 検証項目

統合後に確認すべき事項：
1. MCP サーバー起動確認
2. Claude Desktop での接続テスト
3. Coverity Connect API接続確認
4. ログ出力確認

## 注意事項

- 現在実行中のMCPプロセスがある場合は事前停止が必要
- Claude Desktop設定ファイルのパス更新が必要な場合あり
- Security固有の設定が他の環境で正常動作するかの確認が必要

---
*統合作業日: 2025-08-10*