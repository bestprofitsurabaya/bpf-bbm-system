#!/usr/bin/env bash
# ============================================================
# Buat video walkthrough per peran dari screenshot berkala
# (dari frontend/scripts/record.mjs) + efek zoom Ken Burns.
# Jalankan: bash scripts/make_videos.sh
# ============================================================
set -euo pipefail
SRC=/tmp/record
DEST=presentasi/videos
mkdir -p "$DEST"
FPS=30
PER_SHOT=2.5   # durasi tiap screenshot (detik)

for role in admin ob finance ga marketing chief driver; do
  dir="$SRC/$role"
  [ -d "$dir" ] || { echo "skip $role (tidak ada screenshot)"; continue; }
  n=$(ls "$dir" 2>/dev/null | wc -l)
  [ "$n" -gt 1 ] || { echo "skip $role (hanya $n shot)"; continue; }

  # Bangun filter zoompan: zoom pelan masuk, ganti setiap PER_SHOT detik
  frames=$(awk "BEGIN{print int($PER_SHOT*$FPS)}")
  total=$(awk "BEGIN{print $n*$PER_SHOT}")
  zoom="zoompan=z='min(zoom+0.0006,1.12)':d=${frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1440x900:fps=${FPS}"

  echo "🎞️ $role: $n shot → $role.mp4 (${total}s)"
  ffmpeg -y -loglevel error -framerate "$FPS" \
    -pattern_type glob -i "$dir/s*.png" \
    -vf "$zoom,format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 25 -pix_fmt yuv420p -movflags +faststart \
    "$DEST/$role.mp4"
done

# Video gabungan semua peran
LIST=""
for role in admin ob finance ga marketing chief driver; do
  [ -f "$DEST/$role.mp4" ] && LIST="$LIST -i $DEST/$role.mp4"
done
if [ -n "$LIST" ]; then
  echo "🎞️ gabungan → walkthrough-all.mp4"
  ffmpeg -y -loglevel error $LIST \
    -filter_complex "concat=n=7:v=1:a=0" -c:v libx264 -preset veryfast -crf 25 \
    -pix_fmt yuv420p -movflags +faststart "$DEST/walkthrough-all.mp4"
fi

echo "✅ video siap di $DEST"
ls -lh "$DEST"/*.mp4 2>/dev/null
