@echo off
REM Coverity Connect MCP Server - Production Deployment Script
REM このスクリプトは開発用ファイルを本番用ファイルに置き換えます

echo ================================
echo Coverity Connect MCP Server
echo Production Deployment Script
echo ================================
echo.

REM 現在のディレクトリを確認
if not exist "src\coverity_mcp_server" (
    echo エラー: src\coverity_mcp_serverディレクトリが見つかりません
    echo このスクリプトはプロジェクトのルートディレクトリで実行してください
    pause
    exit /b 1
)

echo ステップ 1: 現在のファイルをバックアップ中...

REM 開発用ファイルをバックアップ
if exist "src\coverity_mcp_server\main.py" (
    copy "src\coverity_mcp_server\main.py" "src\coverity_mcp_server\main_dev.py"
    echo   main.py -> main_dev.py (バックアップ完了)
)

if exist "src\coverity_mcp_server\coverity_client.py" (
    copy "src\coverity_mcp_server\coverity_client.py" "src\coverity_mcp_server\coverity_client_dev.py"
    echo   coverity_client.py -> coverity_client_dev.py (バックアップ完了)
)

echo ステップ 2: 本番用ファイルをメインファイルに変更中...

REM 本番用ファイルをメインファイルとしてコピー
if exist "src\coverity_mcp_server\main_production.py" (
    copy "src\coverity_mcp_server\main_production.py" "src\coverity_mcp_server\main.py"
    echo   main_production.py -> main.py (本番用ファイルに変更完了)
) else (
    echo エラー: main_production.py が見つかりません
    pause
    exit /b 1
)

if exist "src\coverity_mcp_server\coverity_client_production.py" (
    copy "src\coverity_mcp_server\coverity_client_production.py" "src\coverity_mcp_server\coverity_client.py"
    echo   coverity_client_production.py -> coverity_client.py (本番用ファイルに変更完了)
) else (
    echo エラー: coverity_client_production.py が見つかりません
    pause
    exit /b 1
)

echo.
echo ================================
echo デプロイメント完了!
echo ================================
echo.
echo 次のステップ:
echo 1. 必要な環境変数を設定してください:
echo    set COVERITY_HOST=https://sast.kbit-repo.net
echo    set COVAUTHUSER=your_username
echo    set COVAUTHKEY=your_password
echo    set HTTPS_PROXY=http://bypsproxy.daikin.co.jp:3128
echo.
echo 2. 動作確認を実行してください:
echo    python -m src.coverity_mcp_server.main
echo.
echo 3. GitHubにプッシュしてください:
echo    git add .
echo    git commit -m "Deploy production version with environment variables"
echo    git push
echo.

pause
