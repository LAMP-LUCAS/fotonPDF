import PyInstaller.__main__
import os
from pathlib import Path

def build():
    from src import __version__
    print(f"🚀 Iniciando build do fotonPDF v{__version__}...")
    
    # Caminhos
    scripts_path = Path(__file__).parent
    project_root = scripts_path.parent
    entry_point = project_root / "src" / "interfaces" / "cli" / "main.py"
    
    # Configurações do PyInstaller
    params = [
        str(entry_point),
        "--name=foton",
        "--onefile", # Binário único
        "--windowed", # Não abrir console
        "--clean",
        f"--add-data={project_root / 'src'};src", # Incluir todo o código fonte
        "--hidden-import=PyQt6",
        "--hidden-import=fitz",
        "--hidden-import=requests",
        "--hidden-import=plyer",
        # Excluir pacotes pesados do ambiente global que não são usados
        "--exclude-module=torch",
        "--exclude-module=matplotlib",
        "--exclude-module=pandas",
        "--exclude-module=numpy",
        "--exclude-module=PIL",
        "--exclude-module=tkinter",
    ]
    
    # Executar build
    PyInstaller.__main__.run(params)
    print("✅ Build concluído! O executável está na pasta /dist")

if __name__ == "__main__":
    build()
