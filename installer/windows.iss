#define MyAppName "Log Documentation System"
#define MyAppExeName "LogDocumentationSystem.exe"
#define MyAppVersion GetEnv("APP_VERSION")
#define MyAppPublisher "mathewsa"

[Setup]
AppId={{9E6BB60A-6D10-4C54-94E6-8C116A86A2F7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
VersionInfoCompany={#MyAppPublisher}
VersionInfoProductName={#MyAppName}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\Output
OutputBaseFilename=log-documentation-system-{#MyAppVersion}-windows-installer
SetupIconFile=..\assets\lds.ico
LicenseFile=..\eula.txt
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
ChangesAssociations=yes

[Files]
Source: "..\dist\LogDocumentationSystem\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\assets\lds.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "..\assets\ldsg.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "..\assets\ldsd.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "..\assets\ldsu.ico"; DestDir: "{app}\icons"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icons\lds.ico"; IconIndex: 0
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icons\lds.ico"; IconIndex: 0; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\.lds"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.lds"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsg"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.ldsg"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsd"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.ldsd"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsu"; ValueType: string; ValueName: ""; ValueData: "LogDocumentationSystem.ldsu"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.lds\OpenWithProgids"; ValueType: string; ValueName: "LogDocumentationSystem.lds"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsg\OpenWithProgids"; ValueType: string; ValueName: "LogDocumentationSystem.ldsg"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsd\OpenWithProgids"; ValueType: string; ValueName: "LogDocumentationSystem.ldsd"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ldsu\OpenWithProgids"; ValueType: string; ValueName: "LogDocumentationSystem.ldsu"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.lds"; ValueType: string; ValueName: ""; ValueData: "LDS Log File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsg"; ValueType: string; ValueName: ""; ValueData: "LDS General Log"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsd"; ValueType: string; ValueName: ""; ValueData: "LDS Debugging Log"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsu"; ValueType: string; ValueName: ""; ValueData: "LDS UI Mode File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.lds\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\icons\lds.ico"",0"
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsg\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\icons\ldsg.ico"",0"
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsd\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\icons\ldsd.ico"",0"
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsu\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\icons\ldsu.ico"",0"
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.lds\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsg\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsd\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\LogDocumentationSystem.ldsu\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}"; ValueType: string; ValueName: "ApplicationName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".lds"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ldsg"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ldsd"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ldsu"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\LogDocumentationSystem\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\LogDocumentationSystem\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Open LDS log documentation files"
Root: HKA; Subkey: "Software\LogDocumentationSystem\Capabilities\FileAssociations"; ValueType: string; ValueName: ".lds"; ValueData: "LogDocumentationSystem.lds"
Root: HKA; Subkey: "Software\LogDocumentationSystem\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ldsg"; ValueData: "LogDocumentationSystem.ldsg"
Root: HKA; Subkey: "Software\LogDocumentationSystem\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ldsd"; ValueData: "LogDocumentationSystem.ldsd"
Root: HKA; Subkey: "Software\LogDocumentationSystem\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ldsu"; ValueData: "LogDocumentationSystem.ldsu"
Root: HKA; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "Software\LogDocumentationSystem\Capabilities"; Flags: uninsdeletevalue

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
