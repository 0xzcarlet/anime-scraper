from __future__ import annotations

import re
from typing import List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def _text_or_none(element) -> Optional[str]:
    if not element:
        return None
    text = element.get_text(strip=True)
    return text or None


def _normalize_label(link, fallback_url: str) -> str:
    label = link.get_text(" ", strip=True)
    if label:
        return label
    for attr in ("title", "aria-label"):
        value = link.get(attr)
        if value:
            return value
    return fallback_url


def _extract_context_label(link) -> Optional[str]:
    quality_regex = re.compile(
        r"\\b(360|480|540|720|1080|1440|2160)p\\b|\\b(MP4|MKV|WEB|BD|HDRip|BluRay)\\b",
        re.IGNORECASE,
    )
    for parent in list(link.parents)[:5]:
        for candidate in parent.select("strong, b, h3, h4, h5, .quality, .format, .download-qual"):
            text = candidate.get_text(" ", strip=True)
            if text and quality_regex.search(text):
                return text
        parent_text = parent.get_text(" ", strip=True)
        if parent_text and quality_regex.search(parent_text):
            return parent_text
    return None


def _collect_downloads(
    soup: BeautifulSoup,
    base_url: str,
    include_context: bool = False,
) -> List[Tuple[str, str]]:
    downloads: List[Tuple[str, str]] = []
    seen = set()

    def add_link(anchor) -> None:
        href = anchor.get("href")
        if not href:
            return
        absolute_url = urljoin(base_url, href)
        label = _normalize_label(anchor, absolute_url)
        if include_context:
            context_label = _extract_context_label(anchor)
            if context_label and context_label not in label:
                label = f"{context_label} {label}".strip()
        key = (label, absolute_url)
        if key in seen:
            return
        seen.add(key)
        downloads.append((label, absolute_url))

    selectors = [
        ".download .linkdl a[href]",
        ".download .dl-box a[href]",
        ".download a[href]",
        ".linkdownload a[href]",
        ".download-link a[href]",
        ".batchlink a[href]",
        ".batch a[href]",
    ]
    for selector in selectors:
        for link in soup.select(selector):
            add_link(link)

    if downloads:
        return downloads

    container_regex = re.compile(r"(download|dl|mirror|batch)", re.IGNORECASE)
    container_candidates = []
    container_candidates.extend(soup.find_all(class_=container_regex))
    container_candidates.extend(soup.find_all(id=container_regex))
    for container in {id(elem): elem for elem in container_candidates}.values():
        for link in container.select("a[href]"):
            add_link(link)

    if downloads:
        return downloads

    href_regex = re.compile(r"(download|mirror|batch|mega|drive|gdrive|zippy|mediafire)", re.IGNORECASE)
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        if href_regex.search(href):
            add_link(link)

    return downloads


def extract_download_page_urls(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: List[str] = []
    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        if not href:
            continue
        if "/batch/" in href or "/episode/" in href:
            absolute_url = urljoin(base_url, href)
            if absolute_url not in links:
                links.append(absolute_url)
    return links


def parse_download_page(html: str, base_url: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    return _collect_downloads(soup, base_url, include_context=True)


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
    downloads = _collect_downloads(soup, base_url)
    title_value = title or "Unknown"
    return title_value, synopsis, ", ".join(genres) if genres else None, status, anime_type, poster_url, downloads
