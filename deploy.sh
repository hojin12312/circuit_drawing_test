#!/usr/bin/env bash
# deploy.sh — Generate SVG, build index.html, commit, push
set -euo pipefail

echo "=== Generating SVG schematics ==="
python3 inverter.py

echo ""
echo "=== Building index.html with current hash ==="
python3 build.py

echo ""
echo "=== Staging all files ==="
git add -A

if git diff --cached --quiet; then
    echo "Nothing to commit."
else
    echo ""
    echo "=== First commit (code + assets, hash may be stale) ==="
    git commit -m "$1"
fi

echo ""
echo "=== Updating hash to match actual commit ==="
python3 build.py
git add index.html

if git diff --cached --quiet; then
    echo "Hash already current."
else
    echo ""
    echo "=== Second commit (hash correction) ==="
    git commit -m "Update index.html hash after commit"
fi

echo ""
echo "=== Pushing to GitHub ==="
git push

echo ""
echo "=== Latest hash ==="
git rev-parse --short HEAD
