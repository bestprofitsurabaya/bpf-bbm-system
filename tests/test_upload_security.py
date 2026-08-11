"""
Unit Tests — Keamanan Upload File (save_file hardening)
BPF BBM System v2.2.3

Menjamin perbaikan celah path traversal & stored XSS:
- Path traversal (../, /) dinormalisasi via secure_filename.
- Ekstensi di-whitelist (gambar & PDF) — .html/.svg/.exe/.py DITOLAK.
- Nama file dibangkitkan server-side (nama asli user tidak dipakai).

Jalankan:
    docker exec bbm_web python3 -m pytest tests/test_upload_security.py -v
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.helpers import save_file, ALLOWED_UPLOAD_EXT


class FakeFile:
    """Tiruan werkzeug FileStorage minimal (filename + save)."""

    def __init__(self, name):
        self.filename = name

    def save(self, path):
        with open(path, 'wb') as f:
            f.write(b'x')


class TestAllowedExt:
    def test_whitelist_hanya_gambar_dan_pdf(self):
        assert ALLOWED_UPLOAD_EXT == {'png', 'jpg', 'jpeg', 'webp', 'gif', 'pdf'}


class TestSaveFileRejectsDangerous:
    def test_path_traversal_dinetralkan(self):
        """../ dihapus secure_filename — file aman tersimpan di dalam folder upload."""
        with tempfile.TemporaryDirectory() as d:
            name = save_file(FakeFile('../../etc/passwd.jpg'), 'ODO1', 'L1', d)
            assert name is not None
            assert '../' not in name
            saved = os.path.join(d, name)
            assert os.path.dirname(saved) == d  # tidak keluar dari folder upload
            assert os.path.isfile(saved)

    def test_tolak_traversal_dengan_ekstensi_berbahaya(self):
        with tempfile.TemporaryDirectory() as d:
            assert save_file(FakeFile('../../etc/passwd.html'), 'ODO1', 'L1', d) is None

    def test_tolak_ekstensi_berbahaya(self):
        with tempfile.TemporaryDirectory() as d:
            for bad in ('x.html', 'x.svg', 'x.exe', 'x.php', 'x.py', 'x.js', 'x.sh'):
                assert save_file(FakeFile(bad), 'ODO1', 'L1', d) is None, f'{bad} harus ditolak'

    def test_tolak_tanpa_ekstensi(self):
        with tempfile.TemporaryDirectory() as d:
            assert save_file(FakeFile('nothing'), 'ODO1', 'L1', d) is None

    def test_tolak_nama_kosong(self):
        with tempfile.TemporaryDirectory() as d:
            assert save_file(FakeFile(''), 'ODO1', 'L1', d) is None
            assert save_file(None, 'ODO1', 'L1', d) is None


class TestSaveFileAcceptsSafe:
    def test_terima_gambar_dengan_nama_aman(self):
        with tempfile.TemporaryDirectory() as d:
            name = save_file(FakeFile('foto_bukti.jpg'), 'ODO1', 'L 1 AB', d)
            assert name is not None
            assert name.startswith('ODO1_L_1_AB_')
            assert name.endswith('.jpg')
            # Nama asli user tidak dipakai (anti path traversal & anti tabrakan)
            assert 'foto_bukti' not in name
            assert '..' not in name and not name.startswith('/')
            assert os.path.isfile(os.path.join(d, name))

    def test_terima_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            name = save_file(FakeFile('nota.pdf'), 'STRUK', 'L2', d)
            assert name is not None and name.endswith('.pdf')

    def test_nama_nopol_juga_dinormalisasi(self):
        with tempfile.TemporaryDirectory() as d:
            name = save_file(FakeFile('x.png'), 'DISP', '../EVIL', d)
            assert name is not None
            assert '../' not in name
