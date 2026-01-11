from __future__ import annotations

import contextlib
import logging
from dataclasses import asdict
from typing import Iterable, Optional

import mysql.connector
from mysql.connector import pooling

from scraper.models import Anime, AnimeDownload, AnimeImage

LOGGER = logging.getLogger(__name__)


class Database:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        pool_size: int = 5,
    ) -> None:
        self._pool = pooling.MySQLConnectionPool(
            pool_name="anime_pool",
            pool_size=pool_size,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=False,
        )

    @contextlib.contextmanager
    def connection(self):
        conn = self._pool.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def upsert_anime(self, anime: Anime) -> int:
        query = (
            "INSERT INTO anime (slug, source_url, title, synopsis, `status`, `type`, genres, detail_hash) "
            "VALUES (%(slug)s, %(source_url)s, %(title)s, %(synopsis)s, %(status)s, %(type)s, %(genres)s, %(detail_hash)s) "
            "ON DUPLICATE KEY UPDATE title=VALUES(title), synopsis=VALUES(synopsis), "
            "`status`=VALUES(`status`), `type`=VALUES(`type`), genres=VALUES(genres), detail_hash=VALUES(detail_hash)"
        )
        payload = asdict(anime)
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query, payload)
            anime_id = cur.lastrowid
            if anime_id == 0:
                cur.execute("SELECT id FROM anime WHERE slug=%s", (anime.slug,))
                row = cur.fetchone()
                if row:
                    anime_id = row[0]
        return anime_id

    def upsert_downloads(self, anime_id: int, downloads: Iterable[AnimeDownload]) -> None:
        delete_query = "DELETE FROM anime_download WHERE anime_id=%s"
        insert_query = (
            "INSERT INTO anime_download "
            "(anime_id, source_url, section_title, format, resolution, size, provider, url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(delete_query, (anime_id,))
            cur.executemany(
                insert_query,
                [
                    (
                        anime_id,
                        download.source_url,
                        download.section_title,
                        download.format,
                        download.resolution,
                        download.size,
                        download.provider,
                        download.url,
                    )
                    for download in downloads
                ],
            )

    def upsert_image(self, anime_id: int, image: AnimeImage) -> None:
        query = (
            "INSERT INTO anime_image (anime_id, original_url, local_webp_path, width, height) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE original_url=VALUES(original_url), "
            "local_webp_path=VALUES(local_webp_path), width=VALUES(width), height=VALUES(height)"
        )
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                query,
                (
                    anime_id,
                    image.original_url,
                    image.local_webp_path,
                    image.width,
                    image.height,
                ),
            )

    def get_anime_by_slug(self, slug: str) -> Optional[Anime]:
        query = "SELECT slug, source_url, title, synopsis, `status`, `type`, genres, detail_hash FROM anime WHERE slug=%s"
        with self.connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, (slug,))
            row = cur.fetchone()
        if not row:
            return None
        return Anime(
            slug=row["slug"],
            source_url=row["source_url"],
            title=row["title"],
            synopsis=row["synopsis"],
            status=row.get("status"),
            type=row.get("type"),
            genres=row.get("genres"),
            detail_hash=row.get("detail_hash"),
        )

    def get_state(self, key: str) -> Optional[str]:
        query = "SELECT state_value FROM scrape_state WHERE state_key=%s"
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (key,))
            row = cur.fetchone()
        return row[0] if row else None

    def set_state(self, key: str, value: str) -> None:
        query = (
            "INSERT INTO scrape_state (state_key, state_value) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE state_value=VALUES(state_value)"
        )
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (key, value))
