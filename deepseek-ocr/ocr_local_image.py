import base64
from pathlib import Path
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("SIMPLISMART_API_KEY")
BASE_URL = os.getenv("SIMPLISMART_BASE_URL")
DEFAULT_HEADERS_ID = os.getenv("DEFAULT_HEADERS_ID")

def ocr_local_image(image_path: str) -> str:
    """
    Extract text from a local image file using DeepSeek OCR.
    
    Args:
        image_path: Path to the image file (jpg, png, etc.)
        
    Returns:
        Extracted text from the image
    """
    # Read and encode the image
    image_base64 = base64.b64encode(Path(image_path).read_bytes()).decode()
    
    # Initialize the Simplismart client
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        default_headers={"id": DEFAULT_HEADERS_ID}
    )

    
    # Prepare messages with system prompt and image
    messages = [
        {
            "role": "system",
            "content": "You are an expert OCR assistant. Extract all text from images accurately, maintaining the original structure and formatting."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": "Please extract all text from this image, preserving the layout and structure."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }
    ]
    
    # Make the API call
    response = client.chat.completions.create(
        model="deepseek-ocr",
        messages=messages,
        max_tokens=2048,
        temperature=0
    )
    
    return response.choices[0].message.content

# Usage example
if __name__ == "__main__":
    # Process a receipt
    receipt_text = ocr_local_image("samples/receipt.jpg")
    print("Extracted Text:")
    print(receipt_text)
    