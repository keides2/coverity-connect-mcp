@echo off
echo ====================================
echo Coverity Connect MCP Server
echo Production Environment Setup
echo ====================================

echo.
echo Note: Please run this script from the project root directory
echo Current directory: %CD%
echo.

echo.
echo Checking environment variables...
echo COVERITY_HOST: %COVERITY_HOST%
echo COVAUTHUSER: %COVAUTHUSER%
echo.

echo Loading .env file...
if exist .env (
    echo .env file found
    type .env
) else (
    echo WARNING: .env file not found!
)

echo.
echo Starting MCP Server...
python -m src.coverity_mcp_server

pause
