"""
Flux 2 Klein API examples for Simplismart shared endpoint.

Usage:
  pip install requests python-dotenv
  Set SIMPLISMART_API_TOKEN in .env, then:
  python flux2_klein_api_example.py

See blog-post.md for full guide.
"""

import os
import base64
import json
import uuid
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Replace with your Simplismart Flux 2 Klein endpoint URL and endpoint name
API_URL = os.getenv("FLUX2_KLEIN_API_URL", "https://nbvvf0hdo9-proxy.ss-in.s9t.link/subscribe")
ENDPOINT_NAME = os.getenv("FLUX2_KLEIN_ENDPOINT_NAME", "flux-2-klein-9b-d6d713d6-497a-4341-8d3c-8cf0e1db5733")
API_TOKEN = os.getenv("SIMPLISMART_API_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}",
}


def generate_image(
    prompt,
    request_id=None,
    num_images=1,
    width=1024,
    height=1024,
    num_steps=28,
    guidance=3.5,
    seed=42,
    negative_prompt=None,
):
    """
    Generate images from text using the Flux 2 Klein API.

    Args:
        prompt (str): Text description of the image to generate.
        request_id: Optional request identifier (default: auto-generated).
        num_images (int): Number of images to generate per request.
        width, height (int): Output resolution (e.g. 1024).
        num_steps (int): Inference steps (default 28).
        guidance (float): Guidance scale for prompt adherence.
        seed (int): Random seed for reproducibility.
        negative_prompt (str): Optional negative prompt.

    Returns:
        dict: API response containing base64 images and metadata.
    """
    if request_id is None:
        request_id = uuid.uuid4().hex

    payload = {
        "name": ENDPOINT_NAME,
        "input_data": {
            "request_id": request_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt or "blurry, low quality",
            "width": width,
            "height": height,
            "num_steps": num_steps,
            "guidance": guidance,
            "seed": seed,
            "num_images_per_prompt": num_images,
            "input_images": [],
            "output_type": "base64",
        },
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        result = response.json()
        print("✓ Request successful!")
        return result
    else:
        print(f"✗ Request failed: {response.status_code}")
        return None


def edit_image(
    prompt,
    input_images,
    request_id=None,
    num_images=1,
    width=1024,
    height=1024,
    num_steps=4,
    guidance=3.5,
    seed=42,
    negative_prompt=None,
):
    """
    Edit or generate from one or more reference images using the Flux 2 Klein API.

    Args:
        prompt (str): Instruction describing how to use the reference image(s).
        input_images (list): URLs or base64 strings of reference images.
        request_id: Optional request identifier.
        num_images (int): Number of output images per request.
        width, height (int): Output resolution.
        num_steps (int): Inference steps (default 4).
        guidance (float): Guidance scale.
        seed (int): Random seed.
        negative_prompt (str): Optional negative prompt.

    Returns:
        dict: API response with base64 images and metadata.
    """
    if request_id is None:
        request_id = uuid.uuid4().hex

    payload = {
        "name": ENDPOINT_NAME,
        "input_data": {
            "request_id": request_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt or "blurry, low quality",
            "width": width,
            "height": height,
            "num_steps": num_steps,
            "guidance": guidance,
            "seed": seed,
            "num_images_per_prompt": num_images,
            "input_images": input_images,
            "output_type": "base64",
        },
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        result = response.json()
        print("✓ Image editing successful!")
        print(f"  Used {len(input_images)} reference image(s)")
        return result
    else:
        print(f"✗ Request failed: {response.status_code}")
        return None


def load_local_image_as_base64(path):
    """Read a local image file and return its base64 string for API input."""
    p = Path(path)
    if not p.exists():
        return None
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def save_base64_images(images, prefix="flux2_klein", out_dir="output"):
    """Decode base64 image strings and save as PNG files with timestamp postfix."""
    from datetime import datetime
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    saved = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for i, img_b64 in enumerate(images):
        path = Path(out_dir) / f"{prefix}_{i}_{timestamp}.png"
        with open(path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        saved.append(str(path))
        print(f"  Saved: {path}")
    return saved


def _get_images_from_response(result):
    """Extract image list from API response (handles different response shapes)."""
    if not result:
        return []
    # Simplismart wrapper: images live under result.result.images
    if "result" in result and isinstance(result["result"], dict) and "images" in result["result"]:
        return result["result"]["images"]
    if "output" in result and isinstance(result["output"], dict) and "images" in result["output"]:
        return result["output"]["images"]
    return result.get("images", [])


if __name__ == "__main__":
    if not API_TOKEN:
        print("Set SIMPLISMART_API_TOKEN in .env")
        exit(1)

    # Example 1: Text-to-image
    print("\n--- Text-to-image ---")
    result = generate_image(
        prompt="A narrow neon-lit street in Tokyo at night, rain-slicked asphalt reflecting vibrant blue and pink neon signs. A prominent blue neon sign spelling 'Simplismart' glows above a small storefront, casting reflections on the wet pavement. Cyberpunk atmosphere, cinematic composition, moody lighting, photorealistic, highly detailed, 8k quality, atmospheric fog, Japanese cityscape aesthetic",
        width=1024,
        height=1024,
        num_steps=28,
        guidance=4.0,
        seed=60,
        negative_prompt="blurry, low quality",
    )
    images = _get_images_from_response(result)
    txt2img_paths = save_base64_images(images, prefix="flux2_klein_txt2img") if images else []

    # Example 2: Image editing using the generated image from step 1 (local file)
    print("\n--- Image edit (style transfer) ---")
    edit_paths = []
    edit_input = []
    if txt2img_paths:
        b64 = load_local_image_as_base64(txt2img_paths[0])
        if b64:
            edit_input = [b64]
            print(f"  Using local image: {txt2img_paths[0]}")
    if not edit_input:
        print("  No local image from step 1; skipping edit example.")
    else:
        result = edit_image(
            prompt="Transform into a 90s manga panel: bold black ink outlines, speed lines radiating from the neon sign, dramatic halftone dot shading, high contrast screentone textures, dynamic diagonal composition, limited color palette with selective coloring on the blue neon sign, action lines suggesting energy, exaggerated perspective, vintage print aesthetic with slight misregistration, expressive sound effect typography integrated into the scene (SFX: 'ZZZT' 'BUZZ'), cyberpunk manga style inspired by Akira and Ghost in the Shell",
            input_images=edit_input,
            width=1024,
            height=1024,
            num_steps=4,
            guidance=3.5,
            seed=28,
            negative_prompt="blurry, low quality",
        )
        images = _get_images_from_response(result)
        edit_paths = save_base64_images(images, prefix="flux2_klein_edit") if images else []

    # Summary: both outputs stored locally
    if txt2img_paths or edit_paths:
        print("\n--- Outputs saved locally ---")
        for p in txt2img_paths:
            print(f"  Text-to-image: {p}")
        for p in edit_paths:
            print(f"  Image edit:    {p}")
