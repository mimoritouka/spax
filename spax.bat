@echo off
chcp 65001 > nul
title Spax - Professional Testing Framework

:start
cls
color 0c

:: Banner and warning
echo  ▄████████    ▄███████▄    ▄████████ ▀████    ▐████▀
echo  ███    ███   ███    ███   ███    ███   ███▌   ████▀
echo  ███    █▀    ███    ███   ███    ███    ███  ▐███
echo  ███          ███    ███   ███    ███    ▀███▄███▀
echo ▀███████████ ▀█████████▀  ▀███████████    ████▀██▄
echo        ███   ███          ███    ███   ▐███  ▀███
echo   ▄█    ███   ███          ███    ███  ▄███     ███▄
echo ▄████████▀   ▄████▀        ███    █▀  ████       ███▄
echo.
echo !!FOR LEGAL AND EDUCATIONAL PURPOSES ONLY!!
echo Made by. Kaiser
echo.
echo ==========================================================
echo.

<<<<<<< HEAD
:: --- GET USER INPUT ---

set "TARGET_INPUT="
set /p TARGET_INPUT="Enter target address (e.g., https://example.com): "
if not defined TARGET_INPUT (
    echo. & echo [ERROR] Target address is required. & timeout /t 2 > nul & goto start
=======

set "TARGET="
set /p TARGET="target domain (orn: bombo.com): "
if not defined TARGET (
    echo. & echo [ERROR] It is mandatory to enter the destination address. & timeout /t 2 > nul & goto start
>>>>>>> 82561c943e417861aa964de617662c260c24a64e
)

set "PROTOCOL=http"
set /p PROTOCOL_INPUT="Protocol (http, tcp, udp) [Default: http]: "
if defined PROTOCOL_INPUT set "PROTOCOL=%PROTOCOL_INPUT%"

set "THREADS=25"
set /p THREADS_INPUT="Number of threads [Default: 25]: "
if defined THREADS_INPUT set "THREADS=%THREADS_INPUT%"

set "DURATION_ARG="
set /p DURATION_INPUT="Test duration in seconds (optional, e.g., 60): "
if defined DURATION_INPUT set "DURATION_ARG=-d %DURATION_INPUT%"

set "RAMP_UP_ARG="
set /p RAMP_UP_INPUT="Ramp-up time in seconds (optional, e.g., 10): "
if defined RAMP_UP_INPUT set "RAMP_UP_ARG=--ramp-up %RAMP_UP_INPUT%"

set "PROXY_ARG="
set /p PROXY_INPUT="Proxy file path (optional, e.g., proxies.txt): "
if defined PROXY_INPUT set "PROXY_ARG=--proxy-file %PROXY_INPUT%"

set "PAYLOAD_ARG="
set /p PAYLOAD_INPUT="Payload file path (optional, e.g., data.json): "
if defined PAYLOAD_INPUT set "PAYLOAD_ARG=--payload-file %PAYLOAD_INPUT%"

:: YENİ: Payload kullanım modu için soru eklendi
set "PAYLOAD_MODE_ARG="
if defined PAYLOAD_ARG (
    set /p PAYLOAD_MODE_INPUT="Payload mode (random, sequential) [Default: random]: "
    if defined PAYLOAD_MODE_INPUT set "PAYLOAD_MODE_ARG=--payload-mode %PAYLOAD_MODE_INPUT%"
)

<<<<<<< HEAD
set "REPORT_ARG="
set /p REPORT_INPUT="Report output file (optional, e.g., results.json or report.html): "
if defined REPORT_INPUT set "REPORT_ARG=--report-file %REPORT_INPUT%"


:: --- START THE ATTACK ---
=======

>>>>>>> 82561c943e417861aa964de617662c260c24a64e
cls
echo ==========================================================
echo STARTING TEST...
echo.
echo   - Target    : %TARGET_INPUT%
echo   - Protocol  : %PROTOCOL%
echo   - Threads   : %THREADS%
echo.
echo ==========================================================
echo.

<<<<<<< HEAD
:: Execute the Python script with all arguments
python spax.py %TARGET_INPUT% -p %PROTOCOL% -t %THREADS% %DURATION_ARG% %RAMP_UP_ARG% %PROXY_ARG% %PAYLOAD_ARG% %PAYLOAD_MODE_ARG% %REPORT_ARG%


=======

python spax.py -d %TARGET% -m %METHOD% -t %THREADS% %SECONDS_ARG% --quiet


>>>>>>> 82561c943e417861aa964de617662c260c24a64e
if %ERRORLEVEL% neq 0 (
    echo.
    echo ==========================================================
    echo [ERROR] Script exited with an error. Please check your inputs.
    echo ==========================================================
)

:end
echo.
echo ==========================================================
echo Script finished. Press any key to close the window.
echo ==========================================================
pause > nul
