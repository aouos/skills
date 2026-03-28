---
name: gemini-image-gen
description: "Generate images using the Gemini API (AI Studio key). Use when user asks to generate/create images with Gemini, Google AI, or mentions '图片生成', 'Gemini 生图', 'AI 生图', 'generate image', 'create image'."
---

# Gemini Image Generation

```bash
python <skill-path>/scripts/generate_image.py "your prompt here"
```

Output: `gemini-images/{timestamp}-{slug}/` containing `prompt.md`, `image.png`, and optionally `response.json`.

## Requirements

`GEMINI_API_KEY` or `GOOGLE_API_KEY` env var ([get key](https://aistudio.google.com/apikey)).

First-time permission setup:

```bash
claude config add permissions.allow "Bash(python */gemini-image-gen/scripts/generate_image.py*)"
```

## Models

| Model                            | Notes                                                                 |
| -------------------------------- | --------------------------------------------------------------------- |
| `gemini-3.1-flash-image-preview` | **Default.** Fast, supports thinkingConfig + googleSearch/imageSearch |
| `gemini-3-pro-image-preview`     | Higher quality, better text rendering and complex layouts             |

## Parameters

### `--image-size`

Must use **uppercase `K`**. Unsupported values are caught by the script and fall back (Pro 512→1K, others→2K).

| Value | Flash       | Pro |
| ----- | ----------- | --- |
| `512` | Yes         | No  |
| `1K`  | Yes         | Yes |
| `2K`  | **default** | Yes |
| `4K`  | Yes         | Yes |

### `--aspect-ratio`

**Flash** (14): `1:1` · `1:4` · `1:8` · `2:3` · `3:2` · `3:4` · `4:1` · `4:3` · `4:5` · `5:4` · `8:1` · `9:16` · `16:9` · `21:9`

**Pro** (10): `1:1` · `2:3` · `3:2` · `3:4` · `4:3` · `4:5` · `5:4` · `9:16` · `16:9` · `21:9`

Unsupported ratio auto-falls back to `16:9`.

### Other flags

- `--save-request`: Save `response.json` (Gemini API response) to output folder
- `--output-dir`: Override auto-generated output path

## Workflow

**IMPORTANT:**

- You MUST use `AskUserQuestion` tool (not plain text) to collect user input. Plain text does NOT pause execution.
- Match the user's language for all UI text (questions, labels, descriptions).

### Step 1: Collect Prompt

- User already provided a clear prompt → use it directly, craft an English version (Gemini works best with English), go to Step 2.
- No prompt or too vague → call `AskUserQuestion`:
  - question: "Describe the image you want to generate:"
  - header: "Prompt"
  - options: provide 2-3 example prompts as inspiration (e.g. "Cyberpunk city at night", "Watercolor cat portrait")

### Step 2: Settings

Call `AskUserQuestion` with 4 questions in a single call. The first option in each is the default (Recommended). Users can accept defaults or switch as needed:

1. **Model** — header: "Model", options: "Flash (Recommended)" / "Pro"
2. **Size** — header: "Size", options: "2K (Recommended)" / "1K" / "4K"
3. **Ratio** — header: "Ratio", options: "16:9 (Recommended)" / "1:1" / "9:16" / "21:9"
4. **Save JSON** — header: "Debug", options: "No (Recommended)" / "Save response.json"

### Step 3: Generate

```bash
python <skill-path>/scripts/generate_image.py "prompt" [--model ...] [--aspect-ratio ...] [--image-size ...] [--save-request]
```

### Step 4: Results

1. Read and show the generated image
2. If `success: false` → inform user (likely safety filter)
3. Report output folder path

## Prompt Tips

- Style: "oil painting", "3D render", "watercolor", "photorealistic"
- Lighting: "golden hour", "dramatic rim lighting", "soft diffused"
- Composition: "bird's eye view", "close-up", "wide establishing shot"
- Mood: "mysterious", "cheerful", "melancholic", "epic"
- Text in images: 25 characters or fewer

## Error Handling

| Error            | Cause                                                    | Fix                                         |
| ---------------- | -------------------------------------------------------- | ------------------------------------------- |
| `400`            | Invalid parameter                                        | Check supported values for the chosen model |
| `401/403`        | Bad API key                                              | Check env var                               |
| `429`            | Rate limit                                               | Wait and retry                              |
| `success: false` | No image generated (safety filter or text-only response) | Adjust prompt                               |
