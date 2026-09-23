Set WshShell = CreateObject("WScript.Shell")
strStartup = WshShell.SpecialFolders("Startup")
Set oLink = WshShell.CreateShortcut(strStartup & "\NeonBot.lnk")
oLink.TargetPath = "wscript.exe"
oLink.Arguments = """C:\Users\FE-06\Desktop\bot\run_silent.vbs"""
oLink.WorkingDirectory = "C:\Users\FE-06\Desktop\bot"
oLink.Save
