import os
import sys
from PIL import Image, ImageOps

# === constant: B5 at 400dpi ===
DPI = 400
B5_WIDTH_PX = int(182 / 25.4 * DPI)
B5_HEIGHT_PX = int(257 / 25.4 * DPI)
B5_SIZE = (B5_WIDTH_PX, B5_HEIGHT_PX)

# === 2in1 B4 size ===
# B4 landscape = two B5 pages side by side
B4_WIDTH_PX = B5_WIDTH_PX * 2
B4_HEIGHT_PX = B5_HEIGHT_PX
B4_SIZE = (B4_WIDTH_PX, B4_HEIGHT_PX)


def open_with_orientation(path: str) -> Image.Image:
    """Read JPG considering EXIF rotation."""
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")


def fill_to_b5(image: Image.Image) -> Image.Image:
    """Fit image into B5 by resizing and center-cropping."""
    img = image.convert("RGB")
    img_ratio = img.width / img.height
    b5_ratio = B5_WIDTH_PX / B5_HEIGHT_PX

    if img_ratio > b5_ratio:
        new_height = B5_HEIGHT_PX
        new_width = int(new_height * img_ratio)
    else:
        new_width = B5_WIDTH_PX
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - B5_WIDTH_PX) // 2
    top = (new_height - B5_HEIGHT_PX) // 2
    right = left + B5_WIDTH_PX
    bottom = top + B5_HEIGHT_PX

    return img.crop((left, top, right, bottom))


def make_2in1_b4_page(img1: Image.Image, img2: Image.Image) -> Image.Image:
    """Combine two B5 images into a single B4 (landscape) page."""
    canvas = Image.new("RGB", B4_SIZE, (255, 255, 255))
    canvas.paste(img1, (0, 0))
    canvas.paste(img2, (B5_WIDTH_PX, 0))
    return canvas


def jpgs_to_pdf_2in1(input_dir):
    if not os.path.isdir(input_dir):
        print(f"指定されたディレクトリが存在しません: {input_dir}")
        return

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(".jpg")]
    files.sort()

    if not files:
        print(f"JPGファイルが見つかりません: {input_dir}")
        return

    # Output file in parent directory
    dir_name = os.path.basename(os.path.normpath(input_dir))
    parent_dir = os.path.dirname(os.path.normpath(input_dir))
    output_pdf = os.path.join(parent_dir, f"{dir_name}_2in1_B4.pdf")

    # Convert each JPG into B5 image
    b5_images = [
        fill_to_b5(open_with_orientation(os.path.join(input_dir, f)))
        for f in files
    ]

    # If odd count, add a white B5 blank page
    if len(b5_images) % 2 == 1:
        b5_images.append(Image.new("RGB", B5_SIZE, (255, 255, 255)))

    # Create list of B4 pages
    b4_pages = []
    for i in range(0, len(b5_images), 2):
        page = make_2in1_b4_page(b5_images[i], b5_images[i + 1])
        b4_pages.append(page)

    # Save PDF
    first_page = b4_pages[0]
    rest_pages = b4_pages[1:]

    first_page.save(
        output_pdf,
        save_all=True,
        append_images=rest_pages,
        resolution=DPI,
    )

    print(f"PDFを作成しました: {output_pdf}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python jpgs_to_pdf_b4_2in1.py <画像ディレクトリ>")
        sys.exit(1)

    jpgs_to_pdf_2in1(sys.argv[1])
