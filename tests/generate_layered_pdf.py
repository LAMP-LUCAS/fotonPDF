import fitz

def create_layered_pdf(filename="test_layers.pdf"):
    doc = fitz.open()
    page = doc.new_page()

    # Create OCGs
    ocg1 = doc.add_ocg("Background (Red)", on=True)
    ocg2 = doc.add_ocg("Foreground (Blue)", on=True)

    # Draw Red Circle in Background Layer
    page.draw_circle((100, 100), 50, color=(1, 0, 0), fill=(1, 0, 0), oc=ocg1)
    
    # Draw Blue Rect in Foreground Layer
    page.draw_rect((100, 100, 200, 200), color=(0, 0, 1), fill=(0, 0, 1), oc=ocg2)
    
    # Draw Text in both
    page.insert_text((50, 300), "This text is always visible", fontsize=20, color=(0,0,0))
    page.insert_text((50, 350), "Red Layer", fontsize=15, color=(1,0,0), oc=ocg1)
    page.insert_text((50, 380), "Blue Layer", fontsize=15, color=(0,0,1), oc=ocg2)

    doc.save(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    create_layered_pdf()
