# Coverity Connect MCP Python パッケージ配布手順書

## プロジェクト概要

- **パッケージ名**: coverity-connect-mcp
- **現在のバージョン**: v1.0.2
- **リポジトリ**: https://github.com/keides2/coverity-connect-mcp
- **目的**: GitHub PackagesでのPythonパッケージ配布設定

## 完了した作業ステップ

### ステップ1-6: 初期確認とリリース準備

1. **既存リリース状況確認**
   - GitHubでの現在のリリース・タグ状況を確認
   - 既存のv1.0.0リリースを確認

2. **DXTパッケージ内容確認**
   - coverity-connect-mcp-1.0.0.dxtの中身をチェック
   - パッケージ構成の理解

3. **ソースコード確認**
   - dxt-packageディレクトリの内容確認
   - プロジェクト構造の把握

4. **v1.0.1バージョンアップ**
   ```bash
   # pyproject.tomlのバージョン更新
   version = "1.0.0" → "1.0.1"
   
   # コミットとタグ作成
   git add pyproject.toml
   git commit -m "feat: Update to v1.0.1 for GitHub Packages distribution"
   git tag -a v1.0.1 -m "Release v1.0.1 - GitHub Packages Distribution"
   git push origin main
   git push origin v1.0.1
   ```

5. **GitHubリリースv1.0.1作成**
   - GitHub WebUIでリリース作成完了

### ステップ7-12: リポジトリクリーンアップ

6. **不要フォルダの整理**
   ```powershell
   # 有用なドキュメントの保存
   Copy-Item "dxt-package\docs\dxt_packaging_guide.md" "docs\" -Force
   
   # フォルダをevacに移動
   Move-Item dxt-clean .\evac\dxt-clean-backup-20250814
   Move-Item dxt-package .\evac\dxt-package-backup-20250814
   ```

7. **.gitignore更新**
   ```gitignore
   dxt-*/
   __pycache__/
   *.log
   temp-*/
   dist/
   build/
   *.egg-info/
   ```

8. **GitHub Actionsワークフロー作成**
   - `.github/workflows/publish.yml`作成
   - リリース時の自動パッケージ公開設定

### ステップ13-18: パッケージビルドとテスト

9. **ビルドツールのインストール**
   ```bash
   pip install build twine
   ```

10. **パッケージビルド実行**
    ```bash
    python -m build
    ```
    **成果物**:
    - `coverity_connect_mcp-1.0.1-py3-none-any.whl` (39KB)
    - `coverity_connect_mcp-1.0.1.tar.gz` (12MB)

11. **パッケージ検証**
    ```bash
    # 内容確認
    python -m zipfile -l dist\coverity_connect_mcp-1.0.1-py3-none-any.whl
    
    # 品質チェック
    twine check dist/*
    # 結果: PASSED
    ```

12. **v1.0.2バージョンアップ**
    ```bash
    # バージョン更新
    version = "1.0.1" → "1.0.2"
    
    # コミットとタグ作成
    git commit -m "feat: Update to v1.0.2 for GitHub Packages automated distribution"
    git tag -a v1.0.2 -m "Release v1.0.2 - GitHub Packages Automated Distribution"
    git push origin main
    git push origin v1.0.2
    ```

### ステップ19-23: GitHub Actions設定と問題解決

13. **ワークフロー設定修正**
    - 手動実行機能追加 (`workflow_dispatch`)
    - `TWINE_USERNAME`修正: `**token**` → `__token__`
    - Python版バージョン: 3.8 → 3.10

14. **GitHub Actions実行テスト**
    - 手動実行を試行
    - **結果**: 403 Forbiddenエラー発生

## 現在の問題と解決待ち状況

### 発生した問題

**GitHub Actions実行エラー**:
```
403 Forbidden from https://upload.pypi.org/legacy/
Invalid or non-existent authentication information
```

**原因分析**:
- `GITHUB_TOKEN`はPyPIでは使用不可
- PyPI配布には専用のAPI TOKEN が必要
- 現在の設定はPyPI向けだがGitHub Packages向けに変更が必要

### 解決選択肢

#### 選択肢A: GitHub Packages配布 (推奨)
- **メリット**: GITHUB_TOKENが使用可能、認証問題なし
- **設定**: ワークフローをGitHub Packages用に修正

#### 選択肢B: PyPI配布
- **必要作業**: PyPI_API_TOKEN取得とGitHub Secretsに設定
- **追加手順**: PyPIアカウント作成と認証設定

## プロジェクト技術仕様

### パッケージ構成

```toml
[project]
name = "coverity-connect-mcp"
version = "1.0.2"
description = "Model Context Protocol server for Black Duck Coverity Connect static analysis platform"
requires-python = ">=3.8"
```

### 主要依存関係
```toml
dependencies = [
    "mcp>=1.0.0",
    "aiohttp>=3.8.0",
    "suds-community>=1.1.2",
    "requests>=2.31.0",
    "pandas>=1.5.0",
    "pydantic>=2.0.0",
    "aiofiles>=23.0.0",
    "python-dotenv>=1.0.0",
    "click>=8.0.0",
    "rich>=13.0.0",
    "PyYAML>=6.0",
]
```

### エントリーポイント
```toml
[project.scripts]
coverity-mcp = "coverity_mcp_server.main:cli"
coverity-mcp-server = "coverity_mcp_server.main:run_server"

[project.entry-points."mcp.servers"]
coverity-connect = "coverity_mcp_server.main:create_server"
```

### ビルドシステム
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## 次のステップ

### GitHub Packages配布実装 (推奨)

1. **ワークフロー修正**
   - GitHub Packages用のリポジトリURL設定
   - 認証方法の調整

2. **パッケージ設定調整**
   - GitHub Packages向けの設定追加

3. **配布テスト**
   - 修正後のワークフロー実行
   - パッケージインストールテスト

4. **ユーザー向けドキュメント作成**
   - インストール手順書
   - 使用方法ガイド

## 参考情報

### 重要なファイルパス
- **メインパッケージ**: `src/coverity_mcp_server/`
- **設定ファイル**: `pyproject.toml`
- **ワークフロー**: `.github/workflows/publish.yml`
- **ドキュメント**: `docs/dxt_packaging_guide.md`

### GitHub URLs
- **リポジトリ**: https://github.com/keides2/coverity-connect-mcp
- **リリース**: https://github.com/keides2/coverity-connect-mcp/releases
- **Actions**: https://github.com/keides2/coverity-connect-mcp/actions

---

**作業完了日**: 2025年8月14日  
**次回作業**: GitHub Packages配布設定の実装