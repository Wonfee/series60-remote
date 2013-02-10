; Please run PyInstaller _before_ Inno Setup!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5CDAE448-28FD-401D-BB5B-1E97B25249DC}
AppName=Series60-Remote
AppVerName=Series60-Remote 0.5.0 - Alpha 1
AppPublisher=Lukas Hetzenecker
AppPublisherURL=http://series60-remote.sourceforge.net
AppSupportURL=http://series60-remote.sourceforge.net
AppUpdatesURL=http://series60-remote.sourceforge.net
DefaultDirName={pf}\Series60-Remote
DefaultGroupName=Series60-Remote
AllowNoIcons=yes
LicenseFile=dist\series60-remote\LICENSE.txt
InfoBeforeFile=dist\series60-remote\Changelog.txt
OutputBaseFilename=series60-remote-0.4.80
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\series60-remote\series60-remote.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\series60-remote\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Series60-Remote"; Filename: "{app}\series60-remote.exe"
Name: "{group}\{cm:ProgramOnTheWeb,Series60-Remote}"; Filename: "http://series60-remote.sourceforge.net"
Name: "{group}\{cm:UninstallProgram,Series60-Remote}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Series60-Remote"; Filename: "{app}\series60-remote.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Series60-Remote"; Filename: "{app}\series60-remote.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\series60-remote.exe"; Description: "{cm:LaunchProgram,Series60-Remote}"; Flags: nowait postinstall skipifsilent




