#!/usr/bin/env python3
import argparse
import base64
import mimetypes
import os
import re
import sys
import time
from typing import Optional

from openai import OpenAI

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}


def build_data_url(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "application/octet-stream"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def sanitize_caption(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "image"


def extract_output_text(resp) -> Optional[str]:
    if getattr(resp, "output_text", None):
        return resp.output_text
    output = getattr(resp, "output", []) or []
    for item in output:
        if getattr(item, "type", None) == "message":
            for content in getattr(item, "content", []) or []:
                if getattr(content, "type", None) == "output_text":
                    return content.text
    return None


def caption_image(client: OpenAI, model: str, data_url: str, max_tokens: int) -> str:
    prompt = (
        "Create a descriptive filename for this image. "
        "Return only the filename words, no quotes. "
        "Use 6-12 words. Use underscores instead of spaces. "
        "Only letters, numbers, underscores. No trailing underscores."
    )
    resp = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
        max_output_tokens=max_tokens,
    )
    text = extract_output_text(resp)
    if not text:
        raise RuntimeError("No text returned from model")
    return text.strip()


def unique_path(directory: str, base: str, ext: str) -> str:
    candidate = os.path.join(directory, f"{base}{ext}")
    if not os.path.exists(candidate):
        return candidate
    i = 2
    while True:
        candidate = os.path.join(directory, f"{base}_{i:02d}{ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1


def iter_images(folder: str):
    for name in sorted(os.listdir(folder)):
        if name.startswith("."):
            continue
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext in IMAGE_EXTS:
            yield name, path, ext


def main() -> int:
    parser = argparse.ArgumentParser(description="Rename photos using AI-generated captions.")
    parser.add_argument("--dir", default="photos", help="Folder with images (default: photos)")
    parser.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model for captioning")
    parser.add_argument("--env-var", default="OPENAI_API_KEY", help="API key env var name")
    parser.add_argument("--dry-run", action="store_true", help="Show renames without writing")
    parser.add_argument("--sleep", type=float, default=0.2, help="Seconds to sleep between calls")
    parser.add_argument("--max-tokens", type=int, default=80, help="Max output tokens")
    args = parser.parse_args()

    api_key = os.getenv(args.env_var)
    if not api_key:
        print(f"Missing API key. Set ${args.env_var}.", file=sys.stderr)
        return 1

    client = OpenAI(api_key=api_key)
    folder = args.dir
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}", file=sys.stderr)
        return 1

    for name, path, ext in iter_images(folder):
        data_url = build_data_url(path)
        try:
            caption = caption_image(client, args.model, data_url, args.max_tokens)
        except Exception as exc:
            print(f"ERROR: {name}: {exc}", file=sys.stderr)
            continue

        base = sanitize_caption(caption)
        new_path = unique_path(folder, base, ext)
        if os.path.abspath(new_path) == os.path.abspath(path):
            print(f"SKIP: {name} (unchanged)")
            continue

        if args.dry_run:
            print(f"DRY: {name} -> {os.path.basename(new_path)}")
        else:
            os.rename(path, new_path)
            print(f"REN: {name} -> {os.path.basename(new_path)}")

        if args.sleep > 0:
            time.sleep(args.sleep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
