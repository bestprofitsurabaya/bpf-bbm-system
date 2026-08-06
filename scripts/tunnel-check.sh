#!/usr/bin/env bash
# ============================================================
# BPF Fleet & BBM System — Periksa Status URL Public (Tunnel)
# ------------------------------------------------------------
# Memeriksa apakah Cloudflare Tunnel masih hidup dan aplikasi
# dapat diakses publik. Menampilkan URL aktif + hasil health check.
#
# Pakai:
#   bash scripts/tunnel-check.sh            # cek sekali
#   bash scripts/tunnel-check.sh --watch    # pantau tiap 10 detik
#   bash scripts/tunnel-check.sh --quiet    # hanya output status (0/1)
#
# Exit code: 0 = online, 1 = offline/tidak ditemukan.
# ============================================================
set -uo pipefail

WATCH=0
QUIET=0
for arg in "$@"; do
    case "$arg" in
        --watch)  WATCH=1 ;;
        --quiet)  QUIET=1 ;;
        *)        echo "Argumen tidak dikenal: $arg" >&2; exit 2 ;;
    esac
done

# --- Ambil URL aktif dari log container cloudflared -----------------
get_url() {
    docker logs bbm_cloudflared 2>&1 \
        | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' \
        | tail -1
}

# --- Cek kesehatan satu kali -----------------------------------------
check_once() {
    local URL
    URL=$(get_url)

    if [ -z "$URL" ]; then
        if [ "$QUIET" = "1" ]; then
            echo "OFFLINE"
        else
            echo "❌ Tunnel tidak ditemukan."
            echo "   Pastikan container cloudflared berjalan:"
            echo "   docker compose up -d cloudflared"
        fi
        return 1
    fi

    local CODE_LOGIN CODE_DRIVER
    CODE_LOGIN=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$URL/login" 2>/dev/null || echo 000)
    CODE_DRIVER=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$URL/driver" 2>/dev/null || echo 000)

    if [ "$CODE_LOGIN" = "200" ] && [ "$CODE_DRIVER" = "200" ]; then
        if [ "$QUIET" = "1" ]; then
            echo "ONLINE $URL"
        else
            echo "✅ APLIKASI ONLINE"
            echo "   URL public : $URL"
            echo "   Driver PWA : $URL/driver"
            echo "   Login admin: $URL/login"
        fi
        return 0
    else
        if [ "$QUIET" = "1" ]; then
            echo "DEGRADED $URL (login=$CODE_LOGIN driver=$CODE_DRIVER)"
        else
            echo "⚠️  Tunnel aktif tapi aplikasi merespons tidak normal:"
            echo "   URL public : $URL"
            echo "   /login -> $CODE_LOGIN   /driver -> $CODE_DRIVER"
            echo "   (000 = tidak terhubung; 500 = error server; 502/504 = tunnel proxy bermasalah)"
        fi
        return 1
    fi
}

# --- Mode watch ------------------------------------------------------
if [ "$WATCH" = "1" ]; then
    echo "🔍 Memantau tunnel setiap 10 detik (Ctrl+C untuk berhenti)..."
    while true; do
        TS=$(date '+%H:%M:%S')
        if check_once "$@" >/dev/null 2>&1; then
            URL=$(get_url)
            echo "[$TS] ✅ ONLINE  $URL"
        else
            echo "[$TS] ❌ OFFLINE"
        fi
        sleep 10
    done
fi

# --- Mode sekali -----------------------------------------------------
check_once
exit $?
