#NoEnv
SetBatchLines, -1
#Include Socket.ahk
Menu, Tray, NoIcon
;--------------------------------------------------------------
global Server := "", ServerSocket := ""
global resHTML := "Server Running..."
global resKEY := "A000-000-000-000"
global isServerRunning := false
;--------------------------------------------------------------
Gui, -Resize
Gui, Color, White

Gui, -AlwaysOnTop
Gui, Font, s14 Bold, Segoe UI
Gui, Add, Text, x20 y15, Gallery Web

Gui, Font, s10 norm
Gui, Add, Text, x20 y60, Enter your enc.key

Gui, Font, s12 norm
Gui, Add, Edit, x20 y85 w300 h30 vEncKey Border Center Password, %resKEY%
Gui, Add, Checkbox, x20 y120 vShowKey gTogglePassword, Show Key

Gui, Font, s12 Bold
Gui, Add, Button, x20 y160 w300 h40 vBtnServer gToggleServer Background0x28a745 cWhite, Start Server

Gui, Font, s9 norm
Gui, Add, Text, x20 y220 w300 cGray, Alt + Mouse-Click ➤ To launch the video in VLC Player

Gui, Font, s9 norm cBlack
Gui, Add, Text, x20 y245, Credit:

Gui, Font, s9 underline cBlue
Gui, Add, Text, x60 y245 vGitHubLink gOpenGitHub, https://github.com/AntorPi314

Gui, Show, w360 h280, Temporary 'enc.key' Server
return

TogglePassword:
GuiControlGet, ShowKey
if (ShowKey)
    GuiControl, -Password, EncKey
else
    GuiControl, +Password, EncKey
return

OpenGitHub:
Run, https://github.com/AntorPi314
return
;--------------------------------------------------------------
ToggleServer:
GuiControlGet, EncKey,, EncKey
resKEY := EncKey

if (!isServerRunning) {
    try {
        Server := new SocketTCP()
        Server.OnAccept := Func("OnAccept")
        Server.Bind(["0.0.0.0", 8080])
        Server.Listen()
        isServerRunning := true
        GuiControl,, BtnServer, Stop Server
        GuiControl, +Background0xdc3545, BtnServer 
    } catch e {
        MsgBox, Failed to start server: %e%
    }
} else {
    try {
        if IsObject(ServerSocket)
            ServerSocket.Disconnect()
    } catch {}

    try {
        Server.Disconnect()
    } catch {}

    Server := ""
    ServerSocket := ""
    isServerRunning := false

    GuiControl,, BtnServer, Start Server
    GuiControl, +Background0x28a745, BtnServer 
}
return
;--------------------------------------------------------------
GuiClose:
if (isServerRunning) {
    try {
        if IsObject(ServerSocket)
            ServerSocket.Disconnect()
        Server.Disconnect()
    } catch {}
}
ExitApp
;--------------------------------------------------------------
~!s:: 
if (Server) {
    MsgBox, Server is already running.
    return
}
try {
    Server := new SocketTCP()
    Server.OnAccept := Func("OnAccept")
    Server.Bind(["0.0.0.0", 8080])
    Server.Listen()
    ; MsgBox, Server started on port 8080
} catch e {
    ; MsgBox, Failed to start server: %e%
}
return
;--------------------------------------------------------------
~!c:: 

if (Server) {
    try {
        if IsObject(ServerSocket)
            ServerSocket.Disconnect()
    } catch {}

    try {
        Server.Disconnect()
    } catch {}

    Server := ""
    ServerSocket := ""

    Sleep, 500  

    ; MsgBox, Server stopped. You can now start it again.
} else {
    ; MsgBox, Server not running.
}
return
;--------------------------------------------------------------
OnAccept(Server) {
    global resHTML, resKEY, ServerSocket
    try {
        ServerSocket := Server.Accept()
        Request := StrSplit(ServerSocket.RecvLine(), " ")
        while ServerSocket.RecvLine() != "" 
            continue

        if (Request[1] != "GET") {
            ServerSocket.SendText("HTTP/1.0 501 Not Implemented`r`n`r`n")
            ServerSocket.Disconnect()
            return
        }

        if (Request[2] == "/" || Request[2] == "/index.html")
            Response := resHTML, CType := "text/html"
        else if (Request[2] == "/enc.key")
            Response := resKEY, CType := "text/plain"
        else
            Response := "404 Not Found", CType := "text/plain", Status := "404 Not Found"

        if (!Status)
            Status := "200 OK"

        ServerSocket.SendText("HTTP/1.0 " Status "`r`nContent-Type: " CType "`r`nContent-Length: " StrLen(Response) "`r`n`r`n" Response)
        ServerSocket.Disconnect()
    } catch e {
        MsgBox, Error in OnAccept: %e%
    }
}
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
            configFile := A_ScriptDir . "\vlc-path.txt"

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




