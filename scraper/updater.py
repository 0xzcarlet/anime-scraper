from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Iterable, List, Tuple

from scraper.db import Database
from scraper.fetcher import Fetcher
from scraper.image_pipeline import process_image
from scraper.models import Anime, AnimeDownload, AnimeImage
from scraper.parser_detail import parse_anime_detail, parse_download_page
from scraper.utils import hash_values, slugify

LOGGER = logging.getLogger(__name__)


class Updater:
    def __init__(self, db: Database, fetcher: Fetcher, image_dir) -> None:
        self._db = db
        self._fetcher = fetcher
        self._image_dir = image_dir

    def full_update(self, anime_urls: Iterable[str]) -> None:
        for url in anime_urls:
            self._process_anime(url)
        self._db.set_state("last_run", datetime.now(timezone.utc).isoformat())

    def daily_update(self, anime_urls: Iterable[str]) -> None:
        for url in anime_urls:
            self._process_anime(url, daily_mode=True)
        self._db.set_state("last_run", datetime.now(timezone.utc).isoformat())

    def _process_anime(self, url: str, daily_mode: bool = False) -> None:
        slug = slugify(url.split("/anime/")[-1].strip("/"))
        existing = self._db.get_anime_by_slug(slug)
        if daily_mode and existing and existing.status and "ongoing" not in existing.status.lower():
            LOGGER.info("Skipping non-ongoing anime %s", slug)
            return
        html = self._fetcher.fetch_html(url)
        (
            title,
            synopsis,
            genres,
            status,
            anime_type,
            poster_url,
            direct_downloads,
            download_pages,
        ) = parse_anime_detail(html, url)
        downloads: List[AnimeDownload] = [
            AnimeDownload(
                source_url=url,
                section_title=None,
                format=None,
                resolution=None,
                size=None,
                provider=label,
                url=link,
            )
            for label, link in direct_downloads
        ]
        seen_pages = set()
        for page_url in download_pages:
            if page_url in seen_pages:
                continue
            seen_pages.add(page_url)
            page_html = self._fetcher.fetch_html(page_url)
            page_downloads = parse_download_page(page_html, page_url)
            for section_title, format_value, resolution_value, size_value, provider, link in page_downloads:
                downloads.append(
                    AnimeDownload(
                        source_url=page_url,
                        section_title=section_title,
                        format=format_value,
                        resolution=resolution_value,
                        size=size_value,
                        provider=provider,
                        url=link,
                    )
                )
        download_hash = hash_values(
            [
                "|".join(
                    [
                        item.source_url,
                        item.section_title or "",
                        item.format or "",
                        item.resolution or "",
                        item.size or "",
                        item.provider or "",
                        item.url,
                    ]
                )
                for item in downloads
            ]
        )
        if daily_mode and existing and existing.detail_hash == download_hash:
            LOGGER.info("No change detected for %s", slug)
            return
        anime = Anime(
            slug=slug,
            source_url=url,
            title=title,
            synopsis=synopsis,
            status=status,
            type=anime_type,
            genres=genres,
            detail_hash=download_hash,
        )
        anime_id = self._db.upsert_anime(anime)
        self._db.upsert_downloads(anime_id, downloads)
        image_path = self._image_dir / f"{slug}.webp"
        image_result = process_image(poster_url, image_path)
        if image_result:
            original_url, width, height = image_result
            self._db.upsert_image(
                anime_id,
                AnimeImage(
                    original_url=original_url,
                    local_webp_path=str(image_path),
                    width=width,
                    height=height,
                ),
            )
