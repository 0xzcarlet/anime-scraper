from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Anime:
    slug: str
    source_url: str
    title: str
    synopsis: str
    status: Optional[str] = None
    type: Optional[str] = None
    genres: Optional[str] = None
    detail_hash: Optional[str] = None


@dataclass
class AnimeDownload:
    label: str
    url: str


@dataclass
class AnimeImage:
    original_url: str
    local_webp_path: str
    width: int
    height: int
