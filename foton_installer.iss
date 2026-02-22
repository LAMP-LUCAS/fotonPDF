; Script de Instalação Inno Setup para fotonPDF
; Este script gera um instalador (.exe) profissional que configura tudo automaticamente.

#define MyAppVersion GetEnv('APP_VERSION')
#if MyAppVersion == ""
  #define MyAppVersion "1.0.0"
#endif

[Setup]
AppName=fotonPDF
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\fotonPDF
DefaultGroupName=fotonPDF
SetupIconFile=docs\brand\logo.ico
UninstallDisplayIcon={app}\foton.exe
Compression=lzma2
SolidCompression=yes
OutputDir=..
OutputBaseFilename=fotonPDF_Setup_v{#MyAppVersion}
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; Melhorias para Zero-Click e Permissões
PrivilegesRequired=lowest
DisableWelcomePage=yes
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableFinishedPage=no
; Registra a mudança de PATH para que o terminal reconheça 'foton' imediatamente
ChangesEnvironment=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "addtopath"; Description: "Adicionar fotonPDF ao PATH do sistema (permite usar 'foton' no terminal)"; Flags: checked

[Files]
; Inclui todos os arquivos da pasta dist/foton
Source: "dist\foton\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\fotonPDF"; Filename: "{app}\foton.exe"
Name: "{autodesktop}\fotonPDF"; Filename: "{app}\foton.exe"; Tasks: desktopicon

[Registry]
; Adiciona o diretório de instalação ao PATH do usuário (HKCU) para acesso via terminal
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Tasks: addtopath; Check: NeedsAddPath(ExpandConstant('{app}'))

[Run]
; Executa o setup do fotonPDF ao finalizar a instalação para registrar o menu de contexto
Filename: "{app}\foton-cli.exe"; Parameters: "setup"; StatusMsg: "Configurando integracao com o Windows..."; Flags: runhidden

[UninstallRun]
; Remove as entradas do menu de contexto ao desinstalar
Filename: "{app}\foton-cli.exe"; Parameters: "uninstall -y"; Flags: runhidden

[Code]
// Verifica se o caminho já está no PATH do usuário para evitar duplicação
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Uppercase(Param) + ';', ';' + Uppercase(OrigPath) + ';') = 0;
end;
