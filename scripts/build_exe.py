import PyInstaller.__main__
import os
from pathlib import Path

def build():
    import sys
    # Adicionar raíz do projeto ao sys.path para permitir import de 'src'
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
    os.environ['PYINSTALLER_BUILD'] = '1'
    from src import __version__
    print(f"[BUILD] Iniciando build do fotonPDF v{__version__}...")
    
    # IMPORTANTE: src/__init__.py é o ÚNICO Centro de Verdade para a versão.
    # O pipeline de CD no GitHub Actions validará se esta versão coincide com a Tag.
    
    # Caminhos
    scripts_path = Path(__file__).parent
    project_root = scripts_path.parent
    entry_point = project_root / "src" / "interfaces" / "cli" / "main.py"
    
    # Configurações do PyInstaller
    params = [
        str(entry_point),
        "--name=foton_v1.0.0",
        f"--icon={project_root / 'docs' / 'brand' / 'logo.ico'}",
        "--onedir",          # Modo diretório para estabilidade e velocidade
        "--noconfirm",       # Não pedir confirmação para sobrescrever
        "--console",         # Mantemos console para os wizards de sistema
        "--clean",
        f"--distpath={project_root / 'dist'}",
        f"--workpath={project_root / 'build'}",
        f"--specpath={project_root}",
        f"--add-data={project_root / 'src'};src",
        f"--add-data={project_root / 'docs' / 'brand'};docs/brand",
        # Notificações
        "--hidden-import=plyer.platforms.win.notification",
        # PyQt6 - Modo Diretório é muito mais seguro com collect-all
        "--collect-all=PyQt6",
        "--collect-all=litellm",
        "--collect-all=instructor",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui", 
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.sip",
        "--hidden-import=litellm",
        "--hidden-import=instructor",
        # PDF e outras dependências
        "--hidden-import=fitz",
        "--hidden-import=fitz.fitz",
        "--hidden-import=requests",
        "--hidden-import=plyer",
        "--hidden-import=click",
        # Excluir pacotes gigantescos
        "--exclude-module=torch",
        "--exclude-module=matplotlib",
        "--exclude-module=pandas",
        "--exclude-module=numpy",
        "--exclude-module=PIL",
        "--exclude-module=tkinter",
    ]
    
    # Executar build
    PyInstaller.__main__.run(params)
    print("[OK] Build concluido! O executavel esta na pasta /dist")

if __name__ == "__main__":
    build()
