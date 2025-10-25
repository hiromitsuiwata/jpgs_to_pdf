import os
import sys
from PIL import Image, ImageOps  # ← ImageOpsを追加

def jpgs_to_pdf(input_dir):
    # ディレクトリの存在確認
    if not os.path.isdir(input_dir):
        print(f"指定されたディレクトリが存在しません: {input_dir}")
        return

    # ファイル名順にjpgファイルを取得
    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.jpg')]
    files.sort()

    if not files:
        print(f"JPGファイルが見つかりません: {input_dir}")
        return

    # 出力PDFは「親ディレクトリ」に「ディレクトリ名.pdf」として作成
    dir_name = os.path.basename(os.path.normpath(input_dir))
    parent_dir = os.path.dirname(os.path.normpath(input_dir))
    output_pdf = os.path.join(parent_dir, f"{dir_name}.pdf")

    # EXIFの回転を反映して画像を開く関数
    def open_with_orientation(path):
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)  # ← 回転情報を反映
        return img.convert("RGB")

    # JPG画像を開いてPDFを生成
    first_image = open_with_orientation(os.path.join(input_dir, files[0]))
    images = [open_with_orientation(os.path.join(input_dir, f)) for f in files[1:]]

    first_image.save(output_pdf, save_all=True, append_images=images)
    print(f"PDFを作成しました（EXIF回転補正あり）: {output_pdf}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python jpgs_to_pdf.py <画像ディレクトリ>")
        sys.exit(1)

    input_dir = sys.argv[1]
    jpgs_to_pdf(input_dir)
