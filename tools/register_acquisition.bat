@echo off
REM JumpServer Acquisition Registration - Windows Batch Wrapper
REM Usage: register_acquisition.bat E:\evidence\disk.dd CASE-2026-001

setlocal

if "%~1"=="" (
    echo ERROR: Evidence file path required
    echo Usage: register_acquisition.bat ^<evidence_file^> ^<case_number^> [options]
    echo Example: register_acquisition.bat E:\evidence\disk.dd CASE-2026-001
    exit /b 1
)

if "%~2"=="" (
    echo ERROR: Case number required
    echo Usage: register_acquisition.bat ^<evidence_file^> ^<case_number^> [options]
    echo Example: register_acquisition.bat E:\evidence\disk.dd CASE-2026-001
    exit /b 1
)

set EVIDENCE_FILE=%~1
set CASE_NUMBER=%~2

REM Check if file exists
if not exist "%EVIDENCE_FILE%" (
    echo ERROR: File not found: %EVIDENCE_FILE%
    exit /b 1
)

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Run Python script
python "%SCRIPT_DIR%register_acquisition.py" --file "%EVIDENCE_FILE%" --case "%CASE_NUMBER%" %3 %4 %5 %6 %7 %8 %9

endlocal
