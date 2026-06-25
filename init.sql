CREATE DATABASE IF NOT EXISTS bpf_asset_system;
USE bpf_asset_system;

-- Tabel utama transaksi
CREATE TABLE IF NOT EXISTS bbm_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    nopol VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(20) DEFAULT 'AVANZA',
    bbm_type VARCHAR(50) DEFAULT 'PERTALITE',
    nominal DECIMAL(15,2) NOT NULL,
    liter DECIMAL(10,2) NOT NULL,
    price_per_liter DECIMAL(10,2) DEFAULT 10000,
    odo_km INT NOT NULL,
    spbu_type ENUM('rekanan', 'non_rekanan') NOT NULL,
    foto_odo_sebelum VARCHAR(255),
    foto_nota_odo_sesudah VARCHAR(255),
    foto_struk VARCHAR(255),
    foto_struk_dispenser VARCHAR(255),
    foto_mypertamina_admin VARCHAR(255),
    is_mypertamina_error BOOLEAN DEFAULT FALSE,
    kronologis_text TEXT,
    status ENUM('pending', 'verified', 'rejected') DEFAULT 'pending',
    ml_anomaly_flag BOOLEAN DEFAULT FALSE,
    km_per_liter DECIMAL(10,2) DEFAULT 0,
    gps_latitude DECIMAL(10,8),
    gps_longitude DECIMAL(11,8),
    gps_address TEXT,
    is_reported BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nopol (nopol),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_driver (driver_name),
    INDEX idx_vehicle (vehicle_type),
    INDEX idx_bbm_type (bbm_type)
);

-- Tabel jenis BBM dan harga
CREATE TABLE IF NOT EXISTS bbm_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    price_per_liter DECIMAL(15,2) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabel setting batas konsumsi per kendaraan
CREATE TABLE IF NOT EXISTS vehicle_fuel_limits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type VARCHAR(20) NOT NULL,
    bbm_type VARCHAR(50) NOT NULL,
    min_km_per_liter DECIMAL(10,2) DEFAULT 5.0,
    max_km_per_liter DECIMAL(10,2) DEFAULT 18.0,
    warning_km_per_liter DECIMAL(10,2) DEFAULT 10.5,
    good_km_per_liter DECIMAL(10,2) DEFAULT 12.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_vehicle_bbm (vehicle_type, bbm_type)
);

-- Data jenis BBM default
INSERT IGNORE INTO bbm_types (name, price_per_liter, description) VALUES
('PERTALITE', 10000, 'BBM subsidi untuk kendaraan umum'),
('PERTAMAX', 13500, 'BBM non-subsidi dengan oktan tinggi'),
('PERTAMAX TURBO', 15000, 'BBM premium untuk performa tinggi'),
('DEXLITE', 12000, 'Solar subsidi'),
('BIOSOLAR', 14000, 'Solar non-subsidi');

-- Data limit kendaraan default
INSERT IGNORE INTO vehicle_fuel_limits (vehicle_type, bbm_type, min_km_per_liter, max_km_per_liter, warning_km_per_liter, good_km_per_liter) VALUES
('AVANZA', 'PERTALITE', 5.0, 18.0, 10.5, 12.5),
('AVANZA', 'PERTAMAX', 5.0, 18.0, 11.0, 13.0),
('INNOVA', 'PERTALITE', 4.0, 16.0, 8.5, 10.5),
('INNOVA', 'PERTAMAX', 4.0, 16.0, 9.0, 11.0),
('AVANZA', 'PERTAMAX TURBO', 5.0, 17.0, 10.0, 12.0),
('INNOVA', 'PERTAMAX TURBO', 4.0, 15.0, 8.0, 10.0);

-- Data dummy
INSERT IGNORE INTO bbm_transactions 
(driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter, odo_km, spbu_type, status, km_per_liter) VALUES
('AKHAD', 'L 1413 CBI', 'AVANZA', 'PERTALITE', 130700, 13.07, 10000, 12936, 'rekanan', 'verified', 5.17),
('AHMAT', 'B 2628 SRP', 'INNOVA', 'PERTAMAX', 130700, 9.68, 13500, 71126, 'rekanan', 'verified', 6.03),
('BUDI', 'L 1234 ABC', 'AVANZA', 'PERTALITE', 150000, 15.0, 10000, 45230, 'non_rekanan', 'verified', 4.92),
('CANDRA', 'B 5678 DEF', 'INNOVA', 'PERTAMAX', 120000, 8.89, 13500, 89200, 'rekanan', 'verified', 5.38);
