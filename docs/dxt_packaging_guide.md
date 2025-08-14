# DXTパッケージ化手順書
**MCPサーバーをClaude Desktop用DXTパッケージ化する完全ガイド**

## 📋 前提条件

### 必要なツール
- **Node.js**: v16以上
- **Python**: 3.8以上
- **DXTツールチェーン**: `npm install -g @anthropic-ai/dxt`
- **Git**: バージョン管理用

### 対象プロジェクト要件
- MCPサーバーとして動作するPythonプロジェクト
- `pyproject.toml`または`setup.py`が存在
- `requirements.txt`が存在

## 🚀 手順1: プロジェクト分析

### 1.1 プロジェクト構造の確認
```powershell
# プロジェクトディレクトリで実行
tree /F

# 重要ファイルの確認
ls pyproject.toml, requirements.txt, src/
```

### 1.2 依存関係の確認
```powershell
# pyproject.tomlの内容確認
Get-Content pyproject.toml

# requirements.txtの内容確認
Get-Content requirements.txt
```

### 1.3 エントリーポイントの特定
```powershell
# main.pyの関数定義を確認
Get-Content src/*/main.py | Select-String "def "

# __main__.pyの確認
Get-Content src/*/__main__.py

# pyproject.tomlのエントリーポイント確認
Get-Content pyproject.toml | Select-String "entry-points\|scripts"
```

**重要なチェックポイント**:
- [ ] `main.py`に実行可能な関数がある
- [ ] 相対インポートが使用されている
- [ ] MCPサーバーとして動作する

## 🔧 手順2: DXT用ディレクトリの準備

### 2.1 クリーンなディレクトリの作成
```powershell
# プロジェクトルートで実行
mkdir dxt-clean
cd dxt-clean
```

### 2.2 必要ファイルのコピー
```powershell
# 必須ファイルをコピー
Copy-Item -Recurse ..\src .\
Copy-Item ..\requirements.txt .\
Copy-Item ..\README.md .\
Copy-Item ..\LICENSE .\
Copy-Item ..\pyproject.toml .\

# .env.example があれば参考用にコピー
Copy-Item ..\.env.example .\ -ErrorAction SilentlyContinue
```

### 2.3 ディレクトリ構造の確認
```powershell
tree /F
```

**期待される構造**:
```
dxt-clean/
├── manifest.json (次のステップで作成)
├── src/
│   └── [パッケージ名]/
│       ├── __init__.py
│       ├── main.py
│       └── その他のPythonファイル
├── requirements.txt
├── README.md
├── LICENSE
└── pyproject.toml
```

## 📄 手順3: manifest.jsonの作成

### 3.1 DXTサンプルの確認
```powershell
# 一時ディレクトリでDXTサンプル生成
mkdir temp-sample
cd temp-sample
dxt init -y
Get-Content manifest.json
cd ..
Remove-Item -Recurse temp-sample
```

### 3.2 manifest.jsonテンプレート
メモ帳で`manifest.json`を作成：

```json
{
  "dxt_version": "0.1",
  "name": "[パッケージ名]",
  "version": "[バージョン番号]",
  "description": "[説明文]",
  "author": {
    "name": "[作者名]",
    "email": "[メールアドレス]"
  },
  "server": {
    "type": "python",
    "entry_point": "src/[パッケージ名]/main.py",
    "mcp_config": {
      "command": "python",
      "args": [
        "${__dirname}/src/[パッケージ名]/main.py"
      ],
      "env": {
        "[環境変数名1]": "${[環境変数名1]}",
        "[環境変数名2]": "${[環境変数名2]}"
      }
    }
  },
  "license": "MIT"
}
```

### 3.3 実際の値の設定
**置換が必要な項目**:
- `[パッケージ名]`: 実際のPythonパッケージ名
- `[バージョン番号]`: pyproject.tomlから取得
- `[説明文]`: プロジェクトの説明
- `[作者名]`, `[メールアドレス]`: 作者情報
- `[環境変数名]`: 必要な環境変数

## ✅ 手順4: DXTパッケージの検証とビルド

### 4.1 manifest.jsonの検証
```powershell
dxt validate manifest.json
```

**エラーが出た場合の対処**:
- JSON構文エラー → メモ帳で再作成
- 必須フィールド不足 → DXTサンプルと比較
- 認識されないキー → DXT仕様書確認

### 4.2 DXTパッケージのビルド
```powershell
dxt pack
```

**成功の確認**:
- ファイルサイズが適切（数十KB～数百KB）
- エラーメッセージがない
- `.dxt`ファイルが生成される

### 4.3 パッケージ内容の確認
```powershell
# DXTファイルをZIPとして展開して確認
Copy-Item "[パッケージ名].dxt" "[パッケージ名].zip"
Expand-Archive -Path "[パッケージ名].zip" -DestinationPath "verify" -Force
tree verify /F
```

## 🧪 手順5: Claude Desktopでのテスト

### 5.1 設定ファイルのバックアップ
```powershell
Copy-Item "$env:APPDATA\Claude\claude_desktop_config.json" "$env:APPDATA\Claude\claude_desktop_config.json.backup"
```

### 5.2 Python実行環境の確認
```powershell
# 利用可能なPythonコマンドを確認
python3 --version
python --version
where python3
```

### 5.3 テスト用設定の追加
`claude_desktop_config.json`に以下を追加：

