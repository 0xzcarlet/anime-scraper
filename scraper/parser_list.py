from __future__ import annotations

from typing import List, Set
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def parse_anime_list(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: Set[str] = set()
    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        if not href:
            continue
        if "/anime/" in href and "anime-list" not in href:
            links.add(urljoin(base_url, href))
    return sorted(links)
