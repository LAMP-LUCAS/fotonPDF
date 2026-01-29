
import fitz  # PyMuPDF
import sys
import random
from pathlib import Path

def generate_large_dimensions_pdf(filename="test_large_a0.pdf"):
    """Gera um PDF com dimensões A0 (841 x 1189 mm)."""
    doc = fitz.open()
    # A0 em pontos (1 mm = 2.83465 pt)
    width = 841 * 2.83465
    height = 1189 * 2.83465
    page = doc.new_page(width=width, height=height)
    
    # Adicionar marcas de canto e centro
    shape = page.new_shape()
    shape.draw_rect(fitz.Rect(0, 0, width, height))
    shape.draw_line((0, 0), (width, height))
    shape.draw_line((0, height), (width, 0))
    shape.draw_circle((width/2, height/2), 100)
    
    # Texto de aviso
    shape.insert_text((width/2 - 100, height/2), "A0 TEST FILE", fontsize=72, color=(1, 0, 0))
    shape.finish(color=(0, 0, 1), width=2)
    shape.commit()
    
    doc.save(filename)
    print(f"Gerado: {filename}")

def generate_many_elements_pdf(filename="test_many_elements.pdf", count=5000):
    """Gera um PDF com milhares de elementos vetoriais."""
    doc = fitz.open()
    page = doc.new_page() # A4 padrão
    
    shape = page.new_shape()
    
    for _ in range(count):
        x = random.uniform(0, 500)
        y = random.uniform(0, 800)
        w = random.uniform(5, 50)
        h = random.uniform(5, 50)
        color = (random.random(), random.random(), random.random())
        
        shape.draw_rect(fitz.Rect(x, y, x+w, y+h))
        shape.finish(color=color, fill=color, width=0.5)
        
    shape.commit()
    doc.save(filename)
    print(f"Gerado: {filename} com {count} elementos")

def generate_lorem_ipsum_pdf(filename="test_lorem_ipsum.pdf", pages=50):
    """Gera um PDF com muitas páginas de texto."""
    lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. """ * 10
    
    doc = fitz.open()
    
    for i in range(pages):
        page = doc.new_page()
        text_rect = fitz.Rect(50, 50, 550, 800)
        page.insert_textbox(text_rect, f"Page {i+1}\n\n{lorem * 3}", fontsize=11, align=0)
        
    doc.save(filename)
    print(f"Gerado: {filename} com {pages} páginas")

if __name__ == "__main__":
    output_dir = Path("test_files")
    output_dir.mkdir(exist_ok=True)
    
    print("Iniciando geração de arquivos de teste...")
    generate_large_dimensions_pdf(output_dir / "test_A0.pdf")
    generate_many_elements_pdf(output_dir / "test_complex_vectors.pdf")
    generate_lorem_ipsum_pdf(output_dir / "test_multi_page_text.pdf")
    print("Concluído.")
