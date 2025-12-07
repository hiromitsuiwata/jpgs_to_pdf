import sys
import os
import fitz  # PyMuPDF

def extract_pages_to_new_pdf(input_pdf_path, start_page, end_page):
    """
    指定されたPDFからページ範囲を抽出して新しいPDFを作成する関数

    Args:
        input_pdf_path (str): 元のPDFファイルのパス
        start_page (int): 抽出開始ページ番号（1始まり）
        end_page (int): 抽出終了ページ番号（1始まり）
    """

    try:
        # 出力ファイルパス（末尾に _extracted を付ける）
        base, ext = os.path.splitext(input_pdf_path)
        output_pdf_path = f"{base}_extracted.pdf"

        # ページ番号を0始まりに変換
        start_idx = start_page - 1
        end_idx = end_page - 1

        # PDFオープン
        doc = fitz.open(input_pdf_path)
        new_doc = fitz.open()

        # ページ抽出
        for page_num in range(start_idx, end_idx + 1):
            if 0 <= page_num < doc.page_count:
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # 保存
        new_doc.save(output_pdf_path)
        new_doc.close()
        doc.close()

        print(f"成功: {input_pdf_path} の {start_page}〜{end_page} ページを '{output_pdf_path}' に保存しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    # コマンドライン引数の解析
    if len(sys.argv) != 4:
        print("使い方: python extract.py <input.pdf> <start_page> <end_page>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    start_page = int(sys.argv[2])
    end_page = int(sys.argv[3])

    extract_pages_to_new_pdf(input_pdf, start_page, end_page)
