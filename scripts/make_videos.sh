#!/usr/bin/env bash
# ============================================================
# Buat video walkthrough per peran dari screenshot berkala
# (dari frontend/scripts/record.mjs) + efek zoom Ken Burns,
# kartu judul per peran, transisi fade, dan keterangan adegan.
#
# Jalankan: bash scripts/make_videos.sh
# Bahan:    /tmp/record/<role>/s*.png + captions.json
# Hasil:    presentasi/videos/<role>.mp4 + walkthrough-all.mp4
# ============================================================
set -euo pipefail
SRC=/tmp/record
DEST=presentasi/videos
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" # path relatif (DEST/WORK/SRC) aman dari mana pun script dipanggil
mkdir -p "$DEST" "$DEST/.work"
FPS=30
PER_SHOT=3.0     # durasi tiap adegan (detik)
TITLE_LEN=3.5    # durasi kartu judul (detik)
FADE=0.45        # durasi transisi fade (detik)
FONT_BOLD="$ROOT/fonts/DejaVuSans-Bold.ttf"
FONT_REG="$ROOT/fonts/DejaVuSans.ttf"
WORK="$DEST/.work"
WORK_ABS="$(cd "$WORK" && pwd)" # concat ffmpeg relatif ke lokasi file list → wajib absolut

[ -f "$FONT_BOLD" ] && [ -f "$FONT_REG" ] || { echo "❌ font DejaVu tidak ditemukan di ./fonts/"; exit 1; }
command -v ffmpeg >/dev/null || { echo "❌ ffmpeg tidak terinstal"; exit 1; }

