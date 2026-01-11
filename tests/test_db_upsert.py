import mysql.connector
import pytest

from scraper.config import Config
from scraper.db import Database
from scraper.models import Anime


@pytest.mark.integration
def test_upsert_anime_idempotent():
    config = Config.from_env()
    try:
        conn = mysql.connector.connect(
            host=config.db_host,
            port=config.db_port,
            user=config.db_user,
            password=config.db_password,
            database=config.db_name,
        )
    except mysql.connector.Error:
        pytest.skip("Database not available")

    with conn:
        cur = conn.cursor()
        cur.execute("SHOW TABLES LIKE 'anime'")
        if not cur.fetchone():
            pytest.skip("anime table missing")

    db = Database(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
    )
    anime = Anime(
        slug="test-anime",
        source_url="https://example.com/anime/test-anime",
        title="Test Anime",
        synopsis="Test synopsis",
        status="Ongoing",
        type="TV",
        genres="Action",
        detail_hash="abc",
    )
    first_id = db.upsert_anime(anime)
    second_id = db.upsert_anime(anime)
    assert first_id == second_id
