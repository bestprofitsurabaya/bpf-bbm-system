"""Audit SQL injection — temukan cursor.execute/conn.execute yang menginterpolasi
variabel ke dalam string SQL (f-string berisi {}, %(), .format()) yang berpotensi
berasal dari input user.

Cara pakai: python3 scripts/audit_sql.py
"""
import re
import glob

# cari pemanggilan execute yang argumen pertamanya adalah string literal
# (bukan variabel) — lalu cek apakah string itu mengandung interpolasi.
EXEC = re.compile(r'(?:cursor|conn)\.execute\(\s*([fF]?)([\'"])(.*?)\2\s*(?:,|\))', re.S)
INTERP = re.compile(r'\{[^}]*\}|%\(|\.format\(')

issues = []
for f in sorted(glob.glob('modules/*.py')):
    src = open(f, encoding='utf-8').read()
    for m in EXEC.finditer(src):
        is_f, sql = m.group(1), m.group(3)
        if INTERP.search(sql):
            line = src[:m.start()].count('\n') + 1
            snippet = sql[:90].replace('\n', ' ')
            issues.append(f'{f}:{line}: {"F-STRING" if is_f else "interpolasi"} :: {snippet}')

if issues:
    print('=== POTENSI CELAH (periksa manual — pastikan hanya fragment statis) ===')
    for i in issues:
        print(' -', i)
else:
    print('TIDAK ADA query interpolasi berbahaya yang terdeteksi')

# Daftar semua execute f-string untuk review cepat
print()
print('=== SEMUA execute f-string (review) ===')
for f in sorted(glob.glob('modules/*.py')):
    src = open(f, encoding='utf-8').read()
    for m in EXEC.finditer(src):
        if m.group(1):  # f-string
            line = src[:m.start()].count('\n') + 1
            print(f' {f}:{line}: {m.group(3)[:80].replace(chr(10), " ")}')
