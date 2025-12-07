# process_pdf_lightweight_fixed.py
import fitz
import os
import sys

def is_completely_white(page):
    text = page.get_text().strip()
    if text:
        return False

    xobjs = page.get_xobjects()
    images = [k for k in xobjs if xobjs[k]["type"] == fitz.PDF_XOBJECT_IMAGE]
    if images:
        return False

    drawings = page.get_drawings()
    if drawings:
        return False

    return True

def clean_and_reorder(pdf_path):
    doc = fitz.open(pdf_path)
    non_white_pages = [i for i, p in enumerate(doc) if not is_completely_white(p)]
    new_doc = fitz.open()
    filename = os.path.basename(pdf_path).lower()
    if "kokugo" in filename:
        page_order = reversed(non_white_pages)
    else:
        page_order = non_white_pages

    for i in page_order:
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    doc.close()
    return new_doc

def convert_to_b4_2in1(doc):
    B4_HEIGHT_PT = 72 * 10.12
    B4_WIDTH_PT = 72 * 14.33

    out = fitz.open()
    page_count = len(doc)

    for i in range(0, page_count, 2):
        new_page = out.new_page(width=B4_WIDTH_PT, height=B4_HEIGHT_PT)
        left_rect = fitz.Rect(0, 0, B4_WIDTH_PT / 2, B4_HEIGHT_PT)
        new_page.show_pdf_page(left_rect, doc, i)
        if i + 1 < page_count:
            right_rect = fitz.Rect(B4_WIDTH_PT / 2, 0, B4_WIDTH_PT, B4_HEIGHT_PT)
            new_page.show_pdf_page(right_rect, doc, i + 1)
    return out

def process_folder_recursive(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue
            input_pdf = os.path.join(root, file)
            rel_path = os.path.relpath(root, input_dir)
            out_dir = os.path.join(output_dir, rel_path)
            os.makedirs(out_dir, exist_ok=True)
            out_filename = os.path.splitext(file)[0] + "_processed.pdf"
            output_pdf = os.path.join(out_dir, out_filename)
            print("Processing:", input_pdf)
            cleaned = clean_and_reorder(input_pdf)
            final_doc = convert_to_b4_2in1(cleaned)
            final_doc.save(output_pdf)
            final_doc.close()
            cleaned.close()
            print(" → Saved:", output_pdf)

def main():
    if len(sys.argv) < 3:
        print("Usage: python process_pdf_lightweight_fixed.py <input_dir> <output_dir>")
        return
    process_folder_recursive(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
