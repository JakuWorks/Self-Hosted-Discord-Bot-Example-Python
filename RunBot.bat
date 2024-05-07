@echo off

rem The below comment makes it easy to measure how long should the 'arrows' be.

rem "          Running .\main\RunBotPhase2.ps1
set "ArrowBody=-------------------------------"

set "RunBotPhase2_Path=.\main\RunBotPhase2.ps1"

echo %ArrowBody%^>
echo Setup Started!
echo Running PowerShell and '%RunBotPhase2_Path%'
echo ^<%ArrowBody%

@echo on

Powershell -noprofile -noexit -nologo -ExecutionPolicy Bypass -Command %RunBotPhase2_Path%
