import PyInstaller.__main__
import os
from pathlib import Path

def build():
    import sys
    # Adicionar raíz do projeto ao sys.path para permitir import de 'src'
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
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
        "--console", # Habilita console para wizards de setup/uninstall
        "--clean",
        f"--distpath={project_root / 'dist'}",
        f"--workpath={project_root / 'build'}",
        f"--specpath={project_root}",
        f"--add-data={project_root / 'src'};src", # Incluir todo o código fonte
        "--hidden-import=plyer.platforms.win.notification",
        "--hidden-import=plyer.platforms.linux.notification",
        # PyQt6 - incluir submodulos principais
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.sip",
        # Outras dependências
        "--hidden-import=fitz",
        "--hidden-import=requests",
        "--hidden-import=plyer",
        "--hidden-import=click",
        # Coletar todos os binários do PyQt6
        "--collect-all=PyQt6",
        # Excluir pacotes pesados do ambiente global
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
