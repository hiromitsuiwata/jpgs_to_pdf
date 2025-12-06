import sys
import os
import fitz  # PyMuPDF
from PIL import Image

# === constant: B5 at 400dpi ===
DPI = 400
B5_WIDTH_PX = int(182 / 25.4 * DPI)
B5_HEIGHT_PX = int(257 / 25.4 * DPI)
B5_SIZE = (B5_WIDTH_PX, B5_HEIGHT_PX)

# === 2in1 B4 size ===
B4_WIDTH_PX = B5_WIDTH_PX * 2
B4_HEIGHT_PX = B5_HEIGHT_PX
B4_SIZE = (B4_WIDTH_PX, B4_HEIGHT_PX)


def render_pdf_page_to_b5(fitz_page):
    """Render PDF page to a B5-sized PIL image."""
    zoom_x = B5_WIDTH_PX / fitz_page.rect.width
    zoom_y = B5_HEIGHT_PX / fitz_page.rect.height
    mat = fitz.Matrix(zoom_x, zoom_y)

    pix = fitz_page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # If rendered size differs slightly, resize to exact B5
    img = img.resize(B5_SIZE, Image.LANCZOS)
    return img


def make_2in1_b4(img1, img2):
    """Combine two B5 images into a single B4 landscape page."""
    canvas = Image.new("RGB", B4_SIZE, (255, 255, 255))
    canvas.paste(img1, (0, 0))
    canvas.paste(img2, (B5_WIDTH_PX, 0))
    return canvas


def pdf_to_2in1(input_pdf):
    if not os.path.isfile(input_pdf):
        print("PDFファイルが存在しません:", input_pdf)
        return

    base = os.path.splitext(input_pdf)[0]
    output_pdf = f"{base}_2in1_B4.pdf"

    doc = fitz.open(input_pdf)

    # Render each page as B5 image
    b5_pages = [render_pdf_page_to_b5(page) for page in doc]

    # If odd, add a blank page
    if len(b5_pages) % 2 == 1:
        b5_pages.append(Image.new("RGB", B5_SIZE, (255, 255, 255)))

    # Create all B4 (2in1) pages
    b4_pages = []
    for i in range(0, len(b5_pages), 2):
        merged = make_2in1_b4(b5_pages[i], b5_pages[i + 1])
        b4_pages.append(merged)

    # Save to PDF
    first = b4_pages[0]
    rest = b4_pages[1:]
    first.save(output_pdf, save_all=True, append_images=rest, resolution=DPI)

    print("2in1 PDF を作成しました:", output_pdf)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python pdf_b5_to_b4_2in1.py <入力PDFファイル>")
        sys.exit(1)

    pdf_to_2in1(sys.argv[1])
