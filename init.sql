-- ============================================================
-- BPF ASSET SYSTEM - COMPLETE SCHEMA WITH DUMMY DATA SUPPORT
-- ============================================================

CREATE DATABASE IF NOT EXISTS bpf_asset_system;
USE bpf_asset_system;

-- ============================================================
-- 1. TABEL KENDARAAN
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
-- 2. TABEL JENIS BBM
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
-- 3. TABEL RELASI KENDARAAN-BBM
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
-- 4. TABEL DRIVERS (Master Data)
-- ============================================================
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    nopol VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    bbm_type VARCHAR(50) NOT NULL DEFAULT 'PERTALITE',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_nopol (nopol)
);

-- ============================================================
-- 5. TABEL USERS (PIN Security)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin','ga','finance') NOT NULL DEFAULT 'ga',
    pin VARCHAR(255) NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    last_login DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role)
);

-- ============================================================
-- 6. TABEL TRANSAKSI
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
    status ENUM('pending','verified_ga','os_finance','archived','rejected','modified') DEFAULT 'pending',
    ml_anomaly_flag BOOLEAN DEFAULT FALSE,
    km_per_liter DECIMAL(10,2) DEFAULT 0,
    gps_latitude DECIMAL(10,8),
    gps_longitude DECIMAL(11,8),
    gps_address TEXT,
    jumlah_appointment INT DEFAULT 0,
    is_reported BOOLEAN DEFAULT FALSE,
    modified_by VARCHAR(100),
    modification_note TEXT,
    ga_approved_by VARCHAR(100) DEFAULT NULL,
    ga_approved_at DATETIME DEFAULT NULL,
    approved_by_user VARCHAR(50) DEFAULT NULL,
    finance_payout_by VARCHAR(100) DEFAULT NULL,
    finance_payout_at DATETIME DEFAULT NULL,
    payout_by_user VARCHAR(50) DEFAULT NULL,
    archived_by VARCHAR(100) DEFAULT NULL,
    archived_at DATETIME DEFAULT NULL,
    archived_by_user VARCHAR(50) DEFAULT NULL,
    rejection_reason TEXT DEFAULT NULL,
    transaction_notes TEXT DEFAULT NULL,
    is_dummy TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_type) REFERENCES vehicles(vehicle_type),
    FOREIGN KEY (bbm_type) REFERENCES bbm_types(name),
    INDEX idx_nopol (nopol),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_status_created (status, created_at),
    INDEX idx_archived (archived_at),
    INDEX idx_dummy (is_dummy)
);

-- ============================================================
-- 7. TABEL LOG AKTIVITAS
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    action VARCHAR(50) NOT NULL,
    user_type VARCHAR(20) NOT NULL,
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
-- 8. TABEL REKAPITULASI HARIAN
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
-- 9. TABEL DUMMY DATA CONTROL
-- ============================================================
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(50) PRIMARY KEY,
    config_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT IGNORE INTO system_config (config_key, config_value) VALUES ('dummy_data_enabled', 'false');

-- ============================================================
-- SEED DATA: VEHICLES (Selalu ada)
-- ============================================================
INSERT IGNORE INTO vehicles (vehicle_type, brand, fuel_capacity, description) VALUES
('AVANZA', 'Toyota', 45, 'Toyota Avanza 1.3L / 1.5L'),
('INNOVA', 'Toyota', 55, 'Toyota Innova 2.0L / 2.4L'),
('RUSH', 'Toyota', 45, 'Toyota Rush 1.5L'),
('HIACE', 'Toyota', 70, 'Toyota Hiace 2.8L');

-- ============================================================
-- SEED DATA: BBM TYPES (Selalu ada)
-- ============================================================
INSERT IGNORE INTO bbm_types (name, price_per_liter, octane_rating, description) VALUES
('PERTALITE', 10000, 90, 'BBM RON 90'),
('PERTAMAX', 13500, 92, 'BBM RON 92'),
('PERTAMAX TURBO', 15000, 98, 'BBM RON 98'),
('DEXLITE', 12000, NULL, 'Solar subsidi'),
('BIOSOLAR', 14000, NULL, 'Solar non-subsidi');

