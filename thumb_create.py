import fitz  # PyMuPDF
from PIL import Image
import io

def pdf_to_fixed_thumbnail(pdf_path, thumbnail_path='thumbnail.jpg', max_size_kb=20, output_size=(300, 300), scale=2.0):
    # Load PDF and first page
    doc = fitz.open(pdf_path)
    if doc.page_count < 1:
        raise ValueError("PDF has no pages.")
    page = doc.load_page(0)

    # Render PDF page as image
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Resize image maintaining aspect ratio
    img.thumbnail(output_size, Image.LANCZOS)

    # Create white background
    background = Image.new("RGB", output_size, (255, 255, 255))

    # Paste the resized image centered on the background
    offset = ((output_size[0] - img.width) // 2, (output_size[1] - img.height) // 2)
    background.paste(img, offset)

    # Save with compression to ensure it's below size limit
    quality = 95
    while quality >= 10:
        buffer = io.BytesIO()
        background.save(buffer, format="JPEG", quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb:
            with open(thumbnail_path, "wb") as f:
                f.write(buffer.getvalue())
            print(f"Saved to {thumbnail_path}, Size: {size_kb:.2f} KB, Quality: {quality}")
            return
        quality -= 5

    raise RuntimeError("Unable to compress image below 20KB.")

# Example usage:
# pdf_to_fixed_thumbnail("example.pdf")
