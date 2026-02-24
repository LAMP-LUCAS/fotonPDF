<#
.SYNOPSIS
Simula o pipeline de Release do GitHub Actions localmente.

.DESCRIPTION
Este script executa todas as etapas que o workflow `.github/workflows/release.yml` 
executaria na nuvem, permitindo testar a geração de artefatos (Instalador Inno Setup, 
ZIP Portátil e Release Notes) antes de criar uma tag oficial.

.EXAMPLE
.\scripts\test_release_pipeline.ps1
#>

$ErrorActionPreference = "Stop"

# 1. Definir raízes e garantir encoding
$ProjectRoot = (Resolve-Path ".\").Path
$env:PYTHONIOENCODING = "utf-8"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO SIMULAÇÃO DE RELEASE CI/CD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 2. Extrair versão do código (Centro de Verdade)
Write-Host "`n[1/6] Extraindo versão do src/__init__.py..." -ForegroundColor Yellow
$codeVersionLine = (Get-Content "src/__init__.py" -Encoding utf8 | Select-String "__version__")
if (-not $codeVersionLine) {
    Write-Error "Não foi possível encontrar __version__ em src/__init__.py"
}
$codeVersion = $codeVersionLine.ToString().Split('"')[1]
$env:APP_VERSION = $codeVersion
Write-Host "[OK] Versão detectada: $codeVersion" -ForegroundColor Green

# 3. Limpar diretório dist anterior (Opcional, mas seguro pra simulação)
Write-Host "`n[2/6] Limpando diretórios de build/dist antigos..." -ForegroundColor Yellow
if (Test-Path "$ProjectRoot\dist") { Remove-Item -Recurse -Force "$ProjectRoot\dist" }
if (Test-Path "$ProjectRoot\build") { Remove-Item -Recurse -Force "$ProjectRoot\build" }
Write-Host "[OK] Diretórios limpos." -ForegroundColor Green

# 4. Gerar Executável (PyInstaller)
Write-Host "`n[3/6] Iniciando Build PyInstaller..." -ForegroundColor Yellow
python scripts/build_exe.py
if ($LASTEXITCODE -ne 0) { Write-Error "Falha no build do PyInstaller." }
Write-Host "[OK] PyInstaller finalizado." -ForegroundColor Green

# 5. Assinar Executável
Write-Host "`n[4/6] Iniciando Assinatura Digital..." -ForegroundColor Yellow
python scripts/sign_exe.py
if ($LASTEXITCODE -ne 0) { Write-Error "Falha na assinatura." }
Write-Host "[OK] Processo de assinatura finalizado." -ForegroundColor Green

# 6. Compilar Instalador (Inno Setup)
Write-Host "`n[5/6] Compilando Instalador Profissional (Inno Setup)..." -ForegroundColor Yellow
$isccPath = "iscc"
if (-not (Get-Command "iscc" -ErrorAction SilentlyContinue)) {
    # Tenta procurar no caminho padrão
    $defaultIscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if (Test-Path $defaultIscc) {
        $isccPath = "& `"$defaultIscc`""
    }
    else {
        Write-Host "[AVISO] Inno Setup (iscc) não encontrado no PATH ou na pasta padrão. Pulando a geração do Instalador .exe." -ForegroundColor Red
        $isccPath = $null
    }
}

if ($isccPath) {
    if ($isccPath -eq "iscc") {
        iscc foton_installer.iss
    }
    else {
        Invoke-Expression "$isccPath foton_installer.iss"
    }
    if ($LASTEXITCODE -ne 0) { Write-Error "Falha na compilação do Inno Setup." }
    Write-Host "[OK] Instalador gerado: dist/fotonPDF_Setup_v${codeVersion}.exe" -ForegroundColor Green
}

# 7. Gerar ZIP Portátil
Write-Host "`n[6/6] Gerando Artefatos Complementares (ZIP Portátil e Release Notes)..." -ForegroundColor Yellow
$zipPath = "dist\fotonPDF-portable-v${codeVersion}.zip"
Write-Host "  -> Compactando dist\foton\* em $zipPath"
Compress-Archive -Path "dist\foton\*" -DestinationPath $zipPath -Force

# 8. Preparar Release Notes
$templatePath = ".github\RELEASE_TEMPLATE.md"
$notesPath = "dist\release_notes.md"
Write-Host "  -> Gerando $notesPath a partir do template"
$template = Get-Content $templatePath -Raw -Encoding utf8
$notes = $template -replace '\{\{VERSION\}\}', $codeVersion
$notes | Out-File -Encoding utf8 $notesPath
Write-Host "[OK] Artefatos complementares gerados." -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🎉 SIMULAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Cyan
Write-Host "Arquivos gerados na pasta dist/:" -ForegroundColor White
Get-ChildItem -Path "dist\" -File | Select-Object Name, @{Name = "Size(MB)"; Expression = { "{0:N2}" -f ($_.Length / 1MB) } } | Format-Table -AutoSize
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Você pode analisar os arquivos acima. Se estiver tudo OK, você pode fazer o Push para mesclar a branch e criar a Tag Git oficial." -ForegroundColor Yellow
