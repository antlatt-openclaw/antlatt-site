#!/usr/bin/env python3
"""
ComfyUI Image Generator

Generates images using ComfyUI via API. Supports SDXL and SD1.5 models.

Usage:
    python generate_image.py --prompt "a cat" --model sdxl/epicrealismXL
    python generate_image.py --prompt "a cat" --negative "blurry" --width 1024 --height 1024
    python generate_image.py --prompt "a cat" --output /path/to/output.png

Environment:
    COMFYUI_URL - ComfyUI server URL (default: http://192.168.1.142:8188)
"""

import argparse
import json
import os
import random
import sys
import time
import requests
from pathlib import Path

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.1.142:8188")

# Default models
DEFAULT_SDXL = "sdxl/epicrealismXL_vxviLastfameRealism.safetensors"
DEFAULT_SD15 = "v1-5-pruned-emaonly.safetensors"

# Default negative prompt for photorealistic images
DEFAULT_NEGATIVE = "cartoon, anime, illustration, painting, drawing, low quality, blurry, watermark, text"


def get_available_models():
    """Fetch list of available checkpoint models."""
    resp = requests.get(f"{COMFYUI_URL}/object_info", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "CheckpointLoaderSimple" in data:
        return data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    return []


def create_workflow(prompt, negative, model, width, height, steps, cfg, seed):
    """Create a basic text-to-image workflow."""
    if seed is None:
        seed = random.randint(0, 999999999)
    
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": model
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["4", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative,
                "clip": ["4", 1]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "comfyui",
                "images": ["8", 0]
            }
        }
    }
    return workflow, seed


def submit_and_wait(workflow, timeout=180):
    """Submit workflow and wait for completion."""
    # Submit
    resp = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow}, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    
    if "error" in result:
        raise RuntimeError(f"Workflow error: {result['error']}")
    
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("No prompt_id returned")
    
    # Poll for completion
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
        resp.raise_for_status()
        history = resp.json()
        
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            if outputs:
                # Find the saved image
                for node_id, output in outputs.items():
                    if "images" in output:
                        return output["images"]
        
        time.sleep(1)
    
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_image(filename, subfolder, img_type, output_path):
    """Download generated image from ComfyUI."""
    params = {"filename": filename, "type": img_type}
    if subfolder:
        params["subfolder"] = subfolder
    
    resp = requests.get(f"{COMFYUI_URL}/view", params=params, timeout=30)
    resp.raise_for_status()
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(resp.content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate images with ComfyUI")
    parser.add_argument("--prompt", help="Positive prompt (required unless --list-models)")
    parser.add_argument("--negative", default=DEFAULT_NEGATIVE, help="Negative prompt")
    parser.add_argument("--model", default=DEFAULT_SDXL, help="Model checkpoint name")
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=1024, help="Image height")
    parser.add_argument("--steps", type=int, default=25, help="Sampling steps")
    parser.add_argument("--cfg", type=float, default=7.5, help="CFG scale")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--output", "-o", default=None, help="Output path (default: temp file)")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    args = parser.parse_args()
    
    if args.list_models:
        print("Available models:")
        for model in get_available_models():
            print(f"  {model}")
        return
    
    # Create workflow
    workflow, seed = create_workflow(
        prompt=args.prompt,
        negative=args.negative,
        model=args.model,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg=args.cfg,
        seed=args.seed
    )
    
    print(f"Generating image...")
    print(f"  Model: {args.model}")
    print(f"  Size: {args.width}x{args.height}")
    print(f"  Seed: {seed}")
    
    # Submit and wait
    images = submit_and_wait(workflow)
    
    # Download first image
    img = images[0]
    output_path = args.output or f"/tmp/comfyui_{seed}.png"
    path = download_image(
        filename=img["filename"],
        subfolder=img.get("subfolder", ""),
        img_type=img.get("type", "output"),
        output_path=output_path
    )
    
    print(f"Saved: {path}")
    return str(path)


if __name__ == "__main__":
    main()