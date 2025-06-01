#Persistent
#NoEnv
#SingleInstance Force
SetWorkingDir, %A_ScriptDir%
DetectHiddenWindows, On
Menu, Tray, NoIcon

; ------ Configuration ----------------------------------------
serverPath := A_ScriptDir . "\miniweb.exe"
serverArgs := "-p 8080 -d " . A_ScriptDir
global serverPID := 0
;--------------------------------------------------------------
Gui, -Resize
Gui, Color, White

; Custom color values
titleColor := "0x9E7878"
shortcutColor := "0x9E7878"
detailColor := "0x000000"
greenColor := "0x28A745" ; Bootstrap green

Gui, Font, s18 Bold c%titleColor%, Segoe UI
Gui, Add, Text, x20 y20, Gallery Web

Gui, Font, s12 Bold cWhite, Segoe UI
Gui, Add, Button, x200 y20 w100 h30 gsetupStart vbtnSetup, Setup
GuiControl, +Background%greenColor%, btnSetup

Gui, Font, s10 Bold c%shortcutColor%, Segoe UI
Gui, Add, Text, x20 y70, Alt + S ➤
Gui, Add, Text, x20 y110, Ctrl + Shift + G ➤
Gui, Add, Text, x20 y150, Ctrl + Shift + Z ➤
Gui, Add, Text, x20 y190, Ctrl + Shift + M ➤
Gui, Add, Text, x20 y230, Alt + Mouse-Click ➤

Gui, Font, s10 c%detailColor%, Segoe UI
Gui, Add, Text, x160 y70, Start / Stop the server
Gui, Add, Text, x160 y110, Convert your media for upload
Gui, Add, Text, x160 y150, Revert (backtrack) your converted media to the original
Gui, Add, Text, x160 y190, Convert other format media to JPG, PNG, or MP4
Gui, Add, Text, x160 y230, To launch the video in VLC Player

Gui, Font, s9 c%detailColor%, Segoe UI
Gui, Add, Text, x20 y270, Credit:

Gui, Font, s9 cBlue, Segoe UI
Gui, Add, Text, x70 y270 gOpenGitHub, https://github.com/AntorPi314

Gui, Show, w600 h300, GWeb v5
return

OpenGitHub:
Run, https://github.com/AntorPi314
return

setupStart:
    if FileExist("GWeb-setup.py")
        Run, python GWeb-setup.py
    else if FileExist("GWeb-setup.exe")
        Run, GWeb-setup.exe
    else
        MsgBox, 16, Error, Neither GWeb-setup.py nor GWeb-setup.exe found in GWeb folder
return

GuiClose:
ExitApp
;--------------------------------------------------------------
^+g::
    Clipboard := "" 
    Send, ^c
    ClipWait, 1
    if !Clipboard
    {
        MsgBox, 48, Warning, Clipboard is empty or failed to copy!
        return
    }

    SetWorkingDir, %A_ScriptDir%
    
    if FileExist("GWeb-converter.py")
        Run, python GWeb-converter.py "%Clipboard%"
    else if FileExist("GWeb-converter.exe")
        Run, GWeb-converter.exe "%Clipboard%"
    else
        MsgBox, 16, Error, Neither GWeb-converter.py nor GWeb-converter.exe found in GWeb folder
return
;--------------------------------------------------------------
!LButton::
old := Clipboard
Send, ^{Click}
Loop, 10
{
    Sleep, 100
    WinGetTitle, currentTitle, A
    if InStr(currentTitle, "Copied")
    {
        Clipboard := Clipboard
        link := Clipboard
        if (link)
        {
            defaultVLC := "C:\Program Files\VideoLAN\VLC\vlc.exe"
            configFile := A_ScriptDir . "\bin\vlc-path.txt"

            if FileExist(configFile)
            {
                FileReadLine, vlcPath, %configFile%, 1
            }
            else
            {
                vlcPath := defaultVLC
            }

            if !FileExist(vlcPath)
            {
                MsgBox, 48, VLC Not Found, VLC not found at:`n%vlcPath%`nPlease locate vlc.exe manually.

                Gui, New
                Gui, +AlwaysOnTop +Resize +MinSize
                Gui, Add, Text,, Paste or browse to vlc.exe:
                Gui, Add, Edit, vVLCPath w400, %vlcPath%
                Gui, Add, Button, gPickVLCPath, 📂 Pick Path
                Gui, Add, Button, gSaveVLCPath Default, ✅ Save
                Gui, Add, Button, gCancelVLCPath, ❌ Cancel
                Gui, Show,, Locate VLC Player
                return
            }

            Run, "%vlcPath%" "%link%"
            break
        }
    }
}
Clipboard := old
return

