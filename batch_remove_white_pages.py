import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import os
import sys

def is_white_page(page, threshold=255.0):
    """ページを画像化して白紙判定する"""
    pix = page.get_pixmap(dpi=72)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    avg = np.asarray(img).mean()
    print(avg)
    return avg >= threshold


def remove_white_pages(input_pdf, output_pdf, threshold=255.0):
    doc = fitz.open(input_pdf)
    new_doc = fitz.open()

    removed_pages = []

    for i, page in enumerate(doc):
        if is_white_page(page, threshold):
            removed_pages.append(i + 1)
        else:
            new_doc.insert_pdf(doc, from_page=i, to_page=i)

    # 元PDFが全部白紙の場合に空PDFになるのを避ける
    if len(new_doc) == 0:
        new_doc.new_page()

    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()

    print(f"[OK] {os.path.basename(input_pdf)} → {os.path.basename(output_pdf)}")
    print(f"     白紙ページ: {removed_pages}")


def batch_process(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 対象ファイルを選別
    pdf_files = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith(".pdf") and "mondai" in f.lower()
    ]

    if not pdf_files:
        print("対象となる'mondai'を含むPDFがありません。")
        return

    for filename in pdf_files:
        input_path = os.path.join(input_dir, filename)
        output_name = os.path.splitext(filename)[0] + "_no_white.pdf"
        output_path = os.path.join(output_dir, output_name)

        remove_white_pages(input_path, output_path)


def main():
    if len(sys.argv) < 3:
        print("使い方: python batch_remove_white_pages.py <input_dir> <output_dir>")
        return

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    batch_process(input_dir, output_dir)


if __name__ == "__main__":
    main()
