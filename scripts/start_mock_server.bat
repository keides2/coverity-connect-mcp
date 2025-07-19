@echo off
REM Coverity Connect ダミーサーバー起動スクリプト
echo [Starting] Dummy Coverity Connect Server
echo.

REM プロジェクトディレクトリに移動
cd /d "%~dp0\.."
echo [Info] Current directory: %CD%
echo.

REM 必要なパッケージの確認
echo [Check] Checking Flask installation...
python -c "import flask; print('[OK] Flask available')" 2>nul
if errorlevel 1 (
    echo [Error] Flask not found. Installing...
    pip install flask
    if errorlevel 1 (
        echo [Error] Flask installation failed!
        pause
        exit /b 1
    )
)

REM ダミーサーバー起動
echo.
echo [Starting] Dummy Server on http://localhost:5000
echo [Info] Available endpoints:
echo    - http://localhost:5000/          (Status page)
echo    - http://localhost:5000/status    (JSON status)
echo    - SOAP APIs for testing
echo.
echo [Warning] Press Ctrl+C to stop the server
echo.

python examples\development\mock_server.py

pause
