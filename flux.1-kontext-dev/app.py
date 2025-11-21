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
    page_title="Flux.1 Kontext Dev Image Editor",
    page_icon="🎨",
    layout="wide"
)

# Add logo to header using custom CSS
logo_path = Path("assets/logo.png")
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
        
        /* Custom styling for cleaner look */
        .stTextArea label, .stFileUploader label {{
            font-size: 16px !important;
            font-weight: 500 !important;
        }}
        
        /* Image container with border */
        .image-container {{
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            margin: 10px 0;
        }}
        
        /* Hide help icons for cleaner look */
        .stTooltipIcon {{
            visibility: hidden;
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
st.title("🎨 Flux.1 Kontext Dev Image Editor")
st.markdown("")

# Create 3-column layout
col_left, col_middle, col_right = st.columns([1, 1, 1])

# Initialize session state for generated image
if 'generated_image_url' not in st.session_state:
    st.session_state.generated_image_url = None
if 'generation_metrics' not in st.session_state:
    st.session_state.generation_metrics = None

# LEFT COLUMN - Controls
with col_left:
    st.markdown("### 📸 Input Image")
    input_method = st.radio(
        "",
        ["📤 Upload", "📷 Webcam"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    image = None
    
    if input_method == "📤 Upload":
        uploaded_file = st.file_uploader(
            "Upload",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
    
    else:  # Webcam
        camera_photo = st.camera_input("Capture", label_visibility="collapsed")
        if camera_photo is not None:
            image = Image.open(camera_photo)
    
    # Prompt input
    st.markdown("### ✍️ Your Prompt")
    prompt = st.text_area(
        "Prompt",
        value="Change the background to the Golden Gate Bridge",
        height=80,
        label_visibility="collapsed",
        placeholder="Describe what you want to generate..."
    )
    
    # Advanced settings in expander
    with st.expander("⚙️ Settings"):
        guidance_scale = st.slider(
            "Guidance",
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
            "Speed",
            options=["🐢 Low", "🚀 High"],
            index=0,
            horizontal=True,
            help="Higher acceleration means faster generation, but with lower quality."
        )
        threshold = 0.9 if threshold_level == "🐢 Low" else 1.0
        
        size_option = st.selectbox(
            "Size",
            options=["512×512", "768×768", "1024×1024"],
            index=2
        )
        size_map = {"512×512": 512, "768×768": 768, "1024×1024": 1024}
        width = height = size_map[size_option]
    
    # Generate button
    generate_button = st.button("🚀 Generate", type="primary", use_container_width=True)
    
    # Handle generation
    if generate_button:
        if image is None:
            st.error("⚠️ Please provide an image first!")
        elif not prompt.strip():
            st.error("⚠️ Please enter a prompt!")
        else:
            try:
                with st.spinner("🎨 Generating..."):
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
                    
                    # Store results in session state
                    if result and 'images' in result and len(result['images']) > 0:
                        st.session_state.generated_image_url = result['images'][0]['url']
                        st.session_state.generation_metrics = {
                            "total_time": result.get('total_request_time', 0),
                            "inference_time": result.get('model_inference_time', 0),
                            "request_id": result.get('request_id', 'N/A')
                        }
                        st.success("✅ Generated!")
                        st.rerun()
                    else:
                        st.error("❌ Generation failed")
                        
            except RequestException as e:
                st.error(f"❌ API Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    
# MIDDLE COLUMN - Preview
with col_middle:
    st.markdown("### 📷 Preview")
    if image is not None:
        st.image(image, use_container_width=True)
    else:
        st.markdown(
            """
            <div style='
                border: 2px dashed #666;
                border-radius: 10px;
                padding: 80px 20px;
                text-align: center;
                background-color: rgba(255, 255, 255, 0.05);
                margin: 20px 0;
            '>
                <p style='font-size: 48px; margin: 0;'>📸</p>
                <p style='color: #888; font-size: 16px; margin-top: 10px;'>Upload an image</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# RIGHT COLUMN - Generated Image
with col_right:
    st.markdown("### 🎨 AI Edited Image")
    if st.session_state.generated_image_url:
        st.image(st.session_state.generated_image_url, use_container_width=True)
        # st.markdown(f"[🔗 Open in new tab]({st.session_state.generated_image_url})")
    else:
        st.markdown(
            """
            <div style='
                border: 2px dashed #666;
                border-radius: 10px;
                padding: 80px 20px;
                text-align: center;
                background-color: rgba(255, 255, 255, 0.05);
                margin: 20px 0;
            '>
                <p style='font-size: 48px; margin: 0;'>🖼️</p>
                <p style='color: #888; font-size: 16px; margin-top: 10px;'>Generated image</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    # Display metrics if available
    if st.session_state.generation_metrics:
        st.markdown("**⏱️ Metrics**")
        metrics = st.session_state.generation_metrics
        st.markdown(f"**Total Time:** {metrics['total_time']:.2f}s")
        st.markdown(f"**Inference Time:** {metrics['inference_time']:.2f}s")


# Footer
st.markdown("")
st.markdown("")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <small>Made with ❤️ by Simplismart</small>
    </div>
    """,
    unsafe_allow_html=True
)