; --- GUI Button: Pick Path ---
PickVLCPath:
FileSelectFile, chosen, 3,, Select vlc.exe, Executable Files (*.exe)
if (chosen != "")
    GuiControl,, VLCPath, %chosen%
return
;--------------------------------------------------------------
; --- GUI Button: Save ---
SaveVLCPath:
Gui, Submit, NoHide
if (!FileExist(VLCPath) || SubStr(VLCPath, -3) != ".exe")
{
    MsgBox, 16, Invalid, Please select a valid vlc.exe file.
    return
}
FileCreateDir, %A_ScriptDir%\bin
FileDelete, %configFile%
FileAppend, %VLCPath%, %configFile%
Gui, Destroy
Run, "%VLCPath%" "%link%"
return

; --- GUI Button: Cancel ---
CancelVLCPath:
Gui, Destroy
return
;--------------------------------------------------------------
^+m::
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if !Clipboard
    {
        MsgBox, 48, Warning, Clipboard is empty or failed to copy!
        return
    }
    bin_path := A_ScriptDir . "\bin"
    SetWorkingDir, %bin_path%
  
    if FileExist("toJPG_PNG_MP4.py")
        Run, python toJPG_PNG_MP4.py "%Clipboard%"
    else if FileExist("toJPG_PNG_MP4.exe")
        Run, toJPG_PNG_MP4.exe "%Clipboard%"
    else
        MsgBox, 16, Error, Neither toJPG_PNG_MP4.py nor toJPG_PNG_MP4.exe found in %A_ScriptDir%\bin
return
;--------------------------------------------------------------
^+z::
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if !Clipboard
    {
        MsgBox, 48, Warning, Clipboard is empty or failed to copy!
        return
    }
    bin_path := A_ScriptDir . "\bin"
    SetWorkingDir, %bin_path%
  
    if FileExist("backTracking.py")
        Run, python backTracking.py "%Clipboard%"
    else if FileExist("backTracking.exe")
        Run, backTracking.exe "%Clipboard%"
    else
        MsgBox, 16, Error, Neither backTracking.py nor backTracking.exe found in %A_ScriptDir%\bin
return
;--------------------------------------------------------------
x_alphabate := ""
x_count := ""
^+r::
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    folderPath := Clipboard
    folderPath := StrReplace(folderPath, """", "")
    SplitPath, folderPath, folderName
    if (RegExMatch(folderName, "([A-Za-z_]+)(\d*)", match)) {
        if (x_alphabate = "" || x_count = "") {
            x_alphabate := match1
            x_count := match2 ? match2 : 0
        } else {
            x_count += 1
            newFolderName := x_alphabate . x_count
            newFolderPath := RegExReplace(folderPath, "[^\\]+$", newFolderName)
            FileMoveDir, %folderPath%, %newFolderPath%
        }
    }
return
;--------------------------------------------------------------

!s:: 
if (serverPID) {
    Run, taskkill /F /IM miniweb.exe, , Hide
    ToolTip, 🛑 Server stopped
    serverPID := 0
} else {
    Run, %ComSpec% /c "%serverPath%" %serverArgs%, , Hide, newPID
    serverPID := newPID
    ToolTip, ✅ Server started on http://localhost:8080
	Run, http://localhost:8080
}
SetTimer, RemoveTip, -1500
return
;--------------------------------------------------------------
RemoveTip:
ToolTip
return
