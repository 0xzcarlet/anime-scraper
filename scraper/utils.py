from __future__ import annotations

import hashlib
import logging
import re
import time
from typing import Callable, Iterable, Optional, Tuple, Type

import requests

LOGGER = logging.getLogger(__name__)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "unknown"


def hash_values(values: Iterable[str]) -> str:
    joined = "|".join(sorted(v.strip() for v in values if v))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    *,
    max_retries: int = 3,
    backoff_factor: float = 1.2,
    retry_statuses: Tuple[int, ...] = (429, 500, 502, 503, 504),
    timeout: float = 15,
) -> requests.Response:
    attempt = 0
    while True:
        response = session.request(method, url, timeout=timeout)
        if response.status_code not in retry_statuses:
            return response
        attempt += 1
        if attempt > max_retries:
            response.raise_for_status()
            return response
        sleep_time = backoff_factor * (2 ** (attempt - 1))
        LOGGER.warning("Retrying %s (%s) in %.1fs", url, response.status_code, sleep_time)
        time.sleep(sleep_time)


def rate_limit_sleep(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)
