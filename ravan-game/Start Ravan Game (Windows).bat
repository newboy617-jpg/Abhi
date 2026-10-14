@echo off
rem Shoot Ravan's Ten Heads: opens the game full screen, like an app, with sound ready from the start.
rem Double-click this file.
setlocal
cd /d "%~dp0"
set "GAME=shoot-ravan.html"
if not exist "%GAME%" set "GAME=index.html"
if not exist "%GAME%" (
  echo Keep this launcher in the same folder as shoot-ravan.html.
  pause
  exit /b 1
)
set "FILEPATH=%~dp0%GAME%"
set "URL=file:///%FILEPATH:\=/%#stall"
rem its own browser profile, so scores, settings and recordings stay together and the sound setting applies
set "PROFILE=%LOCALAPPDATA%\RavanGame"
set "BROWSER="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined BROWSER if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined BROWSER if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "BROWSER=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if not defined BROWSER if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "BROWSER=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not defined BROWSER if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "BROWSER=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if defined BROWSER (
  start "" "%BROWSER%" --app="%URL%" --start-fullscreen --autoplay-policy=no-user-gesture-required --user-data-dir="%PROFILE%" --no-first-run --no-default-browser-check
) else (
  rem no Chrome or Edge: open it in the default browser (tap once to start the sound)
  start "" "%FILEPATH%"
)
endlocal
