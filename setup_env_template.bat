@echo off
REM Coverity Connect MCP Server - Environment Variables Setup
REM ���̃X�N���v�g�͕K�v�Ȋ��ϐ���ݒ肵�܂��i�e���v���[�g�j

echo ================================
echo Coverity Connect MCP Server
echo Environment Variables Setup
echo ================================
echo.

echo �d�v: ���̃t�@�C����ҏW���Ď��ۂ̔F�؏���ݒ肵�Ă�������
echo ���̃t�@�C����GitHub�Ƀv�b�V�����Ȃ��ł��������I
echo.

REM TODO: �ȉ��̒l�����ۂ̐ݒ�ɕύX���Ă�������
REM ����: ���̃t�@�C����.gitignore�ɒǉ�����GitHub�Ƀv�b�V������Ȃ��悤�ɂ��Ă�������

REM Coverity Connect �T�[�o�[URL
set COVERITY_HOST=https://your-coverity-server.com

REM Coverity Connect �F�؏��i���ۂ̒l�ɕύX���Ă��������j
set COVAUTHUSER=your_username_here
set COVAUTHKEY=your_password_here

REM �v���L�V�ݒ�
set HTTPS_PROXY=http://your-proxy-server.com:3128
set HTTP_PROXY=http://your-proxy-server.com:3128

REM �܂��́A�J�X�^���v���L�V�ݒ���g�p����ꍇ
set PROXY_HOST=your-proxy-server.com
set PROXY_PORT=3128

echo ���ϐ����ݒ肳��܂���:
echo   COVERITY_HOST=%COVERITY_HOST%
echo   COVAUTHUSER=%COVAUTHUSER%
echo   COVAUTHKEY=***
echo   HTTPS_PROXY=%HTTPS_PROXY%
echo.

echo �T�[�o�[���N������ɂ͈ȉ��̃R�}���h�����s���Ă�������:
echo   python -m src.coverity_mcp_server.main
echo.

REM �T�[�o�[�������N������ꍇ�͈ȉ��̍s�̃R�����g���O���Ă�������
REM python -m src.coverity_mcp_server.main

pause
