-- ============================================================
-- DATABASE BPF ASSET SYSTEM - SKEMA LENGKAP
-- ============================================================

CREATE DATABASE IF NOT EXISTS bpf_asset_system;
USE bpf_asset_system;

-- ============================================================
-- 1. TABEL KENDARAAN (VEHICLES)
-- ============================================================
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type VARCHAR(50) NOT NULL UNIQUE,
    brand VARCHAR(50) DEFAULT 'Toyota',
    fuel_capacity DECIMAL(10,2) DEFAULT 45,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. TABEL JENIS BBM (BBM_TYPES)
-- ============================================================
CREATE TABLE IF NOT EXISTS bbm_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    price_per_liter DECIMAL(15,2) NOT NULL,
    octane_rating INT,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. TABEL RELASI KENDARAAN - BBM (VEHICLE_BBM_ALLOWED)
-- ============================================================
CREATE TABLE IF NOT EXISTS vehicle_bbm_allowed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type VARCHAR(50) NOT NULL,
    bbm_type VARCHAR(50) NOT NULL,
    min_km_per_liter DECIMAL(10,2) DEFAULT 5.0,
    max_km_per_liter DECIMAL(10,2) DEFAULT 18.0,
    warning_km_per_liter DECIMAL(10,2) DEFAULT 10.5,
    good_km_per_liter DECIMAL(10,2) DEFAULT 12.5,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_type) REFERENCES vehicles(vehicle_type) ON DELETE CASCADE,
    FOREIGN KEY (bbm_type) REFERENCES bbm_types(name) ON DELETE CASCADE,
    UNIQUE KEY unique_vehicle_bbm (vehicle_type, bbm_type)
);

-- ============================================================
-- 4. TABEL TRANSAKSI (TRANSACTIONS)
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    nopol VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    bbm_type VARCHAR(50) NOT NULL,
    nominal DECIMAL(15,2) NOT NULL,
    liter DECIMAL(10,2) NOT NULL,
    price_per_liter DECIMAL(10,2) NOT NULL,
    odo_km INT NOT NULL,
    spbu_type ENUM('rekanan', 'non_rekanan') NOT NULL,
    foto_odo_sebelum VARCHAR(255),
    foto_nota_odo_sesudah VARCHAR(255),
    foto_struk VARCHAR(255),
    foto_struk_dispenser VARCHAR(255),
    foto_mypertamina_admin VARCHAR(255),
    is_mypertamina_error BOOLEAN DEFAULT FALSE,
    kronologis_text TEXT,
    status ENUM('pending', 'verified', 'rejected', 'modified') DEFAULT 'pending',
    ml_anomaly_flag BOOLEAN DEFAULT FALSE,
    km_per_liter DECIMAL(10,2) DEFAULT 0,
    gps_latitude DECIMAL(10,8),
    gps_longitude DECIMAL(11,8),
    gps_address TEXT,
    is_reported BOOLEAN DEFAULT FALSE,
    modified_by VARCHAR(100),
    modification_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_type) REFERENCES vehicles(vehicle_type),
    FOREIGN KEY (bbm_type) REFERENCES bbm_types(name),
    INDEX idx_nopol (nopol),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_driver (driver_name),
    INDEX idx_vehicle (vehicle_type),
    INDEX idx_bbm_type (bbm_type)
);

-- ============================================================
-- 5. TABEL LOG AKTIVITAS (ACTIVITY_LOGS)
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    action VARCHAR(50) NOT NULL,
    user_type ENUM('driver', 'admin') NOT NULL,
    user_name VARCHAR(100),
    old_data JSON,
    new_data JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    INDEX idx_transaction (transaction_id),
    INDEX idx_created_at (created_at)
);