```json
"[パッケージ名]-dxt": {
  "command": "python3",
  "args": ["-m", "[パッケージ名].main"],
  "cwd": "[DXTパッケージ展開パス]/src",
  "env": {
    "PYTHONPATH": "[DXTパッケージ展開パス]/src",
    "[環境変数名1]": "[テスト値1]",
    "[環境変数名2]": "[テスト値2]"
  }
}
```

### 5.4 Claude Desktopでのテスト
1. Claude Desktopを再起動
2. 新しいチャットで接続確認
3. ツール一覧の確認
4. 基本機能のテスト

### 5.5 設定の復元
```powershell
Copy-Item "$env:APPDATA\Claude\claude_desktop_config.json.backup" "$env:APPDATA\Claude\claude_desktop_config.json"
```

## 📦 手順6: 最終パッケージの作成

### 6.1 最適化されたパッケージの再作成
```powershell
# 不要ファイルの削除
Remove-Item -Recurse verify -ErrorAction SilentlyContinue
Remove-Item "[パッケージ名].zip" -ErrorAction SilentlyContinue

# 最終パッケージの作成
dxt pack
```

### 6.2 最終確認
```powershell
# ファイルサイズとSHAの確認
Get-ChildItem *.dxt | Format-Table Name, Length, LastWriteTime
```

## 🚀 手順7: GitHubリリース

### 7.1 リリースタグの作成
```powershell
# プロジェクトルートで実行
cd ..
Copy-Item "dxt-clean\[パッケージ名].dxt" "[パッケージ名]-[バージョン].dxt"

git tag -a v[バージョン]-dxt -m "DXT Package Release v[バージョン] - Claude Desktop one-click installation"
git push origin v[バージョン]-dxt
```

### 7.2 GitHubリリースページの作成
1. GitHubのReleasesページにアクセス
2. "Create a new release"をクリック
3. タグ`v[バージョン]-dxt`を選択
4. リリースタイトルとDescription入力
5. DXTファイルをアップロード
6. "Publish release"をクリック

### 7.3 リリースDescriptionテンプレート
```markdown
# 🎉 [プロジェクト名] DXT Package

Claude Desktop用のワンクリックインストール対応バージョンです。  
One-click installation package for Claude Desktop.

## 📦 DXTパッケージの特徴 / Features
- **ワンクリックインストール / One-Click Installation**: 複雑な設定が不要 / No complex configuration required
- **依存関係自動解決 / Automatic Dependencies**: Python環境の構築不要 / No Python environment setup needed  
- **セキュアな設定 / Secure Configuration**: 認証情報をOSキーチェーンで安全管理 / Safe credential storage in OS keychain

## 🚀 インストール方法 / Installation
1. `[パッケージ名]-[バージョン].dxt`をダウンロード / Download the DXT file
2. Claude Desktopの設定画面から拡張機能をインストール / Install extension from Claude Desktop settings
3. 必要な認証情報を設定 / Configure required credentials

## 📋 動作確認済み環境 / Tested Environment
- Windows 10/11
- Claude Desktop v0.12.55+
- Python 3.8+

## 📚 ドキュメント / Documentation
詳細はREADMEをご確認ください。 / See README for detailed instructions.
```

## 🛠️ トラブルシューティング

### よくある問題と解決方法

#### 1. 相対インポートエラー
```
ImportError: attempted relative import with no known parent package
```
**解決策**: 
- モジュール実行方式を使用: `python -m パッケージ名.main`
- `PYTHONPATH`を設定
- `cwd`をsrcディレクトリに設定

#### 2. Python実行エラー
```
spawn python ENOENT
```
**解決策**:
- `python3`コマンドを使用
- Pythonの正確なパスを確認: `where python3`

#### 3. manifest.json検証エラー
```
ERROR: Invalid JSON in manifest file
```
**解決策**:
- メモ帳でUTF-8として保存
- JSON構文の確認
- DXTサンプルとの比較

#### 4. パッケージサイズ過大
**解決策**:
- 不要ファイルの除去
- `extracted-dxt`等の一時ファイル削除
- `.dxtignore`ファイルの活用

#### 5. Claude Desktop認識エラー
**解決策**:
- Claude Desktopの完全再起動
- 設定ファイルの構文確認
- ログファイルの確認

## 📚 参考資料

- [DXT公式ドキュメント](https://mcp.so/dxt)
- [MCP仕様書](https://modelcontextprotocol.io/)
- [Claude Desktop設定ガイド](https://docs.anthropic.com/)

## ✅ チェックリスト

### 作業前確認
- [ ] Node.js, Python, DXTツールチェーンがインストール済み
- [ ] プロジェクトが正常に動作する
- [ ] pyproject.toml, requirements.txtが存在

### パッケージ作成
- [ ] クリーンなディレクトリで作業
- [ ] 必要ファイルのみをコピー
- [ ] manifest.jsonを正しく作成
- [ ] `dxt validate`でエラーなし
- [ ] `dxt pack`でパッケージ生成成功

### テスト実施
- [ ] DXTパッケージの展開確認
- [ ] Claude Desktopでの動作確認
- [ ] 基本機能のテスト完了
- [ ] 設定ファイルの復元

### リリース作業
- [ ] 最終パッケージの作成
- [ ] GitHubタグの作成とプッシュ
- [ ] リリースページの作成
- [ ] DXTファイルのアップロード
- [ ] リリースの公開

---

**作成日**: 2025/08/10  
**対象**: MCPサーバーのDXTパッケージ化  
**動作確認**: Windows 10/11 + Claude Desktop v0.12.55