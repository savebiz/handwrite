"""
app/shared/pdf_utils.py — Native PDF Detection, Rendering, and Conversion Utilities

Provides native PDF document support for HandWrite Verify using pypdf and PIL:
  - is_pdf(): Detects PDF files via file extension or %PDF- header magic bytes.
  - convert_pdf_to_image(): Renders/extracts Page 1 from PDF into a PIL Image / PNG file.
  - convert_image_to_pdf(): Converts image files into standard PDF documents.
"""

import os
import io
import uuid
from typing import Union
from PIL import Image, ImageDraw, ImageFont
import pypdf


def is_pdf(source: Union[str, bytes]) -> bool:
    """
    Checks if a file path or byte stream is a PDF document.
    """
    if isinstance(source, str):
        if source.lower().endswith(".pdf"):
            return True
        if os.path.exists(source):
            try:
                with open(source, "rb") as f:
                    header = f.read(5)
                    return header == b"%PDF-"
            except Exception:
                return False
        return False
    elif isinstance(source, bytes):
        return source.startswith(b"%PDF-")
    return False


def convert_image_to_pdf(image_path: str, output_pdf_path: str = None) -> str:
    """
    Converts a PNG/JPG image file into a standard PDF document.
    """
    if not output_pdf_path:
        base, _ = os.path.splitext(image_path)
        output_pdf_path = f"{base}.pdf"

    os.makedirs(os.path.dirname(output_pdf_path) or ".", exist_ok=True)

    with Image.open(image_path) as img:
        rgb_img = img.convert("RGB")
        rgb_img.save(output_pdf_path, "PDF", resolution=100.0)

    return output_pdf_path


def convert_pdf_to_image(
    pdf_source: Union[str, bytes],
    output_image_path: str = None,
    default_dir: str = "data/synthetic/uploads",
) -> str:
    """
    Extracts or renders Page 1 of a PDF document into a PNG image file.
    Returns the output PNG image path.
    """
    if not output_image_path:
        os.makedirs(default_dir, exist_ok=True)
        filename = f"pdf_render_{uuid.uuid4().hex[:8]}.png"
        output_image_path = os.path.join(default_dir, filename)
    else:
        os.makedirs(os.path.dirname(output_image_path) or ".", exist_ok=True)

    if isinstance(pdf_source, str):
        with open(pdf_source, "rb") as f:
            pdf_bytes = f.read()
    else:
        pdf_bytes = pdf_source

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    if len(reader.pages) == 0:
        raise ValueError("PDF document has 0 pages.")

    page = reader.pages[0]

    # Method 1: Extract embedded page image if present
    if len(page.images) > 0:
        try:
            img_data = page.images[0].data
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            img.save(output_image_path, "PNG")
            return output_image_path
        except Exception:
            pass

    # Method 2: Render page text onto canvas if no raw image
    text = page.extract_text() or "PDF Document Page 1"
    width, height = 800, 1000
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw simple header and text content
    draw.text((40, 40), "[ PDF RENDERED DOCUMENT ]", fill=(0, 0, 0))
    y_offset = 80
    for line in text.split("\n")[:30]:
        draw.text((40, y_offset), line[:80], fill=(50, 50, 50))
        y_offset += 25

    img.save(output_image_path, "PNG")
    return output_image_path
