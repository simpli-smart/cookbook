import os
import base64
import uuid
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image

load_dotenv()

API_URL = "https://http.kjae1q8i60.ss-in.s9t.link/predict"
API_TOKEN = os.getenv("SIMPLISMART_API_TOKEN")

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {API_TOKEN}"
}


def convert_image_to_base64(image_path):
    """
    Convert a local image file to base64 encoded string.
    
    Args:
        image_path (str): Path to the local image file
    
    Returns:
        str: Base64 encoded string of the image
    
    Raises:
        Exception: If image cannot be read or converted
    """
    try:
        # Open and read the image
        image = Image.open(image_path)
        buffered = BytesIO()
        
        # Determine the image format from file extension
        file_ext = Path(image_path).suffix.lower()
        format_type = "PNG" if file_ext == '.png' else "JPEG"
        
        # Save image to buffer and encode to base64
        image.save(buffered, format=format_type)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    
    except Exception as e:
        raise Exception(f"Error converting image to base64: {e}")

def save_base64_images(images_list, request_id, request_type):
    """
    Save base64 encoded images to local files.
    
    Args:
        images_list (list): List of base64 encoded image strings
        request_id (str): Unique request ID for file naming
        request_type (str): Type of request ('txt2img' or 'image_edit')
    
    Returns:
        list: List of saved file paths
    """
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    saved_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for idx, base64_str in enumerate(images_list):
        try:
            # Decode base64 string to image data
            image_data = base64.b64decode(base64_str)
            
            # Create a descriptive filename
            filename = f"{request_type}_{request_id}_{timestamp}_{idx}.png"
            filepath = output_dir / filename
            
            # Save the image to disk
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            saved_files.append(str(filepath))
            print(f"✓ Saved: {filepath}")
            
        except Exception as e:
            print(f"✗ Error saving image {idx}: {e}")
    
    return saved_files


def generate_image(
    prompt,
    request_id=None,
    num_images=1,
    steps=28,
    guidance_scale=1.0,
    height=1024,
    width=1024,
    seed=0,
    acceleration="fast"
):
    """
    Generate images from text prompts using Flux 2 Dev model.
    
    Args:
        prompt (str): Text description of the image to generate
        num_images (int): Number of images to generate
        steps (int): Number of inference steps (default: 28)
        guidance_scale (float): How closely to follow the prompt
        height (int): Image height in pixels (up to 2048)
        width (int): Image width in pixels (up to 2048)
        seed (int): Random seed for reproducibility (0 for random)
        acceleration (str): Speed mode - "fast", "slow" or "regular"
    
    Returns:
        tuple: (response_json, list_of_saved_file_paths)    
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    payload = {
        "request_id": request_id,
        "request_type": "txt2img",
        "prompt": prompt,
        "num_images_per_prompt": num_images,
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "height": height,
        "width": width,
        "seed": seed,
        "acceleration": acceleration,
        "safety_tolerance": 2
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Request successful!")
        print(f"  Inference time: {result.get('model_inference_time', 'N/A')}s")
        print(f"  Resolution: {result.get('mega_pixel', 'N/A')} MP")

        # Save generated images
        if 'images' in result and result['images']:
            saved_files = save_base64_images(result['images'], request_id, "txt2img")
            return result, saved_files
        else:
            print("✗ No images in response")
            return result, []        
    else:
        print(f"✗ Request failed: {response.status_code}")
        return None


json_prompt = """{
  "scene": "A three-quarter angle studio product shot of a premium sneaker, isolated on a neutral light-gray background",
  "subjects": [
    {
      "type": "Upper Mesh",
      "description": "Breathable engineered mesh forming the main body of the sneaker, strictly in color #F5F5F5 off-white",
      "position": "upper body",
      "color_match": "exact"
    },
    {
      "type": "Toe Cap Overlay",
      "description": "Reinforced protective overlay covering the toe area, strictly in color #1C1C1C matte black",
      "position": "front toe",
      "color_match": "exact"
    },
    {
      "type": "Midsole",
      "description": "Cushioned foam midsole with a smooth sculpted profile, strictly in color #FF6A00 bright orange",
      "position": "midsole",
      "color_match": "exact"
    },
    {
      "type": "Outsole",
      "description": "Durable rubber outsole with visible traction pattern, strictly in color #2E2E2E dark charcoal",
      "position": "sole bottom",
      "color_match": "exact"
    },
    {
      "type": "Brand Mark",
      "description": "SimpliSneaker brand wordmark printed near the heel counter, strictly in color #1C1C1C black",
      "position": "lateral heel",
      "detail_preservation": "high"
    },
    {
      "type": "Laces and Eyelets",
      "description": "Flat woven laces and reinforced eyelets, strictly in color #F5F5F5 off-white",
      "position": "upper center",
      "color_match": "exact"
    },
    {
      "type": "Background",
      "description": "A smooth, seamless studio background in light gray, evenly lit with no shadows",
      "position": "background",
      "color_match": "exact"
    }
  ],
  "color_palette": [
    "#F5F5F5",
    "#1C1C1C",
    "#FF6A00",
    "#2E2E2E"
  ]
}"""

result = generate_image(    
    prompt=json_prompt,
    num_images=1,
    steps=30,
    height=1024,
    width=1024,
    acceleration="slow",
    guidance_scale=3.5
)