-- ============================================================
-- SEED DATA: VEHICLE-BBM ALLOWED (Selalu ada)
-- ============================================================
INSERT IGNORE INTO vehicle_bbm_allowed (vehicle_type, bbm_type, min_km_per_liter, max_km_per_liter, warning_km_per_liter, good_km_per_liter, is_default) VALUES
('AVANZA', 'PERTALITE', 5.0, 18.0, 10.5, 12.5, TRUE),
('AVANZA', 'PERTAMAX', 5.0, 18.0, 11.0, 13.0, FALSE),
('AVANZA', 'PERTAMAX TURBO', 5.0, 17.0, 10.0, 12.0, FALSE),
('INNOVA', 'PERTALITE', 4.0, 16.0, 8.5, 10.5, TRUE),
('INNOVA', 'PERTAMAX', 4.0, 16.0, 9.0, 11.0, FALSE),
('INNOVA', 'PERTAMAX TURBO', 4.0, 15.0, 8.0, 10.0, FALSE),
('RUSH', 'PERTALITE', 5.0, 17.0, 10.0, 12.0, TRUE),
('RUSH', 'PERTAMAX', 5.0, 17.0, 10.5, 12.5, FALSE),
('HIACE', 'DEXLITE', 3.0, 12.0, 7.0, 9.0, TRUE),
('HIACE', 'BIOSOLAR', 3.0, 12.0, 7.5, 9.5, FALSE);

-- ============================================================
-- SEED DATA: USERS (Selalu ada - PIN default)
-- ============================================================
INSERT IGNORE INTO users (username, full_name, role, pin) VALUES 
('admin', 'Administrator', 'admin', '123456'),
('ga_officer', 'GA Officer', 'ga', '123456'),
('finance_officer', 'Finance Officer', 'finance', '123456');

-- ============================================================
-- SEED DATA: DRIVERS SAMPLE (Selalu ada)
-- ============================================================
INSERT IGNORE INTO drivers (name, nopol, vehicle_type, bbm_type) VALUES
('AKHAD', 'L 1413 CBI', 'AVANZA', 'PERTALITE'),
('AHMAT', 'B 2628 SRP', 'INNOVA', 'PERTAMAX'),
('BUDI', 'L 1234 ABC', 'AVANZA', 'PERTALITE'),
('CANDRA', 'B 5678 DEF', 'INNOVA', 'PERTAMAX');

-- ============================================================
-- DUMMY TRANSACTIONS (For demo - controlled by system_config)
-- ============================================================
INSERT IGNORE INTO transactions 
(driver_name, nopol, vehicle_type, bbm_type, nominal, liter, price_per_liter, odo_km, spbu_type, status, km_per_liter, jumlah_appointment, is_dummy, gps_address, kronologis_text) VALUES
('AKHAD', 'L 1413 CBI', 'AVANZA', 'PERTALITE', 200000, 20.00, 10000, 12936, 'rekanan', 'archived', 12.50, 3, 1, 'Jl. Raya Darmo No. 45, Surabaya', 'Pengisian BBM rutin untuk operasional marketing'),
('AHMAT', 'B 2628 SRP', 'INNOVA', 'PERTAMAX', 270000, 20.00, 13500, 71126, 'rekanan', 'archived', 10.20, 5, 1, 'Jl. Ahmad Yani No. 120, Surabaya', 'Pengisian BBM untuk kunjungan client area Surabaya Barat'),
('BUDI', 'L 1234 ABC', 'AVANZA', 'PERTALITE', 150000, 15.00, 10000, 45230, 'non_rekanan', 'verified_ga', 11.00, 2, 1, 'Jl. Raya Gubeng No. 78, Surabaya', 'Pengisian darurat di SPBU non-rekanan'),
('CANDRA', 'B 5678 DEF', 'INNOVA', 'PERTAMAX', 300000, 22.22, 13500, 89200, 'rekanan', 'os_finance', 9.50, 4, 1, 'Jl. Mayjend Sungkono No. 200, Surabaya', 'Pengisian BBM untuk operasional mingguan');
