[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  Exec('taskkill', '/F /IM ArdoiseDigitale.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

[Setup]
AppName=ArdoiseDigitale
AppVersion=2026.0
DefaultDirName={localappdata}\Programs\ArdoiseDigitale
DefaultGroupName=ArdoiseDigitale
OutputDir=C:\Users\tramb\ArdoiseDigitaleBleu\ArdoiseDigitaleV2026\Output
OutputBaseFilename=Install_Ardoise
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
; Embarque cleanup.vbs dans le dossier temporaire de l'installeur
Source: "cleanup.vbs"; DestDir: "{tmp}"
; Copie l'application compilée par PyInstaller
Source: "C:\Users\tramb\ArdoiseDigitaleBleu\ArdoiseDigitaleV2026\dist\ArdoiseDigitale\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Raccourci sur le Bureau
Name: "{userdesktop}\ArdoiseDigitale"; Filename: "{app}\ArdoiseDigitale.exe"; WorkingDir: "{app}"
; Raccourci dans le Menu Démarrer
Name: "{group}\ArdoiseDigitale"; Filename: "{app}\ArdoiseDigitale.exe"; WorkingDir: "{app}"

[Run]
; Lancement optionnel juste après l'installation (décochable par l'utilisateur)
Filename: "{app}\ArdoiseDigitale.exe"; Description: "Lancer ArdoiseDigitale"; Flags: nowait postinstall skipifsilent
; Auto-suppression de l'installateur via VBScript (detection de fin de processus)
Filename: "wscript.exe"; Parameters: """{tmp}\cleanup.vbs"" ""{srcexe}"""; Flags: runhidden nowait




