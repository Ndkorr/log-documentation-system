#define MyAppName "Log Documentation System"
#define MyAppExeName "LogDocumentationSystem.exe"
#define MyAppVersion GetEnv("APP_VERSION")
#define MyAppPublisher "Ndkorr"

[Setup]
AppId={{9E6BB60A-6D10-4C54-94E6-8C116A86A2F7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\Output
OutputBaseFilename=log-documentation-system-{#MyAppVersion}-windows-installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "..\dist\LogDocumentationSystem\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\.ldsg"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.ldsg"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsd"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.ldsd"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsu"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.ldsu"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsdict"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.ldsdict"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsg"; ValueType: string; ValueName: ""; ValueData: "LDS General Log"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsd"; ValueType: string; ValueName: ""; ValueData: "LDS Debugging Log"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsu"; ValueType: string; ValueName: ""; ValueData: "LDS UI Mode File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsdict"; ValueType: string; ValueName: ""; ValueData: "LDS Dictionary Package"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsg\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsd\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsu\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsdict\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
