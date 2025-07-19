@echo off
REM Coverity Connect MCP Server - 開発環境起動スクリプト
echo [Starting] Coverity Connect MCP Server (Development Mode)
echo.

REM 環境変数設定
echo [Setting] Development environment variables...
set COVERITY_HOST=localhost
set COVERITY_PORT=5000
set COVERITY_SSL=False
set COVAUTHUSER=dummy_user
set COVAUTHKEY=dummy_key
set MCP_DEBUG=True
set LOG_LEVEL=DEBUG

echo [OK] Environment variables set:
echo    COVERITY_HOST=%COVERITY_HOST%
echo    COVERITY_PORT=%COVERITY_PORT%
echo    COVERITY_SSL=%COVERITY_SSL%
echo    COVAUTHUSER=%COVAUTHUSER%
echo.

REM プロジェクトディレクトリに移動
cd /d "%~dp0\.."
echo [Info] Current directory: %CD%
echo.

REM 仮想環境の確認
python -c "import sys; print('Python:', sys.executable)"
echo.

REM パッケージのインストール確認
echo [Check] Checking package installation...
python -c "import coverity_mcp_server; print('[OK] Package imported successfully')" 2>nul
if errorlevel 1 (
    echo [Error] Package not found. Installing...
    pip install -e .
    if errorlevel 1 (
        echo [Error] Installation failed!
        pause
        exit /b 1
    )
)

REM MCPサーバー起動
echo.
echo [Starting] MCP Server...
echo [Warning] Press Ctrl+C to stop the server
echo.
python -m coverity_mcp_server

pause
