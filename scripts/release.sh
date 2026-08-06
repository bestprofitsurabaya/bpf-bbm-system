#!/usr/bin/env bash
# ============================================================
# BPF Fleet & BBM System — GitHub Release Creator
# ------------------------------------------------------------
# Cara pakai:
#   1) Install gh CLI  ->  https://cli.github.com
#      lalu: gh auth login
#      lalu jalankan:  bash scripts/release.sh v1.1.0 "Judul Rilis"
#   2) ATAU pakai token GitHub (repo PAT dengan scope repo):
#      GITHUB_TOKEN=ghp_xxx bash scripts/release.sh v1.1.0 "Judul Rilis"
#
# Membuat tag + GitHub Release dari isi CHANGELOG.md (bagian [x.y.z]).
# ============================================================
set -euo pipefail

TAG="${1:-}"
TITLE="${2:-}"
REPO="bestprofitsurabaya/bpf-bbm-system"
CHANGELOG="CHANGELOG.md"

if [ -z "$TAG" ]; then
    echo "Usage: $0 <tag> [title]" >&2
    echo "Example: $0 v1.1.0 \"Rilis v1.1.0\"" >&2
    exit 1
fi

# Ambil isi changelog untuk versi ini (dari [x.y.z] sampai versi berikutnya / EOF)
BODY="$(awk -v t="$TAG" '
    BEGIN { in_section = 0 }
    $0 ~ "^## \\[" { if (in_section) exit; if ($0 ~ t) in_section = 1; next }
    in_section { print }
' "$CHANGELOG")"

if [ -z "$BODY" ]; then
    echo "Tidak menemukan section \"## [$TAG]\" di $CHANGELOG" >&2
    exit 1
fi

echo "=== Membuat tag $TAG ==="
git tag -a "$TAG" -m "$TITLE" 2>/dev/null || { echo "Tag $TAG sudah ada, lanjut..."; }
git push origin "$TAG"

echo "=== Membuat GitHub Release $TAG ==="
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh release create "$TAG" --repo "$REPO" --title "$TITLE" --notes "$BODY"
else
    if [ -z "${GITHUB_TOKEN:-}" ]; then
        echo "gh CLI tidak terautentikasi dan GITHUB_TOKEN tidak diset." >&2
        echo "Lakukan: gh auth login   ATAU   GITHUB_TOKEN=... bash $0 $TAG" >&2
        exit 1
    fi
    # Fallback: GitHub REST API
    PAYLOAD="$(python3 -c "
import json, sys
print(json.dumps({
    'tag_name': '$TAG',
    'name': '$TITLE',
    'body': '''$BODY''',
    'draft': False,
    'prerelease': False,
}))")"
    curl -sS -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/$REPO/releases" \
        -d "$PAYLOAD"
fi

echo
echo "✅ Rilis $TAG berhasil dibuat."
