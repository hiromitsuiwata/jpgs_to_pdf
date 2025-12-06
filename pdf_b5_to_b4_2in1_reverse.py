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


def render_page_to_b5(page):
    """Render PDF page to B5-sized PIL image."""
    zoom_x = B5_WIDTH_PX / page.rect.width
    zoom_y = B5_HEIGHT_PX / page.rect.height
    mat = fitz.Matrix(zoom_x, zoom_y)

    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # 必ずB5に統一
    img = img.resize(B5_SIZE, Image.LANCZOS)
    return img


def make_2in1_b4_correct(left_img, right_img):
    """
    正しい縦書き配置（右ページは右側に配置）

        [左ページ][右ページ]

    ※ページの読み順は reverse（後→先）で処理する。
    """
    canvas = Image.new("RGB", B4_SIZE, (255, 255, 255))
    canvas.paste(left_img, (0, 0))               # 左ページを左側へ
    canvas.paste(right_img, (B5_WIDTH_PX, 0))    # 右ページを右側へ
    return canvas


def pdf_to_2in1_reverse(input_pdf):
    if not os.path.isfile(input_pdf):
        print("PDFファイルが存在しません:", input_pdf)
        return

    base = os.path.splitext(input_pdf)[0]
    output_pdf = f"{base}_2in1_B4_reverse.pdf"

    doc = fitz.open(input_pdf)

    # === ページを逆順に並べる（3→2→1） ===
    reversed_pages = list(doc)[::-1]

    # === 各ページをB5画像へ ===
    b5_pages = [render_page_to_b5(p) for p in reversed_pages]

    # === 奇数ページなら白紙追加 ===
    if len(b5_pages) % 2 == 1:
        b5_pages.append(Image.new("RGB", B5_SIZE, (255, 255, 255)))

    # === 正しい縦書き2in1（左右反転せず） ===
    b4_pages = []
    for i in range(0, len(b5_pages), 2):
        left_page  = b5_pages[i]
        right_page = b5_pages[i + 1]
        merged = make_2in1_b4_correct(left_page, right_page)
        b4_pages.append(merged)

    # === PDFとして出力 ===
    first = b4_pages[0]
    rest = b4_pages[1:]

    first.save(
        output_pdf,
        save_all=True,
        append_images=rest,
        resolution=DPI
    )

    print("修正済み 2in1（反転）PDF を作成しました:", output_pdf)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python pdf_b5_to_b4_2in1_reverse.py <入力PDFファイル>")
        sys.exit(1)

    pdf_to_2in1_reverse(sys.argv[1])