# ---------- Badge logo bulat BPF (dibuat sekali via PIL) ----------
make_logo() {
  python3 - "$WORK_ABS/logo-round.png" <<'PY'
import sys
from PIL import Image, ImageDraw
out = sys.argv[1]
logo = Image.open('static/icon-192.png').convert('RGBA')
size = 200
canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
# lingkaran putih (badge) + cincin biru khas BPF
mask = Image.new('L', (size, size), 0)
ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
inner = Image.new('RGBA', (size, size), (255, 255, 255, 255))
canvas.paste(inner, (0, 0), mask)
lg = logo.resize((172, 172), Image.LANCZOS)
canvas.paste(lg, ((size - 172) // 2, (size - 172) // 2), mask.resize((172, 172)))
ImageDraw.Draw(canvas).ellipse((2, 2, size - 3, size - 3), outline=(37, 99, 235, 255), width=6)
canvas.save(out)
print('logo badge:', out)
PY
}

# ---------- Kartu judul peran (gradien + badge logo + teks) ----------
# $1 = output file  $2 = judul  $3 = subtitle
title_card() {
  local out="$1" title="$2" subtitle="$3"
  ffmpeg -y -loglevel error \
    -f lavfi -i "gradients=s=1440x900:c0=0x0b1220:c1=0x1d4ed8:x0=0:y0=0:x1=0:y1=900:r=${FPS}:d=${TITLE_LEN}" \
    -i "$WORK_ABS/logo-round.png" \
    -filter_complex "\
[1:v]format=rgba[logo];\
[0:v][logo]overlay=x=(W-w)/2:y=120,\
drawbox=x=0:y=0:w=1440:h=14:color=0x3b82f6:t=fill,\
drawbox=x=0:y=886:w=1440:h=14:color=0x1d4ed8:t=fill,\
drawtext=fontfile=${FONT_BOLD}:text='BPF FLEET & BBM SYSTEM':fontsize=24:fontcolor=0x93c5fd:x=(w-text_w)/2:y=390,\
drawtext=fontfile=${FONT_BOLD}:text='Walkthrough ${title}':fontsize=62:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+90,\
drawtext=fontfile=${FONT_REG}:text='${subtitle}':fontsize=26:fontcolor=0xcbd5e1:x=(w-text_w)/2:y=(h)/2+190,\
fade=t=in:st=0:d=${FADE},fade=t=out:st=$(awk "BEGIN{print $TITLE_LEN-$FADE}"):d=${FADE}" \
    -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p -r "$FPS" "$out"
}

# ---------- Segmen adegan: zoom + caption + fade ----------
# $1 = gambar  $2 = file caption  $3 = durasi  $4 = output
segment() {
  local src_img="$1" cap_file="$2" seg_dur="$3" seg_out="$4"
  ffmpeg -y -loglevel error -loop 1 -framerate "$FPS" -t "$seg_dur" -i "$src_img" \
    -vf "\
zoompan=z='min(zoom+0.0008,1.16)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1440x900:fps=${FPS},\
drawtext=fontfile=${FONT_BOLD}:textfile=${cap_file}:fontsize=27:fontcolor=white:\
box=1:boxcolor=black@0.55:boxborderw=16:x=56:y=h-96,\
fade=t=in:st=0:d=${FADE},fade=t=out:st=$(awk "BEGIN{print $seg_dur-$FADE}"):d=${FADE}" \
    -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p -r "$FPS" "$seg_out"
}

# ---------- Persiapan caption: baca captions.json, buang emoji ----------
# $1 = role → menulis $WORK/<role>/*.txt + daftar segmen
prep_captions() {
  local role="$1"
  python3 - "$role" <<'PY'
import json, sys, re
role = sys.argv[1]
with open(f'/tmp/record/{role}/captions.json') as f:
    meta = json.load(f)
strip = re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2190-\u21FF]')
def clean(s): return strip.sub('', s).strip()
paths = []
for sc in meta['scenes']:
    txt = clean(sc['caption'])
    capfile = f"presentasi/videos/.work/{role}-{sc['file']}.txt"
    with open(capfile, 'w') as cf:
        cf.write(txt)
    paths.append({'img': f"/tmp/record/{role}/{sc['file']}", 'cap': capfile})
with open(f"presentasi/videos/.work/{role}-list.json", 'w') as f:
    json.dump({'title': clean(meta['title']), 'subtitle': clean(meta['subtitle']), 'paths': paths}, f)
PY
}

# ---------- Bangun satu role ----------
build_role() {
  local role="$1"
  local dir="$SRC/$role"
  [ -d "$dir" ] || { echo "skip $role (tidak ada screenshot)"; return; }
  local n; n=$(ls "$dir"/s*.png 2>/dev/null | wc -l)
  [ "$n" -gt 0 ] || { echo "skip $role (tanpa shot)"; return; }

  echo "🎞️ $role: $n adegan → $role.mp4"
  prep_captions "$role"

  title=$(python3 -c "import json;print(json.load(open('$WORK/$role-list.json'))['title'])")
  subtitle=$(python3 -c "import json;print(json.load(open('$WORK/$role-list.json'))['subtitle'])")

  local list="$WORK/$role.conc.txt"; : > "$list"
  # 1. kartu judul (path absolut — concat relatif ke lokasi file list)
  title_card "$WORK_ABS/$role-00-title.mp4" "$title" "$subtitle"
  echo "file '$WORK_ABS/$role-00-title.mp4'" >> "$list"
  # 2. adegan (glob langsung — andal & urut)
  local i=0
  for src_img in "$dir"/s*.png; do
    [ -f "$src_img" ] || continue
    i=$((i+1))
    capfile="$WORK_ABS/$role-$(basename "$src_img").txt"
    seg="$WORK_ABS/$role-$(printf '%02d' "$i")-seg.mp4"
    segment "$src_img" "$capfile" "$PER_SHOT" "$seg"
    echo "file '$seg'" >> "$list"
  done

  ffmpeg -y -loglevel error -f concat -safe 0 -i "$list" -c copy "$DEST/$role.mp4"
}

# ============================================================
# MAIN
# ============================================================
make_logo

for role in admin ob finance ga marketing chief driver; do
  build_role "$role"
done

# ---------- Video gabungan: intro + semua role + outro ----------
LIST_ALL="$WORK/all.conc.txt"; : > "$LIST_ALL"
echo "🎞️ gabungan → walkthrough-all.mp4"

# Intro global
title_card "$WORK_ABS/00-intro.mp4" "Lengkap — 7 Peran" "Satu aplikasi untuk seluruh operasi BPF"
echo "file '$WORK_ABS/00-intro.mp4'" >> "$LIST_ALL"

for role in admin ob finance ga marketing chief driver; do
  [ -f "$DEST/$role.mp4" ] && echo "file '$PWD/$DEST/$role.mp4'" >> "$LIST_ALL"
done

# Outro
title_card "$WORK_ABS/99-outro.mp4" "Terima Kasih" "BPF Fleet & BBM System — PT Bestprofit Futures Surabaya"
echo "file '$WORK_ABS/99-outro.mp4'" >> "$LIST_ALL"

ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST_ALL" -c copy "$DEST/walkthrough-all.mp4"

# ---------- Bersihkan kerja sementara ----------
rm -rf "$WORK"

echo "✅ video siap di $DEST"
ls -lh "$DEST"/*.mp4 2>/dev/null
