import fitz
import os

def create_complex_pdf(path, pages=106):
    doc = fitz.open()
    toc = []
    
    # Adicionar páginas de tamanhos diferentes
    for i in range(pages):
        # Alternar entre A4 e A3
        is_a3 = (i % 5 == 0)
        width = 842 if is_a3 else 595 # A3 landscape vs A4 portrait
        height = 1191 if is_a3 else 842
        
        page = doc.new_page(width=width, height=height)
        
        # Conteúdo visual
        rect = fitz.Rect(50, 50, 500, 150)
        fmt = "A3" if is_a3 else "A4"
        page.insert_textbox(rect, f"Página {i+1} - Formato {fmt}\nEste é um documento de teste com {pages} páginas.", fontsize=18)
        
        # Desenhar uma borda
        page.draw_rect(page.rect, color=(0, 0, 1), width=2)
        
        # Bookmark (Hierárquico)
        if i % 10 == 0:
            level = 1
            toc.append([level, f"Seção Principal {i//10 + 1}", i+1])
        elif i % 10 == 3:
            level = 2
            toc.append([level, f"Subseção {i//10 + 1}.1", i+1])

    doc.set_toc(toc)
    doc.save(path)
    doc.close()
    print(f"Sucesso: {path} criado com {pages} páginas (Mix A3/A4).")

if __name__ == "__main__":
    create_complex_pdf("test_complex.pdf")
