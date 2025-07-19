# 本番環境デプロイガイド

このディレクトリには、Coverity Connect MCP Serverの本番環境用設定が含まれています。

## 🎯 概要

本番環境では、実際のCoverity Connectサーバーに接続してセキュアな運用を行います。

## 📁 ファイル構成

```
production/
├── .env.production               # 本番環境変数テンプレート
├── claude_desktop_config.json   # Claude Desktop設定（本番用）
└── README_prod.md                # このファイル
```

## 🚀 本番デプロイ手順

### 1. 環境準備

#### Python環境のセットアップ
```bash
# 本番用Python環境
python -m venv /opt/coverity-mcp
source /opt/coverity-mcp/bin/activate

# パッケージインストール
pip install -e .
```

### 2. 設定ファイルの準備

#### 環境変数の設定
```bash
# .env.productionをコピーして編集
cp .env.production /opt/coverity-mcp/.env
nano /opt/coverity-mcp/.env

# 必須項目を実際の値に置換:
# - COVERITY_HOST: 実際のCoverityサーバー
# - COVAUTHUSER: 実際のユーザー名
# - COVAUTHKEY: 実際の認証キー
```

#### セキュリティ設定
```bash
# 環境ファイルの権限設定
chmod 600 /opt/coverity-mcp/.env
chown mcp-user:mcp-user /opt/coverity-mcp/.env
```

### 3. systemd サービス設定

#### サービスファイル作成
```bash
sudo nano /etc/systemd/system/coverity-mcp.service
```

