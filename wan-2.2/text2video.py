import requests
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def download_video(url: str, output_path: str = None) -> str:
    """Download video from URL to local file."""
    if output_path is None:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = int(time.time())
        output_path = output_dir / f"wan2_video_{timestamp}.mp4"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Downloading video...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print(f"✅ Video downloaded: {output_path}")
    return str(output_path)


def generate_video(prompt: str) -> str:
    """
    Generate a video using Wan2.2 Text-to-Video API and download it locally.
    
    Args:
        prompt: Text description of the video to generate
        
    Returns:
        Local file path to the downloaded video
    """
    # Get API token from environment
    api_token = os.getenv("SIMPLISMART_API_TOKEN")
    
    # API endpoint
    url = "https://YOUR-MODEL-ENDPOINT/subscribe"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Request payload
    payload = {
        "name": "YOUR-MODEL-ID",
        "input_data": {
            "prompt": prompt,
            "negative_prompt": "overexposed, low quality, worst quality",
            "num_frames": 81,
            "frames_per_second": 16,
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "num_inference_steps": 27,
            "enable_safety_checker": True,
            "enable_output_safety_checker": False,
            "enable_prompt_expansion": False,
            "acceleration": "regular",
            "guidance_scale": 3.5,
            "guidance_scale_2": 4.0,
            "shift": 5,
            "interpolator_model": "film",
            "num_interpolated_frames": 1,
            "adjust_fps_for_interpolation": True,
            "video_quality": "high",
            "video_write_mode": "balanced",
        }
    }
    
    # Make the request
    print("🎬 Generating video...")
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # Check if video generation was successful
    if result.get("status") == "SUCCESS" and result.get("result", {}).get("output_url"):
        video_url = result["result"]["output_url"]
        print(f"✅ Video generated successfully!")
        
        # Download the video
        video_path = download_video(video_url)
        return video_path
    elif result.get("status") == "PENDING":
        raise Exception(f"⏳ Video generation is pending. Request ID: {result.get('request_id')}")
    else:
        raise Exception(f"❌ Video generation failed: {result}")


# Example usage
if __name__ == "__main__":
    prompt = "Close-up shot, edge lighting, daylight, soft lighting, desaturated colors, center composition, daylight.In an eye-level shot, three figures compose the frame. In the center is a foreign boy in a red school uniform, around fifteen or sixteen years old, with slightly curly blond hair, defined features, and a focused expression. He first looks to the left, then quickly turns his head to look right, before looking back to the left, his lips moving as if in conversation. His movements are natural and fluid, and his gaze shifts with the turn of his head. On the right is the blurred face of a foreign woman, with only half her face visible. She is around her thirties, and her expression is indistinct. The background is a classroom setting, with the wall covered in black-and-white framed photos. The figures of several students in red uniforms are faintly visible. In the foreground, a blurry figure quickly passes in front of the frame, creating a sense of motion. The lighting is soft and even, and the overall color tone is neutral, emphasizing the depth and detail of the shot.",
    video_path = generate_video(prompt)
    print(f"\n🎥 Video saved to: {video_path}")
