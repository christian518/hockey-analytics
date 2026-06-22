$ProjectRoot = "C:\hockey-analytics"
$LauncherVbs = "$ProjectRoot\launcher\HockeyAnalytics.vbs"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Hockey Analytics.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$LauncherVbs`""
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = "Hockey Analytics - Youth Tournament Platform"
$Shortcut.IconLocation = "shell32.dll,23"
$Shortcut.Save()
Write-Host "Desktop shortcut created at: $ShortcutPath" -ForegroundColor Green
