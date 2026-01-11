# anime-scraper

Scraper untuk **otakudesu.best** yang mengambil daftar anime, detail anime, dan semua link download lalu menyimpannya ke MySQL secara idempotent.

## Fitur

- Scrape daftar anime dari `https://otakudesu.best/anime-list`.
- Scrape detail per anime (judul, sinopsis, genre, status/type) dan semua link download.
- Upsert ke MySQL berdasarkan `slug` dan `source_url`.
- Download poster, konversi ke WebP, simpan ke `./data/images/{slug}.webp`.
- Simpan metadata gambar ke tabel `anime_image`.
- Mode `full` dan `daily_update`.
- Rate limiting + retry exponential backoff untuk HTTP 429/5xx.

## Prasyarat

- Python 3.11+
- MySQL
- Schema sudah tersedia di `../infra/schema.sql`

## Konfigurasi Environment

Buat file `.env` di root project:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=secret
DB_NAME=anime
IMAGE_DIR=./data/images
MODE=full
RATE_LIMIT_SECONDS=0.6
REQUEST_TIMEOUT=15
```

## Setup Database (via docker compose infra)

Contoh menjalankan MySQL dengan docker compose yang ada di folder infra:

```bash
cd ../infra
# pastikan schema.sql sudah ter-mount dan di-apply sesuai instruksi infra
# contoh: docker compose up -d
```

Pastikan database dan tabel sudah dibuat sesuai `schema.sql` sebelum menjalankan scraper.

## Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Playwright dipakai hanya jika diperlukan, dan butuh install browser:
>
> ```bash
> python -m playwright install
> ```

## Menjalankan Scraper

Mode full:

```bash
python -m scraper.main --mode full
```

Mode daily update:

```bash
python -m scraper.main --mode daily_update
```

## Smoke Test

Smoke test akan fetch 1 anime pertama dari daftar, insert ke DB, dan download+convert gambar.

```bash
python smoke_test.py
```

## Testing

```bash
pytest -q
```

## Struktur Folder

```
.
├── scraper/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── fetcher.py
│   ├── parser_list.py
│   ├── parser_detail.py
│   ├── image_pipeline.py
│   ├── updater.py
│   └── utils.py
├── tests/
└── smoke_test.py
```
