@ECHO OFF
:loopstart
py main.py
echo %ERRORLEVEL%
IF %ERRORLEVEL% NEQ 0 (
	goto loopstart
)