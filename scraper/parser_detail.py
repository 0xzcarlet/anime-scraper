from __future__ import annotations

from typing import List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def _text_or_none(element) -> Optional[str]:
    if not element:
        return None
    text = element.get_text(strip=True)
    return text or None


def parse_anime_detail(html: str, base_url: str) -> Tuple[str, str, Optional[str], Optional[str], Optional[str], Optional[str], List[Tuple[str, str]]]:
    soup = BeautifulSoup(html, "html.parser")
    title = _text_or_none(soup.select_one("h1")) or _text_or_none(
        soup.select_one(".infox h1")
    )
    synopsis = ""
    synopsis_container = soup.select_one(".sinopsis") or soup.select_one(".sinopsis-film")
    if synopsis_container:
        synopsis = synopsis_container.get_text(" ", strip=True)
    genres = []
    for genre_anchor in soup.select(".genre-info a, .infox a"):
        text = genre_anchor.get_text(strip=True)
        if text:
            genres.append(text)
    status = None
    anime_type = None
    info_rows = soup.select(".infozingle p") or soup.select(".infox .info")
    for row in info_rows:
        content = row.get_text(" ", strip=True)
        if "Status" in content:
            status = content.split(":", 1)[-1].strip()
        if "Tipe" in content or "Type" in content:
            anime_type = content.split(":", 1)[-1].strip()
    poster_url = None
    poster_img = soup.select_one(".fotoanime img") or soup.select_one(".poster img")
    if poster_img and poster_img.get("src"):
        poster_url = urljoin(base_url, poster_img["src"])
    downloads: List[Tuple[str, str]] = []
    for download_block in soup.select(".download .linkdl, .download .dl-box, .download"):
        for link in download_block.select("a[href]"):
            label = link.get_text(" ", strip=True)
            href = link.get("href")
            if href and label:
                downloads.append((label, urljoin(base_url, href)))
    title_value = title or "Unknown"
    return title_value, synopsis, ", ".join(genres) if genres else None, status, anime_type, poster_url, downloads
