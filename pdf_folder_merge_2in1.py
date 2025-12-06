import os
import sys
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


def render_page_to_b5(page):
    """Render PDF page to B5-sized PIL image."""
    zoom_x = B5_WIDTH_PX / page.rect.width
    zoom_y = B5_HEIGHT_PX / page.rect.height
    mat = fitz.Matrix(zoom_x, zoom_y)

    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # 必ずB5にリサイズ（微妙なズレ補正）
    img = img.resize(B5_SIZE, Image.LANCZOS)
    return img


def make_2in1_b4(img1, img2):
    """Combine two B5 pages into a single B4 page."""
    canvas = Image.new("RGB", B4_SIZE, (255, 255, 255))
    canvas.paste(img1, (0, 0))
    canvas.paste(img2, (B5_WIDTH_PX, 0))
    return canvas


def merge_and_2in1(input_dir):
    if not os.path.isdir(input_dir):
        print("指定されたディレクトリが存在しません:", input_dir)
        return

    # PDFファイルをソート
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    pdf_files.sort()

    if not pdf_files:
        print("PDFファイルが見つかりません:", input_dir)
        return

    print("読み込むPDF:", pdf_files)

    # 出力先
    dir_name = os.path.basename(os.path.normpath(input_dir))
    output_pdf = os.path.join(os.path.dirname(input_dir), f"{dir_name}_merged_2in1_B4.pdf")

    # === PDF全ページをB5画像として展開 ===
    b5_pages = []

    for pdf_name in pdf_files:
        path = os.path.join(input_dir, pdf_name)
        doc = fitz.open(path)

        for page in doc:
            b5_img = render_page_to_b5(page)
            b5_pages.append(b5_img)

    # === 奇数なら白紙B5を追加 ===
    if len(b5_pages) % 2 == 1:
        b5_pages.append(Image.new("RGB", B5_SIZE, (255, 255, 255)))

    # === 2in1 B4ページの生成 ===
    b4_pages = []
    for i in range(0, len(b5_pages), 2):
        merged = make_2in1_b4(b5_pages[i], b5_pages[i + 1])
        b4_pages.append(merged)

    # === PDF出力 ===
    first = b4_pages[0]
    rest = b4_pages[1:]

    first.save(
        output_pdf,
        save_all=True,
        append_images=rest,
        resolution=DPI
    )

    print("2in1マージPDFを作成しました:", output_pdf)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python pdf_folder_merge_2in1.py <PDFフォルダ>")
        sys.exit(1)

    merge_and_2in1(sys.argv[1])
