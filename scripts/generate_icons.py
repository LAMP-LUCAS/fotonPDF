import sys
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication

def generate_ico():
    # Precisamos de um app para o processamento de imagens do Qt
    app = QApplication(sys.argv)
    
    project_root = Path(__file__).parents[1]
    svg_path = project_root / "docs" / "brand" / "logo.svg"
    ico_path = project_root / "docs" / "brand" / "logo.ico"
    
    if not svg_path.exists():
        print(f"Erro: {svg_path} não encontrado.")
        return

    print(f"🎨 Convertendo {svg_path.name} para {ico_path.name}...")
    
    icon = QIcon(str(svg_path))
    # Gerar um pixmap de alta qualidade (256x256 é padrão para windows)
    pixmap = icon.pixmap(QSize(256, 256))
    
    if pixmap.isNull():
        print("Erro: Falha ao carregar SVG. Verifique se o plugin SVG do Qt está instalado.")
        return
        
    pixmap.save(str(ico_path), "ICO")
    print("✅ Ícone gerado com sucesso!")

if __name__ == "__main__":
    generate_ico()
