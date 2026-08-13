#!/usr/bin/env bash
# ============================================================
# Build SPA Vue 3 (Vite) lalu salin hasil ke static/app/
#
# Mengapa perlu: docker-compose.yml me-bind-mount ./static → /app/static
# di dalam container, sehingga hasil `COPY --from=frontend-build` di
# Dockerfile TERTIMPA oleh folder host. Untuk itu hasil build SPA harus
# ada di host `static/app/` (tidak di-commit — lihat .gitignore).
#
# Cara pakai:
#   bash scripts/build-spa.sh          # build + salin + info
#   bash scripts/build-spa.sh --skip-npm  # hanya salin ulang (dist sudah ada)
# ============================================================
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT=$(pwd)

if [[ "${1:-}" != "--skip-npm" ]]; then
  echo "▶ Build SPA (npm run build) ..."
  (cd frontend && npm install --no-audit --no-fund && npm run build)
else
  echo "▶ Skip npm build (pakai frontend/dist yang sudah ada)"
fi

echo "▶ Salin frontend/dist → static/app ..."
rm -rf static/app
cp -r frontend/dist static/app
# Script anti-flash dark-mode (di-<script src> index.html, bukan inline agar
# Content-Security-Policy tetap ketat: script-src 'self')
if [[ -f frontend/public/dark-init.js ]]; then
  cp frontend/public/dark-init.js static/app/dark-init.js
fi

echo "✅ Selesai. SPA tersedia di static/app:"
ls -la static/app
echo
echo "> Reload container? Tidak perlu — bind-mount ./static sudah memuat otomatis."
echo "> Verifikasi: curl -sk http://localhost:5001/app/ | head"
