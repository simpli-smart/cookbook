import streamlit as st
import requests
import base64
import time
from pathlib import Path
from requests.exceptions import RequestException
from PIL import Image
import io
import os
from dotenv import load_dotenv


load_dotenv()

SIMPLISMART_BASE_URL = os.getenv("SIMPLISMART_BASE_URL")
SIMPLISMART_API_KEY = os.getenv("SIMPLISMART_API_KEY")


# Set page config
st.set_page_config(
    page_title="Flux Kontext Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Add logo to header using custom CSS
logo_path = Path("logo.png")
if logo_path.exists():
    logo_base64 = base64.b64encode(logo_path.read_bytes()).decode()
    st.markdown(
        f"""
        <style>
        /* Glass effect on header bar */
        [data-testid="stHeader"] {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 999 !important;
        }}
        
        /* Logo container stays on top of glass header */
        .logo-container {{
            position: fixed !important;
            top: 5px;
            left: 20px;
            width: 180px;
            height: 60px;
            z-index: 999999 !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .logo-container img {{
            position: relative;
            z-index: 999999 !important;
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        </style>
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" style="width: 100%; height: 100%; object-fit: contain;">
        </div>
        """,
        unsafe_allow_html=True
    )

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def make_request(payload, retries=3, delay=2):
    """Make API request with retry logic"""
    headers = {
        'Authorization': f'Bearer {SIMPLISMART_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(SIMPLISMART_BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay ** attempt)
            else:
                raise e

# App Title
st.title("🎨 Flux.1 Kontext Image Generator")
st.markdown("Generate creative images by combining a reference image with your prompt")

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    # st.header("Input")
    
    # Image input method selection
    input_method = st.radio(
        "Choose image input method:",
        ["Upload Image", "Capture from Webcam"],
        horizontal=True
    )
    
    image = None
    
    if input_method == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png"],
            help="Upload a reference image to use in generation"
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
    
    else:  # Webcam
        camera_photo = st.camera_input("Take a picture")
        if camera_photo is not None:
            image = Image.open(camera_photo)
            st.image(image, caption="Captured Image", use_container_width=True)
    
    # Prompt input
    prompt = st.text_area(
        "Enter your prompt:",
        value="Change the background to the Golden Gate bridge",
        height=100,
        help="Describe what you want to generate with the reference image"
    )
    
    # Advanced settings in expander
    with st.expander("⚙️ Advanced Settings"):
        guidance_scale = st.slider(
            "Guidance Scale",
            min_value=1.0,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help="Higher values make the output more closely follow the prompt"
        )
        
        num_inference_steps = st.slider(
            "Inference Steps",
            min_value=10,
            max_value=50,
            value=28,
            step=1,
            help="More steps generally produce higher quality but take longer"
        )
        
        threshold_level = st.radio(
            "Acceleration Level",
            options=["Low", "High"],
            index=0,
            horizontal=True,
            help="Higher acceleration means faster generation, but with lower quality."

        )
        # Map threshold level to actual value
        threshold = 0.9 if threshold_level == "Low" else 1.0
        
        col_w, col_h = st.columns(2)
        with col_w:
            width = st.selectbox(
                "Width",
                options=[512, 768, 1024],
                index=2
            )
        with col_h:
            height = st.selectbox(
                "Height",
                options=[512, 768, 1024],
                index=2
            )
    
    # Generate button
    generate_button = st.button("🚀 Generate Image", type="primary", use_container_width=True)

with col2:
    # st.header("Output")
    
    if generate_button:
        if image is None:
            st.error("⚠️ Please provide an image first!")
        elif not prompt.strip():
            st.error("⚠️ Please enter a prompt!")
        else:
            try:
                with st.spinner("🎨 Generating your image... This may take a few seconds."):
                    # Convert image to base64
                    image_base64 = image_to_base64(image)
                    
                    # Prepare payload
                    payload = {
                        "image": image_base64,
                        "prompt": prompt,
                        "guidance_scale": guidance_scale,
                        "num_inference_steps": num_inference_steps,
                        "num_images_per_prompt": 1,
                        "height": height,
                        "width": width,
                        "threshold": threshold
                    }
                    
                    # Make API request
                    result = make_request(payload)
                    
                    # Display results
                    if result and 'images' in result and len(result['images']) > 0:
                        st.success("✅ Image generated successfully!")
                        
                        # Display the generated image
                        output_url = result['images'][0]['url']
                        st.image(output_url, caption="Generated Image", use_container_width=True)
                        
                        # Display metadata
                        with st.expander("📊 Generation Details"):
                            st.json({
                                "request_id": result.get('request_id', 'N/A'),
                                "total_time": f"{result.get('total_request_time', 0):.2f}s",
                                "inference_time": f"{result.get('model_inference_time', 0):.2f}s",
                                "image_url": output_url
                            })
                        
                        # # Download button
                        # st.markdown("### Download")
                        # st.markdown(f"[🔗 Open in new tab]({output_url})")
                    else:
                        st.error("❌ Failed to generate image. No output received.")
                        
            except RequestException as e:
                st.error(f"❌ API Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        # st.info("👈 Configure your settings and click 'Generate Image' to start")
        # Placeholder for output
        st.markdown(
            """
            <div style='
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 100px 20px;
                text-align: center;
                background-color: #000000;
                margin: 20px 0;
            '>
                <p style='font-size: 48px; margin: 0;'>🖼️</p>
                <p style='color: #666; font-size: 18px; margin-top: 10px;'>Your Generated Image Will Appear Here</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Powered by Flux Kontext | Made with ❤️ by Simplismart</p>
    </div>
    """,
    unsafe_allow_html=True
)
