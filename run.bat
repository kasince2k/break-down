@echo off
REM Run script for the Obsidian Article Breakdown Agent on Windows

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is required but not found.
    echo Please install Python 3.9 or higher.
    exit /b 1
)

REM Check if Poetry is installed
where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Poetry is required but not found.
    echo Please install Poetry: https://python-poetry.org/docs/#installation
    exit /b 1
)

REM Default values
set VAULT_PATH=
set PORT=8000
set HOST=localhost
set WEB=false
set NO_SERVER=false
set SETUP=false

REM Parse arguments
:parse_args
if "%~1"=="" goto check_args
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="-v" (
    set VAULT_PATH=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--vault-path" (
    set VAULT_PATH=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-p" (
    set PORT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-H" (
    set HOST=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-w" (
    set WEB=true
    shift
    goto parse_args
)
if "%~1"=="--web" (
    set WEB=true
    shift
    goto parse_args
)
if "%~1"=="-n" (
    set NO_SERVER=true
    shift
    goto parse_args
)
if "%~1"=="--no-server" (
    set NO_SERVER=true
    shift
    goto parse_args
)
if "%~1"=="-s" (
    set SETUP=true
    shift
    goto parse_args
)
if "%~1"=="--setup" (
    set SETUP=true
    shift
    goto parse_args
)

echo Error: Unknown option %~1
goto show_help

:show_help
echo Usage: run.bat [options]
echo.
echo Options:
echo   -h, --help                 Show this help message
echo   -v, --vault-path PATH      Path to the Obsidian vault (required)
echo   -p, --port PORT            Port for the MCP server (default: 8000)
echo   -H, --host HOST            Host for the MCP server (default: localhost)
echo   -w, --web                  Run with the ADK web UI
echo   -n, --no-server            Don't start the MCP server (use if it's already running)
echo   -s, --setup                Run the setup script before starting
echo.
echo Example:
echo   run.bat --vault-path "C:\Users\username\Documents\Obsidian\MyVault" --web
echo.
exit /b 0

:check_args
REM Check if vault path is provided
if "%VAULT_PATH%"=="" (
    echo Error: Vault path is required.
    goto show_help
)

REM Run setup if requested
if "%SETUP%"=="true" (
    echo Running setup script...
    python setup.py
    if %ERRORLEVEL% neq 0 (
        echo Setup failed. Exiting.
        exit /b 1
    )
)

REM Activate Poetry environment
echo Activating Poetry environment...
call poetry install

REM Build the command
set CMD=poetry run python run_agent.py --vault-path "%VAULT_PATH%" --port %PORT% --host %HOST%

if "%NO_SERVER%"=="true" (
    set CMD=%CMD% --no-server
)

if "%WEB%"=="true" (
    set CMD=%CMD% --web-ui
)

REM Run the agent
echo Running Obsidian Article Breakdown Agent...
echo Vault path: %VAULT_PATH%
echo MCP server: %HOST%:%PORT%
if "%WEB%"=="true" (
    echo Using web UI
)

echo Executing: %CMD%
%CMD%
