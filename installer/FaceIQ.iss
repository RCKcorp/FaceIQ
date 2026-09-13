#define MyAppName "FaceIQ"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "RCKcorp"
#define MyAppExeName "FaceIQ.exe"

[Setup]
AppId={{D3B91D2B-5389-43AF-9CF8-18EEB6F7721A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/RCKcorp/FaceIQ
AppSupportURL=https://github.com/RCKcorp/FaceIQ/issues
AppUpdatesURL=https://github.com/RCKcorp/FaceIQ/releases
DefaultDirName={autopf}\FaceIQ
DefaultGroupName=FaceIQ
UninstallDisplayName=FaceIQ
OutputDir=..\dist\installer
OutputBaseFilename=FaceIQ-Setup-{#MyAppVersion}
SetupIconFile=..\assets\faceiq.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Analyse locale de la qualité des visages
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Files]
Source: "..\dist\FaceIQ.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\FaceIQ"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\FaceIQ"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer FaceIQ"; Flags: nowait postinstall skipifsilent
