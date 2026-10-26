; =====================================================================
;  UlumiGlow - instalador para Windows (Inno Setup 6)
;  Copyright (c) 2025-2026 Ulises Agustin Rodriguez - Licencia MIT
;
;  Antes de compilar este script, generá el programa con app\build.bat
;  (crea app\dist\UlumiGlow\). El instalador queda en app\dist\.
; =====================================================================

#define AppName      "UlumiGlow"
#define AppVersion   "2.0.0"
#define AppPublisher "Ulises Agustin Rodriguez"
#define AppURL       "https://github.com/UlisesSB/UlumiGlow"
#define AppExe       "UlumiGlow.exe"

[Setup]
AppId={{59CAEDF8-7089-47ED-A5FD-0C96B72CF3C3}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
AppCopyright=Copyright (c) 2025-2026 {#AppPublisher}

; Instalación por usuario: no pide permisos de administrador.
PrivilegesRequired=lowest
DefaultDirName={autopf}\{#AppName}
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

LicenseFile=..\..\LICENSE
OutputDir=..\dist
OutputBaseFilename=UlumiGlow_Setup_{#AppVersion}
SetupIconFile=..\assets\ulumiglow.ico
UninstallDisplayIcon={app}\{#AppExe}
WizardStyle=modern
WizardImageFile=wizard-side.bmp,wizard-side@2x.bmp
WizardSmallImageFile=wizard-small.bmp,wizard-small@2x.bmp
Compression=lzma2
SolidCompression=yes
CloseApplications=yes

VersionInfoVersion={#AppVersion}.0
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} - Sistema Ambilight para PC
VersionInfoCopyright=Copyright (c) 2025-2026 {#AppPublisher}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
spanish.AutoStart=Iniciar UlumiGlow con Windows (en la bandeja)
english.AutoStart=Start UlumiGlow with Windows (in the tray)
spanish.Options=Opciones:
english.Options=Options:

[Tasks]
Name: "autostart";   Description: "{cm:AutoStart}";         GroupDescription: "{cm:Options}"
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Carpeta completa generada por PyInstaller
Source: "..\dist\UlumiGlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExe}"; Tasks: desktopicon
; Inicio con Windows: arranca directo en la bandeja, sin la intro
Name: "{userstartup}\{#AppName}";  Filename: "{app}\{#AppExe}"; Parameters: "--tray"; Tasks: autostart

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Cierra UlumiGlow si está abierto antes de desinstalar
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM {#AppExe}"; Flags: runhidden; RunOnceId: "CloseUlumiGlow"
