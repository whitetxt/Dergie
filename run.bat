@ECHO OFF
:loopstart
py main.py
IF %ERRORLEVEL% NEQ 0 (
	goto loopstart
)