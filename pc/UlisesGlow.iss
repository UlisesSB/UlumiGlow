[Setup]
AppName=UlisesGlow
AppVersion=1.0.0
AppPublisher=Ulises
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=

DefaultDirName={pf}\UlisesGlow
DefaultGroupName=UlisesGlow

OutputDir=.
OutputBaseFilename=UlisesGlow_Setup
Compression=lzma
SolidCompression=yes

ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Icono del instalador
SetupIconFile=ulisesglow.ico

; Icono que se ve en "Agregar o quitar programas"
UninstallDisplayIcon={app}\UlisesGlow.exe

; (Opcional) URL y datos de versión
VersionInfoVersion=1.0.0.0
VersionInfoCompany=Ulises
VersionInfoDescription=UlisesGlow - Ambilight Tray
VersionInfoTextVersion=1.0.0
VersionInfoCopyright=Ulises

[Files]
; EXE principal
Source: "UlisesGlow.exe"; DestDir: "{app}"; Flags: ignoreversion

; Copiamos el ico también por prolijidad (opcional)
Source: "ulisesglow.ico"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el Escritorio"; Flags: unchecked

[Icons]
; Grupo en el menú Inicio
Name: "{group}\UlisesGlow"; Filename: "{app}\UlisesGlow.exe"; WorkingDir: "{app}"
; Acceso directo opcional en Escritorio
Name: "{commondesktop}\UlisesGlow"; Filename: "{app}\UlisesGlow.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Ejecutar al finalizar instalación (sin esperar)
Filename: "{app}\UlisesGlow.exe"; WorkingDir: "{app}"; Description: "Ejecutar UlisesGlow ahora"; Flags: postinstall nowait skipifsilent

[Code]
function ExecCmd(const Cmd: string): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/C ' + Cmd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

procedure CreateTask();
begin
  { Borra si existe }
  ExecCmd('schtasks /Delete /TN "UlisesGlow" /F >nul 2>&1');

  { Crea tarea al iniciar sesion: ejecuta el EXE }
  ExecCmd('schtasks /Create /TN "UlisesGlow" /TR "\"{app}\UlisesGlow.exe\"" /SC ONLOGON /RL HIGHEST /F');
end;

procedure RemoveTask();
begin
  ExecCmd('schtasks /Delete /TN "UlisesGlow" /F >nul 2>&1');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    CreateTask();
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    RemoveTask();
end;
