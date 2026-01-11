from __future__ import annotations

import argparse
import logging
from pathlib import Path

from scraper.config import Config
from scraper.db import Database
from scraper.fetcher import Fetcher
from scraper.parser_list import parse_anime_list
from scraper.updater import Updater

ANIME_LIST_URL = "https://otakudesu.best/anime-list"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def run(mode: str) -> None:
    config = Config.from_env()
    image_dir = Path(config.image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    db = Database(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
    )
    fetcher = Fetcher(config.rate_limit_seconds, config.request_timeout)
    updater = Updater(db, fetcher, image_dir)

    list_html = fetcher.fetch_html(ANIME_LIST_URL)
    anime_urls = parse_anime_list(list_html, ANIME_LIST_URL)
    logging.getLogger(__name__).info("Found %s anime entries", len(anime_urls))

    if mode == "full":
        updater.full_update(anime_urls)
    elif mode == "daily_update":
        updater.daily_update(anime_urls)
    else:
        raise ValueError(f"Unsupported mode: {mode}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Anime scraper for otakudesu.best")
    parser.add_argument("--mode", choices=["full", "daily_update"], required=True)
    return parser


if __name__ == "__main__":
    configure_logging()
    args = build_parser().parse_args()
    run(args.mode)
