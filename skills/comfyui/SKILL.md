---
name: comfyui
description: Generate images and videos using ComfyUI API at 192.168.1.142:8188. Use when the user requests image generation, video generation, AI art, or visual content creation. Supports SDXL/SD1.5 models, img2img, upscaling, ControlNet, LoRA, and AnimateDiff for video.
---

# ComfyUI Image & Video Generation

Generate images and videos via ComfyUI API running on RTX 5060 Ti (16GB VRAM).

## Quick Start

Use the script for basic text-to-image:

```bash
python3 scripts/generate_image.py --prompt "a photorealistic cat" --output /tmp/cat.png
```

For complex workflows, see [references/workflows.md](references/workflows.md).

## Available Models

List all models:
```bash
python3 scripts/generate_image.py --list-models
```

**Photorealistic SDXL:**
- `sdxl/epicrealismXL_vxviLastfameRealism.safetensors` (default)
- `sdxl/ponyRealism_V22.safetensors`
- `sdxl/spicyRealismNSFWMix_v30.safetensors`

**Anime/Stylized:**
- `sdxl/animergePonyXL_v60.safetensors`
- `sdxl/lucentxlPonyByKlaabu_b20.safetensors`

**Flux:**
- `flux/c4pacitor_dV2.safetensors`

## Common Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--width` | 1024 | Image width |
| `--height` | 1024 | Image height |
| `--steps` | 25 | Sampling steps (more = detail) |
| `--cfg` | 7.5 | Guidance scale |
| `--seed` | random | Reproducibility seed |
| `--negative` | (built-in) | Negative prompt |

## Prompt Tips

For photorealistic results, include:
- `photorealistic`, `professional photography`
- `studio lighting`, `natural lighting`
- `highly detailed`, `sharp focus`
- `8k resolution`, `shallow depth of field`

Negative prompt is built-in but can be overridden with `--negative`.

## Advanced Workflows

See [references/workflows.md](references/workflows.md) for:
- Image-to-Image (modify existing images)
- Upscaling (hi-res fix)
- ControlNet (pose/depth guidance)
- LoRA support (style/character)
- AnimateDiff (video generation)

## Custom Workflows

Export workflows from ComfyUI UI and save to:
```
/root/.openclaw/antlatt-workspace/comfyui-workflows/
```

Run any exported workflow:
```bash
# Basic run
python3 scripts/run_workflow.py /path/to/workflow.json

# With parameters
python3 scripts/run_workflow.py workflow.json \
  --param prompt "a cat" \
  --param seed 12345 \
  --param steps 30

# Random seed each time
python3 scripts/run_workflow.py workflow.json --random-seed
```

**Supported parameters:**
- `prompt` / `positive` - Main prompt text
- `negative` - Negative prompt
- `seed` - Random seed
- `steps` - Sampling steps
- `width` / `height` - Image dimensions
- `model` - Checkpoint name
- Any other parameter name in the workflow

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /prompt` | Submit workflow |
| `GET /history/{id}` | Check job status |
| `GET /view` | Download generated image |
| `GET /object_info` | List nodes/models |

## Environment

- `COMFYUI_URL` - Server URL (default: `http://192.168.1.142:8188`)
- Output directory: `/deadpool/StableDiffusion/newest/` (on server)

## Examples

**Photorealistic cat:**
```bash
python3 scripts/generate_image.py --prompt "photorealistic cat, studio lighting, 8k"
```

**Anime style:**
```bash
python3 scripts/generate_image.py --prompt "anime girl, vibrant colors" --model sdxl/animergePonyXL_v60.safetensors
```

**Landscape orientation:**
```bash
python3 scripts/generate_image.py --prompt "mountain landscape" --width 1536 --height 768
```

**Reproducible seed:**
```bash
python3 scripts/generate_image.py --prompt "cyberpunk city" --seed 12345
```