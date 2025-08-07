@echo off
setlocal enabledelayedexpansion

echo ================================
echo Coverity Connect MCP Server
echo Production Deployment Script
echo ================================
echo.

REM ディレクトリ確認
if not exist ".\src\coverity_mcp_server" (
    echo エラー: src\coverity_mcp_serverディレクトリが見つかりません
    pause
    exit /b 1
)

echo ステップ 1: バックアップ作成中...

REM main.py のバックアップ
if exist ".\src\coverity_mcp_server\main.py" (
    copy /Y ".\src\coverity_mcp_server\main.py" ".\src\coverity_mcp_server\main_dev.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo main.py のバックアップ完了
    ) else (
        echo main.py のバックアップ失敗
        pause
        exit /b 1
    )
) else (
    echo main.py が見つかりません
    pause
    exit /b 1
)

REM coverity_client.py のバックアップ
if exist ".\src\coverity_mcp_server\coverity_client.py" (
    copy /Y ".\src\coverity_mcp_server\coverity_client.py" ".\src\coverity_mcp_server\coverity_client_dev.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo coverity_client.py のバックアップ完了
    ) else (
        echo coverity_client.py のバックアップ失敗
        pause
        exit /b 1
    )
) else (
    echo coverity_client.py が見つかりません
    pause
    exit /b 1
)

echo.
echo ステップ 2: 本番用ファイルに切り替え中...

REM main_production.py を main.py にコピー
if exist ".\src\coverity_mcp_server\main_production.py" (
    copy /Y ".\src\coverity_mcp_server\main_production.py" ".\src\coverity_mcp_server\main.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo main_production.py を main.py に変更完了
    ) else (
        echo main.py の変更失敗
        pause
        exit /b 1
    )
) else (
    echo main_production.py が見つかりません
    pause
    exit /b 1
)

REM coverity_client_production.py を coverity_client.py にコピー
if exist ".\src\coverity_mcp_server\coverity_client_production.py" (
    copy /Y ".\src\coverity_mcp_server\coverity_client_production.py" ".\src\coverity_mcp_server\coverity_client.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo coverity_client_production.py を coverity_client.py に変更完了
    ) else (
        echo coverity_client.py の変更失敗
        pause
        exit /b 1
    )
) else (
    echo coverity_client_production.py が見つかりません
    pause
    exit /b 1
)

echo 処理が完了しました。
pause