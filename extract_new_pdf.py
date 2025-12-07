import fitz # PyMuPDF

def extract_pages_to_new_pdf(input_pdf_path, output_pdf_path, page_numbers_to_extract):
    """
    指定されたPDFから特定のページを抽出して新しいPDFを作成する関数

    Args:
        input_pdf_path (str): 元のPDFファイルのパス
        output_pdf_path (str): 新しく作成するPDFファイルのパス
        page_numbers_to_extract (list[int]): 抽出したいページ番号のリスト (0始まり)
    """
    try:
        # 元のPDFファイルを開く
        doc = fitz.open(input_pdf_path)
        # 新しいPDFドキュメントを作成
        new_doc = fitz.open()

        # 指定されたページを抽出して新しいドキュメントに追加
        for page_num in page_numbers_to_extract:
            if 0 <= page_num < doc.page_count:
                page = doc.load_page(page_num)
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num) # ページを挿入

        # 新しいPDFファイルを保存
        new_doc.save(output_pdf_path)
        new_doc.close()
        doc.close()
        print(f"成功: {input_pdf_path} からページ {page_numbers_to_extract} を抽出して {output_pdf_path} に保存しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# --- 使用例 ---
input_pdf = "2020.pdf"  # ここに元のPDFファイル名を入力
output_pdf = "extracted_pages.pdf" # ここに新しいPDFファイル名を入力
pages_to_extract_range = list(range(41, 51))  # 抽出したいページ番号の範囲 
extract_pages_to_new_pdf(input_pdf, output_pdf, pages_to_extract_range)
