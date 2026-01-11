CREATE TABLE IF NOT EXISTS anime (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(255) NOT NULL,
    source_url VARCHAR(512) NOT NULL,
    title VARCHAR(512) NOT NULL,
    synopsis MEDIUMTEXT NOT NULL,
    `status` VARCHAR(100) NULL,
    `type` VARCHAR(100) NULL,
    genres TEXT NULL,
    detail_hash CHAR(64) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_anime_slug (slug),
    UNIQUE KEY uniq_anime_source_url (source_url)
);

CREATE TABLE IF NOT EXISTS anime_download (
    id INT AUTO_INCREMENT PRIMARY KEY,
    anime_id INT NOT NULL,
    source_url VARCHAR(512) NOT NULL,
    section_title VARCHAR(255) NULL,
    format VARCHAR(50) NULL,
    resolution VARCHAR(50) NULL,
    size VARCHAR(50) NULL,
    provider VARCHAR(255) NULL,
    url VARCHAR(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_anime_download (anime_id, source_url, format, resolution, provider, url),
    CONSTRAINT fk_anime_download_anime_id FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS anime_image (
    id INT AUTO_INCREMENT PRIMARY KEY,
    anime_id INT NOT NULL,
    original_url VARCHAR(1024) NOT NULL,
    local_webp_path VARCHAR(512) NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_anime_image_anime_id (anime_id),
    CONSTRAINT fk_anime_image_anime_id FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scrape_state (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state_key VARCHAR(255) NOT NULL,
    state_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_scrape_state_key (state_key)
);
