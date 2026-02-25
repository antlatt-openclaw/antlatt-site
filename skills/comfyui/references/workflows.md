# ComfyUI Workflows

Common workflow templates for image and video generation.

## Basic Text-to-Image

Standard SDXL text-to-image workflow. Used by `scripts/generate_image.py`.

```json
{
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": <seed>,
      "steps": 25,
      "cfg": 7.5,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    }
  },
  "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "<model>"}},
  "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
  "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "<positive_prompt>", "clip": ["4", 1]}},
  "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "<negative_prompt>", "clip": ["4", 1]}},
  "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
  "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "output", "images": ["8", 0]}}
}
```

## Image-to-Image (Img2Img)

Modify existing images with a prompt.

```json
{
  "1": {"class_type": "LoadImage", "inputs": {"image": "<input_image.png>"}},
  "2": {"class_type": "VAEEncode", "inputs": {"pixels": ["1", 0], "vae": ["4", 2]}},
  "3": {"class_type": "KSampler", "inputs": {
    "seed": <seed>,
    "steps": 25,
    "cfg": 7.5,
    "sampler_name": "euler",
    "scheduler": "normal",
    "denoise": 0.75,
    "model": ["4", 0],
    "positive": ["6", 0],
    "negative": ["7", 0],
    "latent_image": ["2", 0]
  }},
  "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "<model>"}},
  "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "<prompt>", "clip": ["4", 1]}},
  "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "<negative>", "clip": ["4", 1]}},
  "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
  "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "img2img", "images": ["8", 0]}}
}
```

Key difference: use `VAEEncode` on input image, and `denoise` < 1.0 to retain structure.

## Upscaling (Hi-Res Fix)

Generate at high resolution with detail preservation.

```json
{
  "10": {"class_type": "UpscaleLatent", "inputs": {
    "samples": ["3", 0],
    "upscale_method": "nearest-exact",
    "width": 2048,
    "height": 2048,
    "crop": "disabled"
  }},
  "11": {"class_type": "KSampler", "inputs": {
    "seed": <seed>,
    "steps": 15,
    "cfg": 7.5,
    "sampler_name": "euler",
    "scheduler": "normal",
    "denoise": 0.5,
    "model": ["4", 0],
    "positive": ["6", 0],
    "negative": ["7", 0],
    "latent_image": ["10", 0]
  }}
}
```

Add these nodes after the initial KSampler for 2x upscaling.

## ControlNet (Pose/Depth Guidance)

Use reference images to guide generation structure.

```json
{
  "20": {"class_type": "LoadImage", "inputs": {"image": "<reference.png>"}},
  "21": {"class_type": "ControlNetApply", "inputs": {
    "conditioning": ["6", 0],
    "control_net": ["22", 0],
    "image": ["20", 0],
    "strength": 1.0
  }},
  "22": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "control_v11p_sd15_openpose.pth"}}
}
```

Replace positive conditioning input in KSampler with ControlNet output.

## LoRA Support

Apply LoRA adapters for style/character modifications.

```json
{
  "30": {"class_type": "LoraLoader", "inputs": {
    "model": ["4", 0],
    "clip": ["4", 1],
    "lora_name": "<lora_file.safetensors>",
    "strength_model": 1.0,
    "strength_clip": 1.0
  }}
}
```

Connect model and clip outputs from LoraLoader to subsequent nodes instead of from CheckpointLoader.

## AnimateDiff (Video)

Generate short video clips from text.

```json
{
  "40": {"class_type": "AnimateDiffUnload", "inputs": {}},
  "41": {"class_type": "AnimateDiffLoaderWithContext", "inputs": {
    "model": ["4", 0],
    "latents": ["5", 0],
    "context_length": 16,
    "context_overlap": 4,
    "model_name": "mm_sd_v15_v2.ckpt"
  }},
  "42": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 16}}
}
```

Replace EmptyLatentImage with batch_size = frame count. The context settings control motion coherence.

## Common Node References

| Node | Purpose |
|------|---------|
| CheckpointLoaderSimple | Load model/CLIP/VAE from checkpoint |
| CLIPTextEncode | Encode positive/negative prompts |
| EmptyLatentImage | Create empty latent (txt2img) |
| VAEEncode | Encode image to latent (img2img) |
| VAEDecode | Decode latent to image |
| KSampler | Main sampling/denoising loop |
| SaveImage | Save output to file |
| LoadImage | Load input image |
| LoraLoader | Apply LoRA weights |
| ControlNetApply | Apply ControlNet conditioning |

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| POST /prompt | Submit workflow |
| GET /history/{id} | Check job status |
| GET /view | Download image |
| GET /object_info | List available nodes/models |
| GET /system_stats | System info |