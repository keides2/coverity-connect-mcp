@echo off
echo [Legacy] Coverity MCP Server Local Testing
echo =====================================
echo.

REM テスト環境変数設定
set COVERITY_HOST=localhost
set COVERITY_PORT=5000
set COVERITY_SSL=False
set COVAUTHUSER=dummy_user
set COVAUTHKEY=dummy_key
set LOG_LEVEL=DEBUG

echo [Info] Test Configuration:
echo   COVERITY_HOST=%COVERITY_HOST%
echo   COVERITY_PORT=%COVERITY_PORT%
echo   COVERITY_SSL=%COVERITY_SSL%
echo   COVAUTHUSER=%COVAUTHUSER%
echo   LOG_LEVEL=%LOG_LEVEL%
echo.

echo [Starting] MCP Server Test...
echo Make sure dummy server is running at http://localhost:5000
echo.

REM MCPサーバーテスト実行
python -m coverity_mcp_server.main

pause