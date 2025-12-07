import sys
import os
import fitz  # PyMuPDF

def merge_pdfs(input_pdf_paths):
    """
    複数のPDFを結合して1つのPDFにする関数
    出力ファイル名は最初のPDFのファイル名に _merged.pdf を付ける

    Args:
        input_pdf_paths (list[str]): 結合対象のPDFファイルパス
    """

    try:
        # 出力ファイル名を生成
        first_pdf = input_pdf_paths[0]
        base, ext = os.path.splitext(first_pdf)
        output_pdf_path = f"{base}_merged.pdf"

        merged_doc = fitz.open()

        # 入力PDFを順番に追加
        for pdf_path in input_pdf_paths:
            print(f"追加中: {pdf_path}")
            with fitz.open(pdf_path) as doc:
                merged_doc.insert_pdf(doc)

        # 保存
        merged_doc.save(output_pdf_path)
        merged_doc.close()

        print(f"成功: {len(input_pdf_paths)} 個のPDFを結合して '{output_pdf_path}' に保存しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python merge_pdfs.py <input1.pdf> <input2.pdf> ...")
        sys.exit(1)

    input_pdfs = sys.argv[1:]
    merge_pdfs(input_pdfs)
