@echo off
REM Coverity Connect MCP Server - Environment Variables Setup
REM このスクリプトは必要な環境変数を設定します（テンプレート）

echo ================================
echo Coverity Connect MCP Server
echo Environment Variables Setup
echo ================================
echo.

echo 重要: このファイルを編集して実際の認証情報を設定してください
echo このファイルはGitHubにプッシュしないでください！
echo.

REM TODO: 以下の値を実際の設定に変更してください
REM 注意: このファイルは.gitignoreに追加してGitHubにプッシュされないようにしてください

REM Coverity Connect サーバーURL
set COVERITY_HOST=https://your-coverity-server.com

REM Coverity Connect 認証情報（実際の値に変更してください）
set COVAUTHUSER=your_username_here
set COVAUTHKEY=your_password_here

REM プロキシ設定
set HTTPS_PROXY=http://your-proxy-server.com:3128
set HTTP_PROXY=http://your-proxy-server.com:3128

REM または、カスタムプロキシ設定を使用する場合
set PROXY_HOST=your-proxy-server.com
set PROXY_PORT=3128

echo 環境変数が設定されました:
echo   COVERITY_HOST=%COVERITY_HOST%
echo   COVAUTHUSER=%COVAUTHUSER%
echo   COVAUTHKEY=***
echo   HTTPS_PROXY=%HTTPS_PROXY%
echo.

echo サーバーを起動するには以下のコマンドを実行してください:
echo   python -m src.coverity_mcp_server.main
echo.

REM サーバーを自動起動する場合は以下の行のコメントを外してください
REM python -m src.coverity_mcp_server.main

pause
