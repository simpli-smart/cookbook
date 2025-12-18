# 🎨 FLUX.2 Dev API - Code Examples

A collection of practical Python examples demonstrating the capabilities of [Simplismart's FLUX.2 Dev API](https://simplismart.ai/playground). FLUX.2 is Black Forest Labs' latest image generation model featuring multi-reference input support (up to 10 images), improved typography, 4 megapixel output resolution, and exceptional character consistency.

**For detailed instructions, check out the companion blog**:  
[FLUX.2 API Guide: Advanced Image Generation with Simplismart](https://simplismart.ai/blog/flux-2-api-simplismart) 

## 🚀 Features

- **Text-to-Image Generation**: Create stunning images from text prompts
- **Multi-Reference Editing**: Edit images using up to 10 reference images for character consistency
- **Batch Processing**: Generate multiple variations efficiently
- **JSON Prompting**: Use structured JSON for precise control over colors and composition
- **High Resolution**: Generate images up to 2048x2048 (4 megapixels)
- **Fast Performance**: Configurable acceleration modes for speed/quality tradeoffs

## 🛠️ Prerequisites

- Python 3.8 or higher
- A Simplismart API Token (Get it from the [Playground](https://simplismart.ai/playground))

## 📦 Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/simpli-smart/cookbook.git
   cd cookbook/flux2-dev
   ```

2. **Create and activate a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Copy the template file:
   ```bash
   cp .env-template .env
   ```

   Open `.env` and add your Simplismart API token:
   ```env
   SIMPLISMART_API_TOKEN=your_api_token_here
   ```

   > **Note:** 
   <br/>You can get your API token from [Settings](https://app.simplismart.ai/settings) > API key > Generate New Key

## 🏃‍♂️ Usage Examples

### 1. Simple Text-to-Image Generation (`image-generate.py`)

Generate a single image from a text prompt with custom resolution and quality settings.

```bash
python image-generate.py
```

**What it does:**
- Generates a photorealistic sunset scene
- Uses 30 inference steps for high quality
- Outputs 1920x1080 resolution
- Uses "slow" acceleration mode for best results

**Key features demonstrated:**
- Basic text-to-image generation
- Custom resolution settings
- Quality/speed tradeoffs with acceleration modes
- Image saving to local `output/` directory

---

### 2. Batch Image Generation (`batch.py`)

Process multiple prompts efficiently to generate variations of the same scene.

```bash
python batch.py
```

**What it does:**
- Generates images for 3 different style variations (realistic, cyberpunk, anime)
- Creates 2 variations per prompt
- Uses fast acceleration for efficient batch processing
- Saves all generated images with descriptive filenames

**Key features demonstrated:**
- Batch processing multiple prompts
- Generating multiple variations per prompt
- Efficient use of fast acceleration mode
- Organized output with timestamps and IDs

---

### 3. Multi-Reference Image Editing (`edit-image.py`)

Edit and composite images using multiple reference images for character consistency.

```bash
python edit-image.py
```

**What it does:**
- Takes a character from one image (Elon Musk portrait)
- Places the character into a different environment (Golden Gate Bridge)
- Maintains facial features, proportions, and clothing details
- Renders in photorealistic style with natural lighting

**Key features demonstrated:**
- Multi-reference image editing (up to 10 images supported)
- Character consistency across different scenes
- Support for both local files and URLs
- Advanced composition and scene blending

**Use cases:**
- Character consistency for marketing campaigns
- Product placement in different environments
- Fashion catalog generation
- Virtual photography

---

### 4. JSON Prompting for Precision (`json-prompt.py`)

Use structured JSON prompts for precise control over colors, components, and composition.

```bash
python json-prompt.py
```

**What it does:**
- Defines a detailed sneaker design with exact hex colors
- Specifies individual components (mesh, toe cap, midsole, outsole, laces)
- Ensures precise color matching using hex codes
- Creates a professional product shot with clean background

**Key features demonstrated:**
- Structured JSON prompting
- Precise color control with hex codes
- Component-level design specification
- Professional product photography setup

**Use cases:**
- E-commerce product visualization
- Design mockups and prototypes
- Brand-compliant marketing materials
- UI/UX design system previews

---

## 📁 Output

All generated images are saved to the `output/` directory with the following naming convention:

```
{request_type}_{request_id}_{timestamp}_{index}.png
```

Example: `txt2img_a7f3c1e2_20241218_143052_0.png`

## 🎛️ API Parameters

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Text description or JSON prompt |
| `num_images_per_prompt` | int | 1 | Number of variations to generate |
| `num_inference_steps` | int | 28 | Quality/speed tradeoff (12-50) |
| `guidance_scale` | float | 1.0 | How closely to follow the prompt |
| `height` | int | 1024 | Image height (up to 2048) |
| `width` | int | 1024 | Image width (up to 2048) |
| `seed` | int | 0 | Random seed (0 for random) |
| `acceleration` | string | "fast" | "fast", "regular", or "slow" |

### Image Editing Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `images` | array | Array of base64 images or URLs (1-10 images) |
| `request_type` | string | Set to "image_edit" for editing mode |

## 🔗 Resources

- [Simplismart Playground](https://simplismart.ai/playground)
- [API Documentation](https://docs.simplismart.ai)
- [FLUX.2 on Hugging Face](https://huggingface.co/black-forest-labs/FLUX.2-dev)
- [Black Forest Labs Blog](https://bfl.ai/blog/flux-2)

## 💡 Tips & Best Practices

### Prompt Engineering
- Be specific and descriptive in your prompts
- Include style references (e.g., "photorealistic", "anime", "oil painting")
- Mention lighting, camera angles, and composition details
- Use JSON prompts for precise color and component control

### Performance Optimization
- Use `acceleration="fast"` for batch processing and prototyping
- Use `acceleration="slow"` for final high-quality outputs
- Reduce `num_inference_steps` for faster generation (minimum 12)
- Generate multiple variations with `num_images_per_prompt` instead of separate requests

### Image Editing
- Provide high-quality reference images for best results
- Use clear, detailed prompts describing the desired composition
- Experiment with `guidance_scale` (2.0-4.0) for stronger adherence to references
- Order images in the array by importance (first image = primary reference)


## 💬 Support

Have questions? [Contact us](https://www.simplismart.ai/contact) or check our [documentation](https://docs.simplismart.ai).

---

Made with ❤️ by [Simplismart](https://simplismart.ai)
