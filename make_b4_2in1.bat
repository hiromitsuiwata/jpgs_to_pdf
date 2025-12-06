@echo off
setlocal enabledelayedexpansion

REM ===================================
REM Argument check
REM ===================================
if "%~1"=="" (
    echo Usage: %~n0 ^<target_folder^>
    exit /b 1
)

set TARGET=%~1

if not exist "%TARGET%" (
    echo Error: Target folder does not exist.
    exit /b 1
)

echo Target folder: %TARGET%
echo Processing subfolders...
echo.

REM ===================================
REM Loop through subfolders
REM ===================================
for /d %%F in ("%TARGET%\*") do (
    echo --- Subfolder: %%~nxF ---

    uv run python jpgs_to_pdf_b4_2in1.py "%%F"

    echo.
)

echo Done.
endlocal
