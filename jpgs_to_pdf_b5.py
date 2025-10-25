import os
import sys
from PIL import Image, ImageOps

# === B5サイズ（mm）を300dpiでピクセル換算 ===
DPI = 300
B5_WIDTH_PX = int(182 / 25.4 * DPI)
B5_HEIGHT_PX = int(257 / 25.4 * DPI)
B5_SIZE = (B5_WIDTH_PX, B5_HEIGHT_PX)

def open_with_orientation(path: str) -> Image.Image:
    """EXIFの回転情報を考慮して画像を開く"""
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")

def fill_to_b5(image: Image.Image) -> Image.Image:
    """
    画像をB5サイズに合わせて拡大・中央トリミングする（余白なし）
    """
    img = image.convert("RGB")
    img_ratio = img.width / img.height
    b5_ratio = B5_WIDTH_PX / B5_HEIGHT_PX

    # 拡大・トリミング方式
    if img_ratio > b5_ratio:
        # 横長 → 高さをB5に合わせて横をトリミング
        new_height = B5_HEIGHT_PX
        new_width = int(new_height * img_ratio)
    else:
        # 縦長 → 幅をB5に合わせて上下をトリミング
        new_width = B5_WIDTH_PX
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # 中央をB5サイズで切り出し
    left = (new_width - B5_WIDTH_PX) // 2
    top = (new_height - B5_HEIGHT_PX) // 2
    right = left + B5_WIDTH_PX
    bottom = top + B5_HEIGHT_PX
    img = img.crop((left, top, right, bottom))

    return img

def jpgs_to_pdf(input_dir):
    if not os.path.isdir(input_dir):
        print(f"指定されたディレクトリが存在しません: {input_dir}")
        return

    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.jpg')]
    files.sort()

    if not files:
        print(f"JPGファイルが見つかりません: {input_dir}")
        return

    dir_name = os.path.basename(os.path.normpath(input_dir))
    parent_dir = os.path.dirname(os.path.normpath(input_dir))
    output_pdf = os.path.join(parent_dir, f"{dir_name}_b5.pdf")

    first_image = fill_to_b5(open_with_orientation(os.path.join(input_dir, files[0])))
    images = [fill_to_b5(open_with_orientation(os.path.join(input_dir, f))) for f in files[1:]]

    first_image.save(output_pdf, save_all=True, append_images=images, resolution=DPI)
    print(f"PDFを作成しました（B5・{DPI}dpi・EXIF補正・余白なし）: {output_pdf}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python jpgs_to_pdf.py <画像ディレクトリ>")
        sys.exit(1)

    input_dir = sys.argv[1]
    jpgs_to_pdf(input_dir)
