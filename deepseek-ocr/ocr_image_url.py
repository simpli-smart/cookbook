import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("SIMPLISMART_API_KEY")
BASE_URL = os.getenv("SIMPLISMART_BASE_URL")
DEFAULT_HEADERS_ID = os.getenv("DEFAULT_HEADERS_ID")

def ocr_image_url(image_url: str) -> str:
    """
    Extract text from an image URL using DeepSeek OCR.
    
    Args:
        image_url: Public URL of the image
        
    Returns:
        Extracted text from the image
    """
    # Initialize the Simplismart client
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        default_headers={"id": DEFAULT_HEADERS_ID}
    )
    
    messages = [
        {
            "role": "system",
            "content": "You are an expert OCR assistant. Extract all text from images accurately."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract all text from this image."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    ]
    
    response = client.chat.completions.create(
        model="deepseek-ocr",
        messages=messages,
        max_tokens=2048,
        temperature=0
    )
    
    return response.choices[0].message.content

# Usage example
if __name__ == "__main__":
    # Process an online document
    url = "https://simplismart-public-assets.s3.ap-south-1.amazonaws.com/logos/ocr.png"
    extracted_text = ocr_image_url(url)
    print(extracted_text)