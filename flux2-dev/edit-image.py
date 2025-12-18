from PIL import Image
from io import BytesIO
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image
import os
import base64
import requests
from dotenv import load_dotenv

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

def edit_image(
    prompt,
    input_image,
    request_id=None,
    num_images=1,
    steps=28,
    guidance_scale=1.0,
    height=1024,
    width=1024,
    seed=-1,
    acceleration="fast",
    reference_images=None
):
    """
    Edit or modify images using multiple references.
    
    Supports both URLs and local file paths. Use reference_images
    to provide up to 9 additional reference images alongside the main input.
    
    Args:
        prompt (str): Text description of how to edit the image
        input_image (str): URL or local file path to the main input image
        reference_images (list): Additional reference images (URLs or paths)
        ... (other parameters same as generate_image)
    
    Returns:
        tuple: (response_json, list_of_saved_file_paths)
    """
    if request_id is None:
        request_id = str(uuid4())
    
    # Process main input image
    if input_image.startswith(('http://', 'https://')):
        processed_image = input_image
    else:
        processed_image = convert_image_to_base64(input_image)
    
    # Build images array
    images_array = [processed_image]
    
    # Add reference images (up to 9 more for total of 10)
    if reference_images:
        for ref_img in reference_images[:9]:  # Limit to 9 additional
            if ref_img.startswith(('http://', 'https://')):
                images_array.append(ref_img)
            else:
                images_array.append(convert_image_to_base64(ref_img))
    
    payload = {
        "request_id": request_id,
        "request_type": "image_edit",
        "prompt": prompt,
        "images": images_array,
        "num_images_per_prompt": num_images,
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "height": height,
        "width": width,
        "seed": seed,
        "acceleration": acceleration
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Image editing successful!")
        print(f"  Used {len(images_array)} reference image(s)")
        # Save edited images
        if 'images' in result and result['images']:
            saved_files = save_base64_images(result['images'], request_id, "image_edit")
            return result, saved_files
        else:
            print("✗ No images in response")
            return result, []
        
    else:
        print(f"✗ Request failed: {response.status_code}")
        return None

# Example: Character consistency across scenes
result = edit_image(    
    prompt="Use the character from Image 1 as the subject, preserving facial features, body proportions, and clothing details. Place this character into the environment from Image 2. Render the final image in a highly photo-realistic style with natural lighting, accurate shadows, realistic textures, and consistent perspective.",    
    input_image="samples/elon-musk.jpg",
    reference_images=["samples/golden-gate.jpg"],    
    num_images=1,
    steps=30,
    guidance_scale=3.5
)