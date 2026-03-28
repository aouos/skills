#!/usr/bin/env python3
"""
Gemini Image Generation Script
Calls the Gemini API (via AI Studio key) to generate images,
saves them along with a prompt.md to a timestamped folder.
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime

VALID_MODELS = [
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
]

# Flash supports all ratios and sizes; Pro has a smaller set
MODEL_ASPECT_RATIOS = {
    "gemini-3.1-flash-image-preview": [
        "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
        "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
    ],
    "gemini-3-pro-image-preview": [
        "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9",
    ],
}

MODEL_IMAGE_SIZES = {
    "gemini-3.1-flash-image-preview": ["512", "1K", "2K", "4K"],
    "gemini-3-pro-image-preview": ["1K", "2K", "4K"],
}


def sanitize_for_folder(text, max_len=50):
    """Create a filesystem-safe folder name snippet from prompt text."""
    text = text.strip()[:max_len]
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = text.strip('-').lower()
    return text or 'image'


def build_payload(prompt, model, aspect_ratio, image_size):
    """Build the API request payload, adapting config per model."""
    image_config = {
        "aspectRatio": aspect_ratio,
        "imageSize": image_size,
    }

    generation_config = {
        "responseModalities": ["IMAGE", "TEXT"],
        "imageConfig": image_config,
    }

    # Flash supports thinkingConfig; Pro does not
    if "flash" in model:
        generation_config["thinkingConfig"] = {
            "thinkingLevel": "MINIMAL",
        }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }

    # Flash supports Google Search + Image Search grounding
    if "flash" in model:
        payload["tools"] = [{
            "googleSearch": {
                "searchTypes": {
                    "imageSearch": {}
                }
            }
        }]

    return payload


def call_gemini_api(prompt, api_key, model, aspect_ratio, image_size):
    """Call the Gemini generateContent endpoint and return the parsed JSON."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    payload = build_payload(prompt, model, aspect_ratio, image_size)

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"API Error ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def extract_and_save(result, output_dir, prompt, model, aspect_ratio, image_size):
    """Extract images and text from API response, write files to output_dir."""
    os.makedirs(output_dir, exist_ok=True)

    images_saved = []
    response_texts = []
    img_idx = 0

    for candidate in result.get("candidates", []):
        parts = candidate.get("content", {}).get("parts", [])
        for part in parts:
            if "text" in part:
                response_texts.append(part["text"])
            elif "inlineData" in part:
                mime = part["inlineData"].get("mimeType", "image/png")
                ext = "png" if "png" in mime else "jpg"
                img_bytes = base64.b64decode(part["inlineData"]["data"])

                fname = f"image.{ext}" if img_idx == 0 else f"image_{img_idx}.{ext}"
                with open(os.path.join(output_dir, fname), "wb") as f:
                    f.write(img_bytes)
                images_saved.append(fname)
                img_idx += 1

    # Write prompt.md
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Gemini Image Generation",
        "",
        "## Parameters",
        "",
        f"- **Model**: `{model}`",
        f"- **Aspect Ratio**: {aspect_ratio}",
        f"- **Image Size**: {image_size}",
        f"- **Generated At**: {now}",
        "",
        "## Prompt",
        "",
        prompt,
        "",
    ]

    if response_texts:
        lines += ["## Model Response", "", *response_texts, ""]

    if images_saved:
        lines += ["## Generated Images", ""]
        for img in images_saved:
            lines += [f"![{img}](./{img})", ""]

    with open(os.path.join(output_dir, "prompt.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return images_saved, response_texts


def main():
    parser = argparse.ArgumentParser(description="Generate images with the Gemini API")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument(
        "--model", default="gemini-3.1-flash-image-preview",
        help=f"Model ID (default: gemini-3.1-flash-image-preview). Options: {', '.join(VALID_MODELS)}",
    )
    parser.add_argument(
        "--aspect-ratio", default="16:9",
        help="Aspect ratio (default: 16:9). Supported ratios vary by model.",
    )
    parser.add_argument(
        "--image-size", default="2K",
        help="Image resolution (default: 2K). Supported sizes vary by model.",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory (auto-generated if omitted)",
    )
    parser.add_argument(
        "--save-request", action="store_true",
        help="Save response.json (Gemini API response) to output folder",
    )
    args = parser.parse_args()

    # Resolve API key from environment
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "Error: API key not found in environment variables.\n"
            "Please set one of the following:\n"
            "  export GEMINI_API_KEY=\"your-key-here\"\n"
            "  export GOOGLE_API_KEY=\"your-key-here\"\n"
            "Get your key from: https://aistudio.google.com/apikey",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate model name
    if args.model not in VALID_MODELS:
        print(
            f"Error: Unknown model '{args.model}'.\n"
            f"Supported models: {', '.join(VALID_MODELS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    supported_ratios = MODEL_ASPECT_RATIOS[args.model]
    supported_sizes = MODEL_IMAGE_SIZES[args.model]

    # Validate aspect ratio
    if args.aspect_ratio not in supported_ratios:
        print(
            f"Warning: '{args.aspect_ratio}' is not supported by {args.model}. "
            f"Supported: {', '.join(supported_ratios)}. Falling back to 16:9.",
            file=sys.stderr,
        )
        args.aspect_ratio = "16:9"

    # Validate image size
    if args.image_size not in supported_sizes:
        fallback = "1K" if args.image_size == "512" else "2K"
        print(
            f"Warning: '{args.image_size}' is not supported by {args.model}. "
            f"Supported: {', '.join(supported_sizes)}. Falling back to {fallback}.",
            file=sys.stderr,
        )
        args.image_size = fallback

    # Determine output directory: gemini-images/<timestamp>-<topic>/
    output_dir = args.output_dir
    if not output_dir:
        parent = os.path.join(os.getcwd(), "gemini-images")
        os.makedirs(parent, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        slug = sanitize_for_folder(args.prompt)
        output_dir = os.path.join(parent, f"{ts}-{slug}")

    print(f"Generating image with {args.model}...", file=sys.stderr)
    result = call_gemini_api(
        prompt=args.prompt,
        api_key=api_key,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        image_size=args.image_size,
    )

    images, texts = extract_and_save(
        result, output_dir, args.prompt,
        args.model, args.aspect_ratio, args.image_size,
    )

    # Determine actual success based on whether images were generated
    success = len(images) > 0
    if not success:
        print(
            "Warning: No images were generated. The request may have been "
            "blocked by safety filters or returned text-only.",
            file=sys.stderr,
        )

    output = {
        "success": success,
        "output_dir": output_dir,
        "images": images,
        "prompt_md": os.path.join(output_dir, "prompt.md"),
        "response_text": "\n".join(texts),
    }

    if args.save_request:
        response_json_path = os.path.join(output_dir, "response.json")
        with open(response_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        output["response_json"] = response_json_path
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
