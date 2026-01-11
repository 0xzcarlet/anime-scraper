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
    source_url: str
    section_title: Optional[str]
    format: Optional[str]
    resolution: Optional[str]
    size: Optional[str]
    provider: Optional[str]
    url: str


@dataclass
class AnimeImage:
    original_url: str
    local_webp_path: str
    width: int
    height: int
