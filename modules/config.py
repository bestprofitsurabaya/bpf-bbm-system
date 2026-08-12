"""Database & App Configuration"""
import os
import mysql.connector
from mysql.connector import Error, pooling
from mysql.connector.connection import MySQLConnection

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'user': os.environ.get('DB_USER', 'bpf_user'),
    'password': os.environ.get('DB_PASSWORD', 'bpf_pass'),
    'database': os.environ.get('DB_NAME', 'bpf_asset_system'),
    'pool_name': 'bbm_pool',
    'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
    'pool_reset_session': True,
    'autocommit': False,
    'connect_timeout': 60,
    'use_pure': True
}

db_pool = None

def init_pool():
    global db_pool
    try:
        db_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
        print("✔ MySQLConnectionPool initialized")
    except Error as e:
        print(f"❌ Pool init failed: {e}")
        db_pool = None

def get_db_connection():
    import time
    if db_pool:
        try:
            return db_pool.get_connection()
        except Error as pool_err:
            print(f"⚠ Pool exhausted: {pool_err}")

    # Fallback: koneksi langsung NON-POOL. Penting: buang SEMUA argumen pool
    # (CNX_POOL_ARGS = pool_name, pool_size, pool_reset_session) karena bila
    # tersisa, mysql.connector.connect() akan kembali di-routing ke pool global
    # yang sama (lihat pooling.connect) dan tetap gagal saat pool exhausted.
    max_retries = 5
    fallback_config = {k: v for k, v in DB_CONFIG.items()
                       if k not in ('pool_name', 'pool_size', 'pool_reset_session')}
    for attempt in range(max_retries):
        try:
            return MySQLConnection(**fallback_config)
        except Error as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    return None
