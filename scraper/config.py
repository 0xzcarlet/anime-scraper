from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    image_dir: Path
    mode: str
    rate_limit_seconds: float
    request_timeout: float

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", "3306"))
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "anime")
        image_dir = Path(os.getenv("IMAGE_DIR", "./data/images"))
        mode = os.getenv("MODE", "full")
        rate_limit_seconds = float(os.getenv("RATE_LIMIT_SECONDS", "0.6"))
        request_timeout = float(os.getenv("REQUEST_TIMEOUT", "15"))
        return cls(
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            db_name=db_name,
            image_dir=image_dir,
            mode=mode,
            rate_limit_seconds=rate_limit_seconds,
            request_timeout=request_timeout,
        )
