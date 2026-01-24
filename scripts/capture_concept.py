import sys
import os
import subprocess
from pathlib import Path

def capture_concept():
    """
    Captura uma screenshot do concept.html usando Playwright.
    Instala as dependências se necessário.
    """
    project_root = Path(__file__).parent.parent.resolve()
    html_file = project_root / "docs" / "visuals" / "concept.html"
    output_dir = project_root / "docs" / "visuals" / "captures"
    output_file = output_dir / "concept_mockup.png"

    # 1. Garantir que a pasta de captures existe
    output_dir.mkdir(parents=True, exist_ok=True)

    if not html_file.exists():
        print(f"❌ Erro: Arquivo {html_file} não encontrado.")
        return

    print("🚀 Iniciando processo de captura visual...")

    try:
        # Tentar importar playwright, instalar se necessário
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("📦 Playwright não encontrado. Instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            print("🌐 Abrindo navegador...")
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Converter caminho local para URL
            file_url = f"file:///{str(html_file).replace(os.sep, '/')}"
            print(f"📄 Carregando: {file_url}")
            
            page.goto(file_url)
            # Esperar o carregamento completo e fontes
            page.wait_for_load_state("networkidle")
            
            # Tirar screenshot full-page
            print(f"📸 Capturando screenshot...")
            page.screenshot(path=str(output_file), full_page=True)
            
            browser.close()
            print(f"✨ Sucesso! Mockup salvo em: {output_file}")

    except Exception as e:
        print(f"❌ Erro durante a captura: {e}")
        print("\n💡 Dica: Se falhar, instale manualmente:")
        print("   pip install playwright")
        print("   playwright install chromium")

if __name__ == "__main__":
    capture_concept()
