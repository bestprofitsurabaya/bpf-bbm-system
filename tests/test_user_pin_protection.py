"""
Unit Tests — Kebijakan Proteksi PIN User (ISO/IEC 27001 A.9.4)
BPF BBM System v2.2.1

Memastikan operasi toggle aktif/nonaktif & hapus user TIDAK menimpa PIN:
- `resolve_user_pin`  -> None bila field `pin` tidak dikirim/kosong (jangan ubah),
                        nilai PIN bila dikirim eksplisit.
- `finalize_pin`      -> fallback level-route: None -> pertahankan existing,
                        user baru tanpa existing -> default.

Jalankan:
    docker exec bbm_web python3 -m pytest tests/test_user_pin_protection.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.helpers import resolve_user_pin, finalize_pin


class TestResolveUserPin:
    """Kebijakan update PIN pada /api/users/sync (helper keputusan)."""

    def test_pin_eksplisit_mengganti_pin_lama(self):
        """Admin mengirim PIN baru -> nilai PIN dikembalikan (update kredensial diizinkan)."""
        assert resolve_user_pin('111222') == '111222'
        assert resolve_user_pin('000000') == '000000'

    def test_pin_tidak_dikirim_berarti_tidak_mengubah(self):
        """Toggle aktif/nonaktif atau hapus (tanpa field pin) -> None (jangan ubah PIN)."""
        assert resolve_user_pin(None) is None
        assert resolve_user_pin('') is None
        assert resolve_user_pin('   ') is None

    def test_pin_baru_di_strip(self):
        """Whitespace di sekitar PIN dirapikan."""
        assert resolve_user_pin(' 123456 ') == '123456'


class TestFinalizePin:
    """Fallback level-route: None -> pertahankan existing / default utk user baru."""

    def test_pin_baru_dipakai_langsung(self):
        assert finalize_pin('777333', existing_pin='555111') == '777333'

    def test_tanpa_pin_mempertahankan_existing(self):
        """Toggle nonaktif (pin None) -> PIN existing dipertahankan."""
        assert finalize_pin(None, existing_pin='555111') == '555111'

    def test_user_baru_tanpa_pin_mendapat_default(self):
        """User baru (row tidak ada -> existing None) tanpa pin -> default '123456'."""
        assert finalize_pin(None, existing_pin=None) == '123456'

    def test_alur_lengkap_toggle(self):
        """Simulasi route: create user pin 777333, lalu toggle tanpa pin."""
        # create
        pin_new = finalize_pin(resolve_user_pin('777333'), existing_pin=None)
        assert pin_new == '777333'
        # toggle tanpa pin -> None -> pertahankan pin yang ada (dari DB)
        pin_after = finalize_pin(resolve_user_pin(None), existing_pin=pin_new)
        assert pin_after == '777333'