-- ============================================================
-- 6. TABEL REKAPITULASI HARIAN (DAILY_SUMMARY)
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    vehicle_type VARCHAR(50),
    total_transactions INT DEFAULT 0,
    total_liter DECIMAL(15,2) DEFAULT 0,
    total_nominal DECIMAL(15,2) DEFAULT 0,
    avg_km_per_liter DECIMAL(10,2) DEFAULT 0,
    total_odo_km INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_daily_vehicle (summary_date, vehicle_type)
);

-- ============================================================
-- 7. DATA SEEDING - DEFAULT VEHICLES
-- ============================================================
INSERT IGNORE INTO vehicles (vehicle_type, brand, fuel_capacity, description) VALUES
('AVANZA', 'Toyota', 45, 'Toyota Avanza 1.3L / 1.5L'),
('INNOVA', 'Toyota', 55, 'Toyota Innova 2.0L / 2.4L'),
('RUSH', 'Toyota', 45, 'Toyota Rush 1.5L'),
('HIACE', 'Toyota', 70, 'Toyota Hiace 2.8L');

-- ============================================================
-- 8. DATA SEEDING - DEFAULT BBM TYPES
-- ============================================================
INSERT IGNORE INTO bbm_types (name, price_per_liter, octane_rating, description) VALUES
('PERTALITE', 10000, 90, 'BBM subsidi RON 90'),
('PERTAMAX', 13500, 92, 'BBM non-subsidi RON 92'),
('PERTAMAX TURBO', 15000, 98, 'BBM premium RON 98'),
('DEXLITE', 12000, NULL, 'Solar subsidi'),
('BIOSOLAR', 14000, NULL, 'Solar non-subsidi');

-- ============================================================
-- 9. DATA SEEDING - VEHICLE-BBM ALLOWED
-- ============================================================
INSERT IGNORE INTO vehicle_bbm_allowed (vehicle_type, bbm_type, min_km_per_liter, max_km_per_liter, warning_km_per_liter, good_km_per_liter, is_default) VALUES
-- AVANZA
('AVANZA', 'PERTALITE', 5.0, 18.0, 10.5, 12.5, TRUE),
('AVANZA', 'PERTAMAX', 5.0, 18.0, 11.0, 13.0, FALSE),
('AVANZA', 'PERTAMAX TURBO', 5.0, 17.0, 10.0, 12.0, FALSE),
-- INNOVA
('INNOVA', 'PERTALITE', 4.0, 16.0, 8.5, 10.5, TRUE),
('INNOVA', 'PERTAMAX', 4.0, 16.0, 9.0, 11.0, FALSE),
('INNOVA', 'PERTAMAX TURBO', 4.0, 15.0, 8.0, 10.0, FALSE),
-- RUSH
('RUSH', 'PERTALITE', 5.0, 17.0, 10.0, 12.0, TRUE),
('RUSH', 'PERTAMAX', 5.0, 17.0, 10.5, 12.5, FALSE),
-- HIACE
('HIACE', 'DEXLITE', 3.0, 12.0, 7.0, 9.0, TRUE),
('HIACE', 'BIOSOLAR', 3.0, 12.0, 7.5, 9.5, FALSE);

-- ============================================================
-- 10. DATA DUMMY UNTUK TESTING
-- ============================================================
INSERT IGNORE INTO transactions 
(driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter, odo_km, spbu_type, status, km_per_liter) VALUES
('AKHAD', 'L 1413 CBI', 'AVANZA', 'PERTALITE', 130700, 13.07, 10000, 12936, 'rekanan', 'verified', 5.17),
('AHMAT', 'B 2628 SRP', 'INNOVA', 'PERTAMAX', 130700, 9.68, 13500, 71126, 'rekanan', 'verified', 6.03),
('BUDI', 'L 1234 ABC', 'AVANZA', 'PERTALITE', 150000, 15.0, 10000, 45230, 'non_rekanan', 'verified', 4.92),
('CANDRA', 'B 5678 DEF', 'INNOVA', 'PERTAMAX', 120000, 8.89, 13500, 89200, 'rekanan', 'verified', 5.38);
