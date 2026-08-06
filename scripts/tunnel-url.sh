#!/usr/bin/env bash
# ============================================================
# BPF Fleet & BBM System — Tampilkan URL public Cloudflare Tunnel
# ------------------------------------------------------------
# Quick tunnel (trycloudflare) menghasilkan URL acak yang bisa
# berubah tiap kali container cloudflared di-restart.
# Script ini menampilkan URL yang sedang aktif.
#
# Pakai:  bash scripts/tunnel-url.sh
# ============================================================
set -uo pipefail

URL=$(docker logs bbm_cloudflared 2>&1 | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | tail -1)

if [ -z "$URL" ]; then
    echo "⚠️  Belum menemukan URL tunnel." >&2
    echo "Pastikan container cloudflared berjalan:" >&2
    echo "  docker compose up -d cloudflared" >&2
    exit 1
fi

echo "🌐 URL public aplikasi:"
echo "   $URL"
echo
echo "Driver PWA : $URL/driver"
echo "Login admin: $URL/login"
echo
echo "⚠️  Catatan: URL quick tunnel berubah saat container di-restart."
echo "   Untuk URL permanen, gunakan named tunnel + domain (lihat DEPLOYMENT.md)."