```ini
[Unit]
Description=Coverity Connect MCP Server
After=network.target

[Service]
Type=simple
User=mcp-user
Group=mcp-user
WorkingDirectory=/opt/coverity-mcp
Environment=PATH=/opt/coverity-mcp/bin
EnvironmentFile=/opt/coverity-mcp/.env
ExecStart=/opt/coverity-mcp/bin/python -m coverity_mcp_server
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

# セキュリティ設定
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/coverity-mcp
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

#### サービス有効化
```bash
sudo systemctl daemon-reload
sudo systemctl enable coverity-mcp
sudo systemctl start coverity-mcp
```

### 4. Claude Desktop設定

#### 設定ファイルの更新
本番用設定を適用：

```json
{
  "mcpServers": {
    "coverity-connect": {
      "command": "python",
      "args": ["-m", "coverity_mcp_server"],
      "cwd": "/opt/coverity-mcp",
      "env": {
        "COVERITY_HOST": "your-coverity-server.company.com",
        "COVERITY_PORT": "8080",
        "COVERITY_SSL": "True",
        "COVAUTHUSER": "your-username",
        "COVAUTHKEY": "your-auth-key",
        "MCP_DEBUG": "False",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 5. 本番環境テスト

#### 接続テスト
```bash
# 基本テスト
python -c "from coverity_mcp_server.coverity_client import CoverityClient; print('Import OK')"

# 実際の接続テスト
curl -k https://your-coverity-server:8080/ws/v9/configurationservice?wsdl
```

#### Claude Desktop統合テスト
Claude Desktopで実際のCoverityデータにアクセス：
```
実際のCoverityプロジェクト一覧を表示してください
```

## 🔒 セキュリティ設定

### 認証情報の管理
```bash
# 環境変数の暗号化保存（推奨）
echo "COVAUTHKEY=your-key" | gpg --symmetric --armor > /opt/coverity-mcp/.env.gpg

# または secure vault使用
vault kv put secret/coverity-mcp \
  username=your-user \
  authkey=your-key
```

### SSL/TLS設定
```bash
# 証明書の確認
openssl s_client -connect your-coverity-server:8080 -showcerts

# SSL検証設定
export SSL_VERIFY=True
export SSL_CERT_PATH=/etc/ssl/certs/ca-certificates.crt
```

### ファイアウォール設定
```bash
# 必要なポートのみ開放
sudo ufw allow from trusted-ip-range to any port 8080
sudo ufw deny 8080
```

## 📊 監視・ログ設定

### ログ設定
```bash
# ログディレクトリ作成
sudo mkdir -p /var/log/coverity-mcp
sudo chown mcp-user:mcp-user /var/log/coverity-mcp

# logrotate設定
sudo nano /etc/logrotate.d/coverity-mcp
```

```conf
/var/log/coverity-mcp/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su mcp-user mcp-user
}
```

### ヘルスチェック
```bash
# ヘルスチェックスクリプト作成
nano /opt/coverity-mcp/health_check.sh
```

```bash
#!/bin/bash
# Coverity MCP Server Health Check

LOG_FILE="/var/log/coverity-mcp/health.log"
STATUS_URL="http://localhost:8080/health"

# サービスステータス確認
if systemctl is-active --quiet coverity-mcp; then
    echo "$(date): Service is running" >> $LOG_FILE
else
    echo "$(date): Service is down - restarting" >> $LOG_FILE
    systemctl restart coverity-mcp
fi

# プロセス確認
if pgrep -f "coverity_mcp_server" > /dev/null; then
    echo "$(date): Process is active" >> $LOG_FILE
else
    echo "$(date): Process not found" >> $LOG_FILE
fi
```

```bash
# 実行権限付与
chmod +x /opt/coverity-mcp/health_check.sh

# cron設定
echo "*/5 * * * * /opt/coverity-mcp/health_check.sh" | crontab -
```

## 🔧 パフォーマンス最適化

### メモリ設定
```bash
# Python メモリ制限
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2

# systemdでの制限
sudo systemctl edit coverity-mcp
```

```ini
[Service]
MemoryLimit=512M
CPUQuota=50%
```

### 接続プール設定
```python
# 設定ファイルで調整
AIOHTTP_CONNECTOR_LIMIT = 10
AIOHTTP_TIMEOUT = 30
COVERITY_REQUEST_TIMEOUT = 60
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. Coverity Connect接続エラー
```bash
# SSL証明書問題
export PYTHONHTTPSVERIFY=0  # 一時的な回避（非推奨）

# 正しい解決方法
curl -k https://your-server:8080/cert.pem > /opt/coverity-mcp/server.crt
export SSL_CA_BUNDLE=/opt/coverity-mcp/server.crt
```

#### 2. 認証エラー
```bash
# 認証情報確認
echo $COVAUTHUSER
echo $COVAUTHKEY

# Coverity側での確認
covadmin --host your-server --port 8080 --user $COVAUTHUSER list-projects
```

#### 3. パフォーマンス問題
```bash
# メモリ使用量確認
ps aux | grep coverity_mcp_server

# ログレベル調整
export LOG_LEVEL=WARNING

# 接続数制限
export MAX_CONNECTIONS=5
```

#### 4. systemd サービス問題
```bash
# ログ確認
sudo journalctl -u coverity-mcp -f

# サービス再起動
sudo systemctl restart coverity-mcp

# 設定リロード
sudo systemctl daemon-reload
```

## 📈 運用監視

### メトリクス収集
```bash
# プロセス監視
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | grep coverity

# ネットワーク監視
netstat -an | grep :8080

# ディスク使用量
du -sh /opt/coverity-mcp/
```

### アラート設定
```bash
# メール通知設定
echo "coverity-mcp service failed" | mail -s "Alert" admin@company.com

# Slack通知（webhook使用）
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Coverity MCP service alert"}' \
  YOUR_SLACK_WEBHOOK_URL
```

## 🔄 バックアップ・復旧

### 設定バックアップ
```bash
# 設定ファイルバックアップ
tar -czf coverity-mcp-config-$(date +%Y%m%d).tar.gz \
  /opt/coverity-mcp/.env \
  /etc/systemd/system/coverity-mcp.service \
  ~/.config/claude/claude_desktop_config.json
```

### 災害復旧手順
```bash
# 1. Python環境復旧
python -m venv /opt/coverity-mcp
source /opt/coverity-mcp/bin/activate
pip install -e .

# 2. 設定復旧
tar -xzf coverity-mcp-config-backup.tar.gz -C /

# 3. サービス復旧
sudo systemctl daemon-reload
sudo systemctl enable coverity-mcp
sudo systemctl start coverity-mcp
```

## 📋 チェックリスト

### デプロイ前チェック
- [ ] Python環境準備完了
- [ ] 認証情報設定済み
- [ ] SSL証明書確認済み
- [ ] ファイアウォール設定済み
- [ ] systemdサービス設定済み

### デプロイ後チェック
- [ ] サービス正常起動確認
- [ ] Claude Desktop接続確認
- [ ] 実データアクセス確認
- [ ] ログ出力確認
- [ ] ヘルスチェック動作確認

### 運用チェック
- [ ] 定期ヘルスチェック設定
- [ ] ログローテーション設定
- [ ] バックアップスケジュール設定
- [ ] 監視アラート設定
- [ ] 災害復旧手順確認

## 📞 エスカレーション

### 緊急時連絡先
- **システム管理者**: admin@company.com
- **Coverity管理者**: coverity-admin@company.com
- **開発チーム**: dev-team@company.com

### サポートチャネル
- **GitHub Issues**: https://github.com/keides2/coverity-connect-mcp/issues
- **社内Slack**: #coverity-mcp-support
- **ドキュメント**: 統合セットアップガイド (SETUP_GUIDE.md)

---

**重要**: 本番環境では機密情報を適切に保護し、セキュリティガイドラインに従ってください。

**更新日**: 2025年7月19日  
**バージョン**: 1.0.0