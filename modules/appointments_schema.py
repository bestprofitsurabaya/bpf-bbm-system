"""Appointment System - schema migration.

Safe to run at every startup (CREATE IF NOT EXISTS + guarded ALTERs)
so existing databases get upgraded without dropping any data.
"""
from modules.config import get_db_connection


def _run(sql, cursor, label):
    try:
        cursor.execute(sql)
        return True
    except Exception as e:
        print(f"[appointments-schema] {label}: {e}")
        return False


def ensure_appointments_schema():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("[appointments-schema] DB unavailable, skip migration")
            return
        cursor = conn.cursor()

        # --- marketing_teams ---
        _run("""
            CREATE TABLE IF NOT EXISTS marketing_teams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                leader_name VARCHAR(100) DEFAULT '',
                is_active TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, cursor, "marketing_teams")

        # --- marketing_members (anggota tim marketing yang memprospek) ---
        _run("""
            CREATE TABLE IF NOT EXISTS marketing_members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_name VARCHAR(100) NOT NULL DEFAULT '',
                member_name VARCHAR(100) NOT NULL,
                is_active TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_team_member (team_name, member_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, cursor, "marketing_members")

        # --- appointments ---
        _run("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                display_id VARCHAR(30) NOT NULL UNIQUE,
                marketing_username VARCHAR(50) NOT NULL,
                marketing_name VARCHAR(100) NOT NULL,
                marketing_member VARCHAR(100) DEFAULT '',
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, cursor, "appointments")

        # --- users: extend role enum ---
        _run("""
            ALTER TABLE users
            MODIFY role ENUM('admin','ga','finance','marketing','chief_driver') NOT NULL DEFAULT 'ga'
        """, cursor, "users.role enum")

        # --- users: team_name column ---
        _run("""
            ALTER TABLE users ADD COLUMN team_name VARCHAR(100) DEFAULT ''
        """, cursor, "users.team_name")

        # --- trip_details: appointment_id ---
        _run("""
            ALTER TABLE trip_details ADD COLUMN appointment_id INT DEFAULT NULL
        """, cursor, "trip_details.appointment_id")

        # --- appointments: marketing_member (upgrade DB lama) ---
        _run("""
            ALTER TABLE appointments ADD COLUMN marketing_member VARCHAR(100) DEFAULT ''
        """, cursor, "appointments.marketing_member")

        # --- appointments: hasil kunjungan (visit_result / visit_note) ---
        _run("""
            ALTER TABLE appointments ADD COLUMN visit_result ENUM('ditemui','prospek','gagal') DEFAULT NULL
        """, cursor, "appointments.visit_result")
        _run("""
            ALTER TABLE appointments ADD COLUMN visit_note VARCHAR(255) DEFAULT ''
        """, cursor, "appointments.visit_note")

        # --- trip_masters: display_id (gap init.sql lama; upgrade DB lama) ---
        _run("""
            ALTER TABLE trip_masters ADD COLUMN display_id VARCHAR(30) DEFAULT NULL
        """, cursor, "trip_masters.display_id")
        # Backfill trip lama yang display_id-nya masih NULL (idempotent)
        _run("""
            UPDATE trip_masters SET display_id = CONCAT('TRIP-', id)
            WHERE display_id IS NULL OR display_id = ''
        """, cursor, "trip_masters.display_id backfill")

        conn.commit()
        cursor.close()
        print("✔ Appointment schema ready")
    except Exception as e:
        print(f"[appointments-schema] error: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
