CREATE DATABASE IF NOT EXISTS bpf_asset_system;
USE bpf_asset_system;

CREATE TABLE IF NOT EXISTS bbm_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nopol VARCHAR(50) NOT NULL,
    nominal INT NOT NULL,
    spbu_type ENUM('rekanan', 'non_rekanan') NOT NULL DEFAULT 'rekanan',
    foto_odo_sebelum VARCHAR(255) NULL,
    foto_nota_odo_sesudah VARCHAR(255) NULL,
    foto_struk VARCHAR(255) NULL,
    foto_struk_dispenser VARCHAR(255) NULL,
    foto_mypertamina_admin VARCHAR(255) NULL,
    is_mypertamina_error BOOLEAN DEFAULT FALSE,
    kronologis_text TEXT NULL,
    status ENUM('pending', 'verified') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
