from pathlib import Path

from io import BytesIO

from PIL import Image

from scraper.image_pipeline import save_webp


def test_save_webp(tmp_path: Path):
    img = Image.new("RGB", (16, 12), color="red")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_path = tmp_path / "test.webp"
    width, height = save_webp(buffer.getvalue(), image_path)
    assert width == 16
    assert height == 12
    assert image_path.exists()
