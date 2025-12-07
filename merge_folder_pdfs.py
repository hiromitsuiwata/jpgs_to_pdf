import sys
import os
import fitz  # PyMuPDF

def merge_pdfs_in_folder(input_folder):
    """
    指定フォルダ内（再帰なし）の PDF をすべて結合して 1 ファイルにまとめる

    出力ファイル名: <フォルダ名>_merged.pdf

    Args:
        input_folder (str): PDF が入っているフォルダ
    """

    try:
        if not os.path.isdir(input_folder):
            print(f"エラー: フォルダが見つかりません: {input_folder}")
            return

        # PDFファイル一覧を取得（拡張子 .pdf のみ）
        pdf_files = [
            os.path.join(input_folder, f)
            for f in os.listdir(input_folder)
            if f.lower().endswith(".pdf")
        ]

        if not pdf_files:
            print("PDF ファイルがフォルダ内にありません。")
            return

        # ファイル名順に並べ替え
        pdf_files.sort()

        # 出力ファイル名を作成
        folder_name = os.path.basename(os.path.abspath(input_folder))
        output_pdf_path = os.path.join(input_folder, f"{folder_name}_merged.pdf")

        merged_doc = fitz.open()

        # PDFを順番に追加
        for pdf_path in pdf_files:
            print(f"追加中: {pdf_path}")
            with fitz.open(pdf_path) as doc:
                merged_doc.insert_pdf(doc)

        # 保存
        merged_doc.save(output_pdf_path)
        merged_doc.close()

        print(f"成功: {len(pdf_files)} 個のPDFを結合して '{output_pdf_path}' に保存しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python merge_folder_pdfs.py <folder_path>")
        sys.exit(1)

    input_folder = sys.argv[1]
    merge_pdfs_in_folder(input_folder)
