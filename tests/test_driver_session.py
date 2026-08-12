"""
Unit Tests — Identitas Driver dari Sesi Login PIN (v2.4 / Fase 2 migrasi Vue)
BPF BBM System

`session_driver_name()` adalah sumber identitas tunggal untuk sesi role 'driver':
- role driver + user_name → nama driver (UPPER) yang TIDAK bisa dipalsukan via
  parameter `driver`/`driver_name` (anti impersonasi & IDOR — ISO/IEC 27001 A.8.2).
- role lain / tanpa sesi → None (jalur legacy PWA memakai parameter query/form).

Jalankan:
    docker exec bbm_web python3 -m pytest tests/test_driver_session.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, session
from modules.helpers import session_driver_name, home_for_role, ROLE_HOME, resolve_driver_scope

# App minimal hanya untuk test request context sesi (tanpa DB).
app = Flask(__name__)
app.secret_key = 'test-secret'


class TestSessionDriverName:
    def test_tanpa_sesi_menghasilkan_none(self):
        """Tanpa login → tidak ada identitas driver (jalur legacy memakai param)."""
        with app.test_request_context():
            session.clear()
            assert session_driver_name() is None

    def test_sesi_driver_mengembalikan_username_uppercase(self):
        """Sesi role 'driver' → nama driver di-UPPER-kan (cocok dengan drivers.name)."""
        with app.test_request_context():
            session.clear()
            session['user_role'] = 'driver'
            session['user_name'] = 'rivan'
            assert session_driver_name() == 'RIVAN'

    def test_username_awalnya_uppercase_tetap_utuh(self):
        with app.test_request_context():
            session.clear()
            session['user_role'] = 'driver'
            session['user_name'] = 'RIVAN'
            assert session_driver_name() == 'RIVAN'

    def test_role_lain_tidak_menghasilkan_driver(self):
        """Admin/GA/Finance/login apa pun BUKAN identitas driver."""
        for role, uname in (('admin', 'admin'), ('ga', 'ga_officer'), ('marketing', 'icang')):
            with app.test_request_context():
                session.clear()
                session['user_role'] = role
                session['user_name'] = uname
                assert session_driver_name() is None, f'role {role} tidak boleh jadi driver'


class TestHomeForRoleDriver:
    def test_role_driver_masuk_rolegit_rolegit_home(self):
        """Driver login → diarahkan ke SPA /app/driver."""
        assert ROLE_HOME.get('driver') == '/app/driver'
        assert home_for_role('driver') == '/app/driver'

    def test_role_lain_tetap_dashboard(self):
        assert home_for_role('ga') == '/app/dashboard'
        assert home_for_role('finance') == '/app/dashboard'


class TestResolveDriverScope:
    """v2.5: jalur legacy `?driver=` anonim ditutup (None → 401 di route)."""

    def test_anon_tanpa_param_none(self):
        """Tanpa sesi → None (pemanggil menolak 401)."""
        with app.test_request_context():
            session.clear()
            assert resolve_driver_scope('RIVAN') is None

    def test_sesi_driver_mengalahkan_param(self):
        """Sesi driver login dipaksa memakai identitas sendiri (anti impersonasi)."""
        with app.test_request_context():
            session.clear()
            session['user_role'] = 'driver'
            session['user_name'] = 'rivan'
            # param berbeda pun tidak bisa memalsukan identitas
            assert resolve_driver_scope('ORANG_LAIN') == 'RIVAN'

    def test_backoffice_param_diizinkan(self):
        """Sesi back-office (admin UI) boleh query data per driver eksplisit."""
        with app.test_request_context():
            session.clear()
            session['user_role'] = 'admin'
            assert resolve_driver_scope('RIVAN') == 'RIVAN'

    def test_backoffice_tanpa_param_kosong(self):
        """Back-office tanpa param → '' (artinya 'semua'), bukan None."""
        with app.test_request_context():
            session.clear()
            session['user_role'] = 'ga'
            assert resolve_driver_scope('') == ''
