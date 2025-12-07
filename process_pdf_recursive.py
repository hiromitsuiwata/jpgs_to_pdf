import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import os
import sys


# ------------------------------------------------------------
# 1. 完全白紙ページ判定（RGB全255）
# ------------------------------------------------------------
def is_completely_white(page):
    pix = page.get_pixmap(dpi=100)  # 低dpiで高速化
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    arr = np.asarray(img)

    return arr.max() == 255 and arr.min() == 255


# ------------------------------------------------------------
# 2. 白紙削除 & kokugo の場合はページ逆順
# ------------------------------------------------------------
def clean_and_reorder(pdf_path):
    doc = fitz.open(pdf_path)

    # 白紙削除
    non_white_pages = []
    for i, page in enumerate(doc):
        if not is_completely_white(page):
            non_white_pages.append(i)

    # 新しいPDFへコピー
    new_doc = fitz.open()

    if "kokugo" in os.path.basename(pdf_path).lower():
        page_order = reversed(non_white_pages)
    else:
        page_order = non_white_pages

    for i in page_order:
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    doc.close()
    return new_doc


# ------------------------------------------------------------
# 3. B5ページ → 400dpi 2in1 B4 ページ化
# ------------------------------------------------------------
def convert_to_b4_2in1(doc):
    B4_WIDTH = 728  # 257mm * 2.835 (fitz pixel per point conversion) ではない
    B4_HEIGHT = 1031  # fitzはポイントなので後で調整

    # 正しいB4サイズ（fitzはポイント：1pt=1/72inch）
    B4_WIDTH_PT = 72 * 10.12   # B4: 257mm = 10.12インチ
    B4_HEIGHT_PT = 72 * 14.33  # B4: 364mm = 14.33インチ

    # 新PDF
    out = fitz.open()

    pages = [p for p in doc]
    total = len(pages)

    # 2ページずつ処理
    for i in range(0, total, 2):
        left_page = pages[i]

        # 新規B4ページ
        new_page = out.new_page(width=B4_WIDTH_PT, height=B4_HEIGHT_PT)

        # 左ページを400dpiレンダリング
        left_pix = left_page.get_pixmap(dpi=400)
        left_rect = fitz.Rect(0, 0, B4_WIDTH_PT / 2, B4_HEIGHT_PT)
        new_page.insert_image(left_rect, pixmap=left_pix)

        # 右ページがあれば挿入
        if i + 1 < total:
            right_page = pages[i + 1]
            right_pix = right_page.get_pixmap(dpi=400)
            right_rect = fitz.Rect(B4_WIDTH_PT / 2, 0, B4_WIDTH_PT, B4_HEIGHT_PT)
            new_page.insert_image(right_rect, pixmap=right_pix)

    return out


# ------------------------------------------------------------
# 再帰処理でフォルダ内すべてのPDFを処理
# ------------------------------------------------------------
def process_folder_recursive(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            input_pdf = os.path.join(root, file)

            # 出力先フォルダを構造ごと作成
            rel_path = os.path.relpath(root, input_dir)
            out_dir = os.path.join(output_dir, rel_path)
            os.makedirs(out_dir, exist_ok=True)

            out_name = os.path.splitext(file)[0] + "_processed.pdf"
            output_pdf = os.path.join(out_dir, out_name)

            print(f"Processing: {input_pdf}")

            # Step1, Step2
            cleaned_doc = clean_and_reorder(input_pdf)

            # Step3
            final_doc = convert_to_b4_2in1(cleaned_doc)

            # Save
            final_doc.save(output_pdf)
            final_doc.close()
            cleaned_doc.close()

            print(f" → Saved: {output_pdf}\n")


# ------------------------------------------------------------
# メイン
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 3:
        print("使い方: python process_pdf_recursive.py <input_dir> <output_dir>")
        return

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    process_folder_recursive(input_dir, output_dir)


if __name__ == "__main__":
    main()
