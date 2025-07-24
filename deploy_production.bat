@echo off
REM Coverity Connect MCP Server - Production Deployment Script
REM ���̃X�N���v�g�͊J���p�t�@�C����{�ԗp�t�@�C���ɒu�������܂�

echo ================================
echo Coverity Connect MCP Server
echo Production Deployment Script
echo ================================
echo.

REM ���݂̃f�B���N�g�����m�F
if not exist "src\coverity_mcp_server" (
    echo �G���[: src\coverity_mcp_server�f�B���N�g����������܂���
    echo ���̃X�N���v�g�̓v���W�F�N�g�̃��[�g�f�B���N�g���Ŏ��s���Ă�������
    pause
    exit /b 1
)

echo �X�e�b�v 1: ���݂̃t�@�C�����o�b�N�A�b�v��...

REM �J���p�t�@�C�����o�b�N�A�b�v
if exist "src\coverity_mcp_server\main.py" (
    copy "src\coverity_mcp_server\main.py" "src\coverity_mcp_server\main_dev.py"
    echo   main.py -> main_dev.py (�o�b�N�A�b�v����)
)

if exist "src\coverity_mcp_server\coverity_client.py" (
    copy "src\coverity_mcp_server\coverity_client.py" "src\coverity_mcp_server\coverity_client_dev.py"
    echo   coverity_client.py -> coverity_client_dev.py (�o�b�N�A�b�v����)
)

echo �X�e�b�v 2: �{�ԗp�t�@�C�������C���t�@�C���ɕύX��...

REM �{�ԗp�t�@�C�������C���t�@�C���Ƃ��ăR�s�[
if exist "src\coverity_mcp_server\main_production.py" (
    copy "src\coverity_mcp_server\main_production.py" "src\coverity_mcp_server\main.py"
    echo   main_production.py -> main.py (�{�ԗp�t�@�C���ɕύX����)
) else (
    echo �G���[: main_production.py ��������܂���
    pause
    exit /b 1
)

if exist "src\coverity_mcp_server\coverity_client_production.py" (
    copy "src\coverity_mcp_server\coverity_client_production.py" "src\coverity_mcp_server\coverity_client.py"
    echo   coverity_client_production.py -> coverity_client.py (�{�ԗp�t�@�C���ɕύX����)
) else (
    echo �G���[: coverity_client_production.py ��������܂���
    pause
    exit /b 1
)

echo.
echo ================================
echo �f�v���C�����g����!
echo ================================
echo.
echo ���̃X�e�b�v:
echo 1. �K�v�Ȋ��ϐ���ݒ肵�Ă�������:
echo    set COVERITY_HOST=https://sast.kbit-repo.net
echo    set COVAUTHUSER=your_username
echo    set COVAUTHKEY=your_password
echo    set HTTPS_PROXY=http://bypsproxy.daikin.co.jp:3128
echo.
echo 2. ����m�F�����s���Ă�������:
echo    python -m src.coverity_mcp_server.main
echo.
echo 3. GitHub�Ƀv�b�V�����Ă�������:
echo    git add .
echo    git commit -m "Deploy production version with environment variables"
echo    git push
echo.

pause
