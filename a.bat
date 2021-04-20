@echo off
Setlocal enabledelayedexpansion

Set "Pattern= "
Set "Replace=_"

For %%a in (*) Do (
    Set "File=%%~a"
    Ren "%%a" "!File:%Pattern%=%Replace%!"
)

Pause&Exit