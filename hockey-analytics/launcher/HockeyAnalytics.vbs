Set objShell = CreateObject("WScript.Shell")
strPath = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
objShell.CurrentDirectory = strPath & "..\"
objShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & strPath & "launcher.ps1""", 0, False
