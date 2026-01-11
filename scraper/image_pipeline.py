from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional, Tuple

import requests
from PIL import Image

LOGGER = logging.getLogger(__name__)


def download_image(url: str, timeout: float = 15) -> Optional[bytes]:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as exc:
        LOGGER.warning("Failed to download image %s: %s", url, exc)
        return None


def save_webp(image_bytes: bytes, output_path: Path) -> Tuple[int, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(image_bytes)) as img:
        rgb_img = img.convert("RGB")
        rgb_img.save(output_path, format="WEBP")
        return rgb_img.width, rgb_img.height


def process_image(url: Optional[str], output_path: Path, timeout: float = 15) -> Optional[Tuple[str, int, int]]:
    if not url:
        return None
    image_bytes = download_image(url, timeout=timeout)
    if not image_bytes:
        return None
    width, height = save_webp(image_bytes, output_path)
    return url, width, height
