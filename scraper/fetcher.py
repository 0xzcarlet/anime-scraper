from __future__ import annotations

import logging
from typing import Optional

import requests

from scraper.utils import rate_limit_sleep, request_with_retry

LOGGER = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, rate_limit_seconds: float, timeout: float) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "anime-scraper/1.0 (+https://otakudesu.best)",
            }
        )
        self._rate_limit_seconds = rate_limit_seconds
        self._timeout = timeout

    def fetch_html(self, url: str, use_js: bool = False) -> str:
        if use_js:
            html = self._fetch_with_playwright(url)
            if html:
                rate_limit_sleep(self._rate_limit_seconds)
                return html
        response = request_with_retry(
            self._session,
            "GET",
            url,
            timeout=self._timeout,
        )
        response.raise_for_status()
        rate_limit_sleep(self._rate_limit_seconds)
        return response.text

    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:  # pragma: no cover - optional dependency
            LOGGER.warning("Playwright not available: %s", exc)
            return None

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=int(self._timeout * 1000))
                html = page.content()
                browser.close()
                return html
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Playwright fetch failed for %s: %s", url, exc)
            return None
