---
name: gemini-image-gen
description: "Generate images using the Gemini API (AI Studio key). Use when user asks to generate/create images with Gemini, Google AI, or mentions 'Gemini 图片', 'Gemini 生图', 'AI Studio 生图'."
---

# Gemini Image Generation

```bash
python <skill-path>/scripts/generate_image.py "your prompt here"
```

Output: `gemini-images/{timestamp}-{slug}/` containing `prompt.md`, `image.png`, and optionally `request.json`.

## Requirements

`GEMINI_API_KEY` or `GOOGLE_API_KEY` env var ([get key](https://aistudio.google.com/apikey)).

First-time permission setup:
```bash
claude config add permissions.allow "Bash(python */gemini-image-gen/scripts/generate_image.py*)"
```

## Models

| Model | Notes |
|---|---|
| `gemini-3.1-flash-image-preview` | **Default.** Fast, supports thinkingConfig + googleSearch/imageSearch |
| `gemini-3-pro-image-preview` | Higher quality, better text rendering and complex layouts |

## Parameters

### `--image-size`
Must use **uppercase `K`**. Unsupported values are caught by the script and fall back (Pro 512→1K, others→2K).

| Value | Flash | Pro |
|---|---|---|
| `512` | Yes | No |
| `1K` | Yes | Yes |
| `2K` | **default** | Yes |
| `4K` | Yes | Yes |

### `--aspect-ratio`
**Flash** (14): `1:1` · `1:4` · `1:8` · `2:3` · `3:2` · `3:4` · `4:1` · `4:3` · `4:5` · `5:4` · `8:1` · `9:16` · `16:9` · `21:9`

**Pro** (10): `1:1` · `2:3` · `3:2` · `3:4` · `4:3` · `4:5` · `5:4` · `9:16` · `16:9` · `21:9`

Unsupported ratio auto-falls back to `16:9`.

### Other flags
- `--person-generation`: `ALLOW_ADULT`(default) · `ALLOW_ALL` · `ALLOW_NONE`
- `--save-request`: Save `request.json` (API payload without key) to output folder
- `--output-dir`: Override auto-generated output path

## Workflow (Interactive)

Use `AskUserQuestion` for guidance. Skip steps when the user already provided enough info.

### Step 1: Prompt

Clear description (e.g. "生成一张赛博朋克城市夜景") → Step 2.

Vague request → ask for details. Craft a detailed English prompt (Gemini works best with English). Show the crafted prompt for transparency.

### Step 2: Confirm Parameters

> **Generation settings:**
> - Model: Flash / Pro
> - Size: 2K
> - Ratio: 16:9
> - Prompt: "..."
>
> Enter to generate, or tell me what to change

### Step 3: Generate

```bash
python <skill-path>/scripts/generate_image.py "prompt" [--model ...] [--aspect-ratio ...] [--image-size ...] [--save-request]
```

### Step 4: Results

1. Show the generated image (Read tool on image file)
2. Check `success` field — if `false`, the image was likely blocked by safety filters; inform the user
3. Report output folder path
4. Ask if the user wants to regenerate or adjust

## Prompt Tips

- Style: "oil painting", "3D render", "watercolor", "photorealistic"
- Lighting: "golden hour", "dramatic rim lighting", "soft diffused"
- Composition: "bird's eye view", "close-up", "wide establishing shot"
- Mood: "mysterious", "cheerful", "melancholic", "epic"
- Text in images: 25 characters or fewer

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `400` | Invalid parameter | Check supported values for the chosen model |
| `401/403` | Bad API key | Check env var |
| `429` | Rate limit | Wait and retry |
| `success: false` | No image generated (safety filter or text-only response) | Adjust prompt |
