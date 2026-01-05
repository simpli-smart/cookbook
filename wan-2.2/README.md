# WAN 2.2 Text-to-Video Generation

Generate high-quality videos from text prompts using Alibaba's WAN 2.2 model (27B parameters, MoE architecture). This cookbook demonstrates how to deploy WAN 2.2 on [Simplismart](https://simplismart.ai) with **3.2x faster inference** compared to standard implementations.

## Quick Start

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set up your API token:**

Create a `.env` file:
```bash
SIMPLISMART_API_TOKEN=your_token_here
```

3. **Generate your first video:**

```python
python text2video.py
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `prompt` | Required | Text description of your video |
| `num_frames` | 81 | Video length (81 frames = 5s at 16fps, up to 113 supported) |
| `resolution` | "720p" | Output quality: "480p", "720p" |
| `aspect_ratio` | "16:9" | Format: "16:9" (widescreen), "9:16" (vertical), "1:1" (square) |
| `num_inference_steps` | 27 | Quality vs speed (27-40, higher = better quality) |
| `guidance_scale` | 3.5 | Prompt adherence (3.5-4.0, higher = stricter) |
| `frames_per_second` | 16 | Playback speed (16 or 24 fps) |

## Writing Effective Prompts

**Tips:**
- Include camera angles (close-up, wide shot, tracking shot)
- Specify lighting (golden hour, dramatic, soft)
- Add motion details (slow pan, fast zoom, static)
- Use cinematic terms (depth of field, bokeh, volumetric lighting)

## Performance

Simplismart's optimized WAN 2.2 deployment delivers:

- **Inference time**: 49s (3.2x faster than baseline 159s)
- **Resolution**: Up to 720p at 16-24 fps
- **Frame support**: 81 frames (baseline) to 113 frames (extended)
- **Multi-GPU**: Efficient scaling across 2-8 GPUs

## Additional Resources

- **Blog Post**: [Full technical breakdown](https://simplismart.ai/blog/deploy-wan-2-2)
- **Get Access**: [Contact Simplismart](https://simplismart.ai/contact-us) to deploy WAN 2.2

## Model Information

- **Architecture**: Mixture-of-Experts (27B parameters, 14B active per step)
- **License**: Apache 2.0
- **Modalities**: Text-to-Video (T2V) and Image-to-Video (I2V)
- **Output**: 720p resolution, 16-24 fps, up to 113 frames
