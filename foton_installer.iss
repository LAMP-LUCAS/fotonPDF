; Script de Instalação Inno Setup para fotonPDF
; Este script gera um instalador (.exe) profissional que configura tudo automaticamente.

[Setup]
AppName=fotonPDF
AppVersion=1.0.0
DefaultDirName={autopf}\fotonPDF
DefaultGroupName=fotonPDF
UninstallDisplayIcon={app}\foton.exe
Compression=lzma2
SolidCompression=yes
OutputDir=..
OutputBaseFilename=fotonPDF_Setup_v1.0.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Inclui todos os arquivos da pasta dist/foton
Source: "dist\foton\*"; DestDir: "{app}"; Flags: igonreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\fotonPDF"; Filename: "{app}\foton.exe"
Name: "{autodesktop}\fotonPDF"; Filename: "{app}\foton.exe"; Tasks: desktopicon

[Run]
; Executa o setup do fotonPDF ao finalizar a instalação para registrar o menu de contexto
Filename: "{app}\foton.exe"; Parameters: "setup"; StatusMsg: "Configurando integracao com o Windows..."; Flags: runhidden
