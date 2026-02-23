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
    
    # Configurações do PyInstaller via foton.spec oficial
    spec_file = project_root / "foton.spec"
    
    if not spec_file.exists():
        print(f"[ERRO CRÍTICO] O arquivo spec '{spec_file}' não foi encontrado.")
        sys.exit(1)
        
    params = [
        str(spec_file),
        "--noconfirm",       # Não pedir confirmação para sobrescrever
        "--clean",
        f"--distpath={project_root / 'dist'}",
        f"--workpath={project_root / 'build'}"
    ]
    
    # Executar build
    PyInstaller.__main__.run(params)
    print("[OK] Build concluido! O executavel esta na pasta /dist")

if __name__ == "__main__":
    build()
