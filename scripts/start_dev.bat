@echo off
REM Coverity Connect MCP Server - �J�����N���X�N���v�g
echo [Starting] Coverity Connect MCP Server (Development Mode)
echo.

REM ���ϐ��ݒ�
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

REM �v���W�F�N�g�f�B���N�g���Ɉړ�
cd /d "%~dp0\.."
echo [Info] Current directory: %CD%
echo.

REM ���z���̊m�F
python -c "import sys; print('Python:', sys.executable)"
echo.

REM �p�b�P�[�W�̃C���X�g�[���m�F
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

REM MCP�T�[�o�[�N��
echo.
echo [Starting] MCP Server...
echo [Warning] Press Ctrl+C to stop the server
echo.
python -m coverity_mcp_server

pause
