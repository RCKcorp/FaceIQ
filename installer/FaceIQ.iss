#define MyAppName "FaceIQ"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "RCKcorp"
#define MyAppExeName "FaceIQ.exe"

[Setup]
AppId={{D3B91D2B-5389-43AF-9CF8-18EEB6F7721A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\FaceIQ
DefaultGroupName=FaceIQ
UninstallDisplayName=FaceIQ
OutputDir=..\dist\installer
OutputBaseFilename=FaceIQ-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Files]
Source: "..\dist\FaceIQ.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\FaceIQ"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\FaceIQ"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer FaceIQ"; Flags: nowait postinstall skipifsilent
