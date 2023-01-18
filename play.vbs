strTitle = "Labyrinth"
strMsg = "1. Play" & vbCr
strMsg = strMsg & "2. Initialise SQL creds" & vbCR
strMsg = strMsg & "3. Dump sample data" & vbCR
strMsg = strMsg & "Select choice:" & vbCR
Dim oShell
Set oShell = WScript.CreateObject ("WScript.Shell")
Dim folderName
folderName = "."
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")
Dim fullpath
fullpath = fso.GetAbsolutePathName(folderName)
const quote = """"
Dim command
Do
    inp01 = InputBox(strMsg,strTitle)
    OK = True
    Select Case inp01
        Case "1"
            command = quote + "C:\Program Files\PowerShell\7\pwsh.exe" & quote & "-ExecutionPolicy ByPass -NoExit -Command & " & quote & "E:\Programs\Miniconda3\shell\condabin\conda-hook.ps1" & quote & "; conda activate " & quote & "E:\Programs\Miniconda3" & quote & "; conda activate adi; python " & fullpath & "\starter.py"
            command = "cmd.exe /C python "+fullpath+"\starter.py"
            msgBox command
            oShell.run ""+command
        Case "2"
            command = quote + "C:\Program Files\PowerShell\7\pwsh.exe" & quote & "-ExecutionPolicy ByPass -NoExit -Command & " & quote & "E:\Programs\Miniconda3\shell\condabin\conda-hook.ps1" & quote & "; conda activate " & quote & "E:\Programs\Miniconda3" & quote & "; conda activate adi; python " & fullpath & "\starter.py initsql"
            command = "cmd.exe /C python "+fullpath+"\starter.py initsql"
            oShell.run ""+command
        Case "3"
            command = quote + "C:\Program Files\PowerShell\7\pwsh.exe" & quote & "-ExecutionPolicy ByPass -NoExit -Command & " & quote & "E:\Programs\Miniconda3\shell\condabin\conda-hook.ps1" & quote & "; conda activate " & quote & "E:\Programs\Miniconda3" & quote & "; conda activate adi; python " & fullpath & "\starter.py dumpsample"
            command = "cmd.exe /C python "+fullpath+"\starter.py dumpsample"
            oShell.run ""+command
        Case ""
            WScript.quit
        Case Else
            MsgBox "You made an incorrect selection!",64,strTitle
            OK = False
    End Select
Loop While Not OK
