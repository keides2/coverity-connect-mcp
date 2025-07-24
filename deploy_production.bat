@echo off
setlocal enabledelayedexpansion

echo ================================
echo Coverity Connect MCP Server
echo Production Deployment Script
echo ================================
echo.

REM �f�B���N�g���m�F
if not exist ".\src\coverity_mcp_server" (
    echo �G���[: src\coverity_mcp_server�f�B���N�g����������܂���
    pause
    exit /b 1
)

echo �X�e�b�v 1: �o�b�N�A�b�v�쐬��...

REM main.py �̃o�b�N�A�b�v
if exist ".\src\coverity_mcp_server\main.py" (
    copy /Y ".\src\coverity_mcp_server\main.py" ".\src\coverity_mcp_server\main_dev.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo main.py �̃o�b�N�A�b�v����
    ) else (
        echo main.py �̃o�b�N�A�b�v���s
        pause
        exit /b 1
    )
) else (
    echo main.py ��������܂���
    pause
    exit /b 1
)

REM coverity_client.py �̃o�b�N�A�b�v
if exist ".\src\coverity_mcp_server\coverity_client.py" (
    copy /Y ".\src\coverity_mcp_server\coverity_client.py" ".\src\coverity_mcp_server\coverity_client_dev.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo coverity_client.py �̃o�b�N�A�b�v����
    ) else (
        echo coverity_client.py �̃o�b�N�A�b�v���s
        pause
        exit /b 1
    )
) else (
    echo coverity_client.py ��������܂���
    pause
    exit /b 1
)

echo.
echo �X�e�b�v 2: �{�ԗp�t�@�C���ɐ؂�ւ���...

REM main_production.py �� main.py �ɃR�s�[
if exist ".\src\coverity_mcp_server\main_production.py" (
    copy /Y ".\src\coverity_mcp_server\main_production.py" ".\src\coverity_mcp_server\main.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo main_production.py �� main.py �ɕύX����
    ) else (
        echo main.py �̕ύX���s
        pause
        exit /b 1
    )
) else (
    echo main_production.py ��������܂���
    pause
    exit /b 1
)

REM coverity_client_production.py �� coverity_client.py �ɃR�s�[
if exist ".\src\coverity_mcp_server\coverity_client_production.py" (
    copy /Y ".\src\coverity_mcp_server\coverity_client_production.py" ".\src\coverity_mcp_server\coverity_client.py" >nul
    if !ERRORLEVEL! EQU 0 (
        echo coverity_client_production.py �� coverity_client.py �ɕύX����
    ) else (
        echo coverity_client.py �̕ύX���s
        pause
        exit /b 1
    )
) else (
    echo coverity_client_production.py ��������܂���
    pause
    exit /b 1
)

echo �������������܂����B
pause