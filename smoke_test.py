from __future__ import annotations

import logging
from pathlib import Path

from scraper.config import Config
from scraper.db import Database
from scraper.fetcher import Fetcher
from scraper.parser_detail import parse_anime_detail
from scraper.parser_list import parse_anime_list
from scraper.updater import Updater
from scraper.utils import slugify

ANIME_LIST_URL = "https://otakudesu.best/anime-list"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    config = Config.from_env()
    db = Database(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
    )
    fetcher = Fetcher(config.rate_limit_seconds, config.request_timeout)
    list_html = fetcher.fetch_html(ANIME_LIST_URL)
    anime_urls = parse_anime_list(list_html, ANIME_LIST_URL)
    if not anime_urls:
        raise RuntimeError("No anime URLs found.")
    first_url = anime_urls[0]
    logging.info("Smoke testing first anime: %s", first_url)
    updater = Updater(db, fetcher, Path(config.image_dir))
    updater.full_update([first_url])
    slug = slugify(first_url.split("/anime/")[-1].strip("/"))
    logging.info("Smoke test completed for %s", slug)


if __name__ == "__main__":
    main()
