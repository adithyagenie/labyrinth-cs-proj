:: Play the game
@ECHO off
cls
:start
ECHO.
ECHO 1. Play game
ECHO 2. Initialise SQL login creds
ECHO 3. Dump sample data
ECHO 4. Exit
set choice=
set /p choice=Choice?
if not '%choice%'=='' set choice=%choice:~0,1%
if '%choice%'=='1' goto play
if '%choice%'=='2' goto initsql
if '%choice%'=='3' goto dump
if '%choice%'=='4' goto end
ECHO "%choice%" is not valid, try again
ECHO.
goto start

:play
start cmd /c "python %~dp0%~1/starter.py"
move nul 2>&0
goto end

:initsql
start cmd /c "python %~dp0%~1/starter.py initsql"
move nul 2>&0
goto end

:dump
start cmd /c "python %~dp0%~1/starter.py dumpsample"
move nul 2>&0
goto end

:end
pause