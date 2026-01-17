import PyInstaller.__main__
import os
from pathlib import Path

def build():
    print("🚀 Iniciando build do fotonPDF v1.0.0...")
    
    # Caminhos
    base_path = Path(__file__).parent
    entry_point = base_path / "src" / "interfaces" / "cli" / "main.py"
    
    # Configurações do PyInstaller
    params = [
        str(entry_point),
        "--name=foton",
        "--onefile", # Binário único
        "--windowed", # Não abrir console
        "--clean",
        f"--add-data=src;src", # Incluir todo o código fonte
        "--hidden-import=PyQt6",
        "--hidden-import=fitz",
        "--hidden-import=requests",
        "--hidden-import=plyer",
    ]
    
    # Executar build
    PyInstaller.__main__.run(params)
    print("✅ Build concluído! O executável está na pasta /dist")

if __name__ == "__main__":
    build()
