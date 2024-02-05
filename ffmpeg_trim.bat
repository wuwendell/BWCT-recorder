@echo off
setlocal enabledelayedexpansion

REM Check if ffmpeg is installed
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: ffmpeg is not installed or not in the system PATH.
    pause
    exit /b 1
)

REM Get input file
set /p input_file="Enter input file: "
if not exist "%input_file%" (
    echo Error: Input file not found.
    pause
    exit /b 1
)

REM Get output file
set /p output_file="Enter output file: "

REM Get input video duration
for /f "tokens=*" %%a in ('ffmpeg -i "%input_file%" 2^>^&1 ^| find "Duration"') do (
    set "duration_line=%%a"
)
for /f "tokens=*" %%b in ("!duration_line:*Duration=!") do (
    set "duration=%%b"
)
set "duration=!duration:~0,-7!"

REM Get user input for trim durations
set /p trim_start="Enter trim start duration (HH:MM:SS.mmm): "
set /p trim_end="Enter trim end duration (HH:MM:SS.mmm): "

REM Run ffmpeg to trim the video
ffmpeg -ss %trim_start% -i "%input_file%" -to %trim_end% -c copy "%output_file%"

echo Video trimmed successfully.
pause
exit /b 0
