import os
import fitz
import io
from tqdm import tqdm
from PIL import Image
from openai import OpenAI
import base64
from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("SIMPLISMART_API_KEY")
BASE_URL = os.getenv("SIMPLISMART_BASE_URL")
DEFAULT_HEADERS_ID = os.getenv("DEFAULT_HEADERS_ID")

# Your config
INPUT_PATH = "samples/deepseek-ocr-paper.pdf"
OUTPUT_PATH = "output"
PROMPT = "Convert the document to markdown."
NUM_WORKERS = 4
DPI = 144

os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(f"{OUTPUT_PATH}/images", exist_ok=True)


def pdf_to_images_high_quality(pdf_path, dpi=DPI):
    images = []
    pdf_document = fitz.open(pdf_path)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        img = Image.open(io.BytesIO(pixmap.tobytes("png")))
        images.append(img)
    pdf_document.close()
    return images


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def ocr_page(image, page_index):
    img_b64 = image_to_base64(image)
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        default_headers={"id": DEFAULT_HEADERS_ID}
    )

    response = client.chat.completions.create(
        model="deepseek-ocr",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]}
        ],
        temperature=0.0,
        max_tokens=2048,
    )

    text = response.choices[0].message.content
    print(text)

    if text:
      with open(f"{OUTPUT_PATH}/page_{page_index}.txt", "w", encoding="utf-8") as f:
          f.write(text)
    else:
        print(f"No text found for page {page_index}")
    return text if text else ""


def main():
    print("Loading PDF...")
    images = pdf_to_images_high_quality(INPUT_PATH)

    print("Running OCR via OpenAI API...")
    results = []
    for idx, img in tqdm(list(enumerate(images)), total=len(images)):
        results.append(ocr_page(img, idx))

    combined = "\n\n<--- Page Split --->\n\n".join(results)
    with open(f"{OUTPUT_PATH}/combined_ocr.txt", "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"OCR completed. Output saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
