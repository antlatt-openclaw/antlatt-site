#!/usr/bin/env python3
"""
ComfyUI Workflow Runner

Run any exported ComfyUI workflow JSON file.

Usage:
    python run_workflow.py workflow.json
    python run_workflow.py workflow.json --output /path/to/output.png
    python run_workflow.py workflow.json --param prompt "a cat" --param seed 12345

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


def load_workflow(path):
    """Load workflow from JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def submit_and_wait(workflow, timeout=300):
    """Submit workflow and wait for completion."""
    resp = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow}, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    
    if "error" in result:
        raise RuntimeError(f"Workflow error: {result['error']}")
    
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("No prompt_id returned")
    
    print(f"Submitted: {prompt_id}")
    
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
        resp.raise_for_status()
        history = resp.json()
        
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            if outputs:
                return outputs
        
        time.sleep(1)
    
    raise TimeoutError(f"Workflow timed out after {timeout}s")


def download_all_images(outputs, output_dir):
    """Download all generated images from outputs."""
    saved = []
    for node_id, output in outputs.items():
        if "images" in output:
            for img in output["images"]:
                params = {"filename": img["filename"], "type": img.get("type", "output")}
                if img.get("subfolder"):
                    params["subfolder"] = img["subfolder"]
                
                resp = requests.get(f"{COMFYUI_URL}/view", params=params, timeout=60)
                resp.raise_for_status()
                
                path = Path(output_dir) / img["filename"]
                path.write_bytes(resp.content)
                saved.append(str(path))
                print(f"Saved: {path}")
    
    return saved


def find_and_set_param(workflow, param_name, param_value):
    """Find and set a parameter in the workflow by searching all nodes."""
    found = False
    
    for node_id, node in workflow.items():
        if not isinstance(node, dict) or "inputs" not in node:
            continue
        
        inputs = node["inputs"]
        
        # Handle common parameter names
        if param_name.lower() == "prompt" or param_name.lower() == "positive":
            if "text" in inputs and "CLIPTextEncode" in node.get("class_type", ""):
                # Check if this is the positive prompt (usually connected to positive input)
                inputs["text"] = param_value
                found = True
                print(f"Set {param_name} in node {node_id}")
        
        elif param_name.lower() == "negative":
            if "text" in inputs and "CLIPTextEncode" in node.get("class_type", ""):
                inputs["text"] = param_value
                found = True
                print(f"Set negative prompt in node {node_id}")
        
        elif param_name.lower() == "seed":
            if "seed" in inputs:
                inputs["seed"] = int(param_value)
                found = True
                print(f"Set seed={param_value} in node {node_id}")
        
        elif param_name.lower() == "steps":
            if "steps" in inputs:
                inputs["steps"] = int(param_value)
                found = True
                print(f"Set steps={param_value} in node {node_id}")
        
        elif param_name.lower() == "width":
            if "width" in inputs:
                inputs["width"] = int(param_value)
                found = True
                print(f"Set width={param_value} in node {node_id}")
        
        elif param_name.lower() == "height":
            if "height" in inputs:
                inputs["height"] = int(param_value)
                found = True
                print(f"Set height={param_value} in node {node_id}")
        
        elif param_name.lower() == "model":
            if "ckpt_name" in inputs:
                inputs["ckpt_name"] = param_value
                found = True
                print(f"Set model={param_value} in node {node_id}")
        
        elif param_name in inputs:
            inputs[param_name] = param_value
            found = True
            print(f"Set {param_name}={param_value} in node {node_id}")
    
    if not found and param_name not in ["prompt", "positive", "negative", "seed", "steps", "width", "height", "model"]:
        print(f"Warning: Parameter '{param_name}' not found in workflow")
    
    return workflow


def main():
    parser = argparse.ArgumentParser(description="Run a ComfyUI workflow")
    parser.add_argument("workflow", help="Path to workflow JSON file")
    parser.add_argument("--output", "-o", default=None, help="Output directory (default: same as workflow)")
    parser.add_argument("--param", "-p", nargs=2, action="append", default=[],
                        metavar=("NAME", "VALUE"), help="Set a parameter (can be used multiple times)")
    parser.add_argument("--random-seed", action="store_true", help="Set random seed")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    args = parser.parse_args()
    
    workflow_path = Path(args.workflow)
    if not workflow_path.exists():
        print(f"Error: Workflow not found: {workflow_path}")
        sys.exit(1)
    
    output_dir = args.output or str(workflow_path.parent)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load workflow
    workflow = load_workflow(workflow_path)
    print(f"Loaded workflow: {workflow_path.name}")
    
    # Apply parameters
    for name, value in args.param:
        workflow = find_and_set_param(workflow, name, value)
    
    if args.random_seed:
        seed = random.randint(0, 999999999)
        workflow = find_and_set_param(workflow, "seed", seed)
    
    # Run workflow
    print("Running workflow...")
    outputs = submit_and_wait(workflow, timeout=args.timeout)
    
    # Download results
    saved = download_all_images(outputs, output_dir)
    print(f"\nGenerated {len(saved)} image(s)")
    
    return saved


if __name__ == "__main__":
    main()