import os
import subprocess
import sys
from pathlib import Path

def sign_executable(file_path: Path):
    """
    Assina um executável usando um certificado auto-assinado.
    Se o certificado não existir, tenta criar um via PowerShell.
    """
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False

    cert_name = "fotonPDF_Dev_Cert"
    pfx_path = Path(__file__).parent / f"{cert_name}.pfx"
    password = "foton_dev_safe"

    # 1. Verificar/Criar Certificado
    if not pfx_path.exists():
        print("🛠️ Gerando certificado auto-assinado para desenvolvimento...")
        try:
            # Comando PowerShell para gerar certificado e exportar para PFX
            ps_cmd = f"""
            $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN={cert_name}" -HashAlgorithm sha256 -KeyLength 2048 -NotAfter (Get-Date).AddYears(1)
            $pwd = ConvertTo-SecureString -String "{password}" -Force -AsPlainText
            Export-PfxCertificate -Cert $cert -FilePath "{pfx_path}" -Password $pwd
            """
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            print(f"✅ Certificado gerado: {pfx_path}")
        except Exception as e:
            print(f"❌ Erro ao gerar certificado: {e}")
            return False

    # 2. Assinar artefato
    print(f"🔏 Assinando {file_path.name}...")
    try:
        # Tenta usar o SignTool do Windows SDK se estiver no PATH
        # Caso contrário, informa o usuário
        sign_cmd = [
            "signtool", "sign",
            "/f", str(pfx_path),
            "/p", password,
            "/fd", "SHA256",
            "/td", "SHA256",
            "/tr", "http://timestamp.digicert.com",
            str(file_path)
        ]
        
        # Signtool costuma estar em "C:\Program Files (x86)\Windows Kits\10\bin\<version>\x64\signtool.exe"
        # Mas vamos assumir que pode estar no PATH ou falhar graciosamente
        subprocess.run(sign_cmd, check=True)
        print("✨ Assinatura aplicada com sucesso!")
        return True
    except FileNotFoundError:
        print("⚠️ 'signtool' não encontrado no PATH.")
        print("   Para assinar oficialmente, instale o Windows SDK e adicione o SignTool ao seu PATH.")
        print("   A infraestrutura de certificado (.pfx) foi preparada.")
        return False
    except Exception as e:
        print(f"❌ Erro ao assinar: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        # Default para o caminho padrão de build
        target = Path(__file__).parent.parent / "dist" / "foton" / "foton.exe"
    
    sign_executable(target)
