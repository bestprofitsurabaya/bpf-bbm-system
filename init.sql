-- ============================================================
-- BPF ASSET SYSTEM - CLEAN SCHEMA (No Seed Data)
-- ============================================================

CREATE DATABASE IF NOT EXISTS bpf_asset_system;
USE bpf_asset_system;

-- Vehicles
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

-- BBM Types
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

-- Vehicle-BBM Allowed
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

-- Drivers
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

-- Users (PIN Security)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin','ga','finance','marketing','chief_driver','driver','ob') NOT NULL DEFAULT 'ga',
    pin VARCHAR(255) NOT NULL,
    team_name VARCHAR(100) DEFAULT '',
    is_active TINYINT(1) DEFAULT 1,
    last_login DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role)
);

-- Transactions
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
    is_dummy TINYINT(1) DEFAULT 0,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_type) REFERENCES vehicles(vehicle_type),
    FOREIGN KEY (bbm_type) REFERENCES bbm_types(name),
    INDEX idx_nopol (nopol),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_status_created (status, created_at),
    INDEX idx_archived (archived_at)
);

-- Activity Logs
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

-- Daily Summary
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

-- System Config
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(50) PRIMARY KEY,
    config_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Trip Masters
CREATE TABLE IF NOT EXISTS trip_masters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    display_id VARCHAR(30) NOT NULL UNIQUE,
    driver_name VARCHAR(100) NOT NULL,
    nopol VARCHAR(20) NOT NULL,
    trip_date DATE NOT NULL,
    jam_keberangkatan TIME NOT NULL,
    jam_tiba TIME,
    km_awal INT NOT NULL,
    km_akhir INT,
    status ENUM('pending','verified_ga','rejected') DEFAULT 'pending',
    verified_by VARCHAR(100),
    verified_at DATETIME,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_driver (driver_name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Trip Details
CREATE TABLE IF NOT EXISTS trip_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_master_id INT NOT NULL,
    no_urut INT NOT NULL,
    lokasi_berangkat VARCHAR(255) NOT NULL,
    pukul_berangkat TIME NOT NULL,
    km_berangkat INT NOT NULL,
    lokasi_tujuan VARCHAR(255) NOT NULL,
    pukul_tujuan TIME NOT NULL,
    km_tujuan INT NOT NULL,
    appointment_id INT DEFAULT NULL,
    FOREIGN KEY (trip_master_id) REFERENCES trip_masters(id) ON DELETE CASCADE,
    INDEX idx_trip_master (trip_master_id),
    INDEX idx_appointment (appointment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Vehicle Assignments
CREATE TABLE IF NOT EXISTS vehicle_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    nopol VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    bbm_type VARCHAR(50) NOT NULL,
    assigned_date DATE NOT NULL,
    unassigned_date DATE DEFAULT NULL,
    is_current TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_driver (driver_name),
    INDEX idx_nopol (nopol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- MARKETING TEAMS
-- ============================================================
CREATE TABLE IF NOT EXISTS marketing_teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    leader_name VARCHAR(100) DEFAULT '',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- APPOINTMENTS (Marketing -> Chief Driver -> Trip Log)
-- Sesi 1 = 08.30, Sesi 2 = 14.30
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    display_id VARCHAR(30) NOT NULL UNIQUE,
    marketing_username VARCHAR(50) NOT NULL,
    marketing_name VARCHAR(100) NOT NULL,
    team_name VARCHAR(100) DEFAULT '',
    nasabah_name VARCHAR(150) NOT NULL,
    nasabah_phone VARCHAR(30) DEFAULT '',
    alamat VARCHAR(500) NOT NULL,
    area VARCHAR(100) DEFAULT '',
    appointment_date DATE NOT NULL,
    sesi ENUM('1','2') NOT NULL DEFAULT '1',
    status ENUM('scheduled','assigned','completed','cancelled') DEFAULT 'scheduled',
    driver_name VARCHAR(100) DEFAULT NULL,
    driver_note VARCHAR(255) DEFAULT '',
    notes VARCHAR(500) DEFAULT '',
    completed_at DATETIME DEFAULT NULL,
    visit_result ENUM('ditemui','prospek','gagal') DEFAULT NULL,
    visit_note VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_date_sesi (appointment_date, sesi),
    INDEX idx_driver (driver_name),
    INDEX idx_status (status),
    INDEX idx_marketing (marketing_username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- DEFAULT USERS (PIN: 123456)
-- ============================================================
INSERT INTO users (username, full_name, role, pin) VALUES 
('admin', 'Administrator', 'admin', '123456'),
('ga_officer', 'GA Officer', 'ga', '123456'),
('finance_officer', 'Finance Officer', 'finance', '123456');

-- Default system config
INSERT INTO system_config (config_key, config_value) VALUES 
('multifill_km_threshold', '40'),
('dummy_data_enabled', 'false');

-- ============================================================
-- NOTIFICATIONS (driver PWA real-time + offline catch-up)
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    action VARCHAR(30) NOT NULL,
    message VARCHAR(255) NOT NULL,
    ref_id VARCHAR(60) DEFAULT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_driver_read (driver_name, is_read),
    KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- AIR MINUM (v2.6) — Tanda Terima Pembelian Air Minum
-- Master tipe & merk dikelola Finance; pengajuan diisi OB;
-- verifikasi (approve/tolak) oleh Finance; PDF TTD Finance+GA.
-- ============================================================
CREATE TABLE IF NOT EXISTS water_drink_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO water_drink_types (name) VALUES ('Gelas'), ('Botol'), ('Galon');

CREATE TABLE IF NOT EXISTS water_drink_brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_id INT NOT NULL,
    brand VARCHAR(100) NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_type_brand (type_id, brand),
    FOREIGN KEY (type_id) REFERENCES water_drink_types(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS water_purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    display_id VARCHAR(30) NOT NULL UNIQUE,
    ob_name VARCHAR(100) NOT NULL,
    purchase_date DATE NOT NULL,
    status ENUM('pending','verified','rejected') DEFAULT 'pending',
    remark VARCHAR(500) DEFAULT '',
    note TEXT,
    rejection_reason VARCHAR(500) DEFAULT '',
    verified_by VARCHAR(100) DEFAULT '',
    verified_at DATETIME DEFAULT NULL,
    foto_before VARCHAR(255),
    foto_after VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_ob (ob_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS water_purchase_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    drink_type VARCHAR(50) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    satuan VARCHAR(20) DEFAULT 'pcs',
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (purchase_id) REFERENCES water_purchases(id) ON DELETE CASCADE,
    INDEX idx_purchase (purchase_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT '✅ Clean database ready' AS result;
