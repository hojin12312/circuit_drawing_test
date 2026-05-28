"""build.py — Generate index.html with current commit hash.

Usage: python3 build.py

Reads index_template.html, replaces __COMMIT_HASH__ with the current
short git hash, and writes index.html.

Or, if index_template.html doesn't exist, reads index.html and updates
any existing 7-char hex hash in the commit link.
"""
import subprocess, os, re

HASH = subprocess.run(
    ["git", "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True, check=True
).stdout.strip()

os.makedirs("output", exist_ok=True)

TEMPLATE_FILE = "index_template.html"

if os.path.exists(TEMPLATE_FILE):
    with open(TEMPLATE_FILE) as f:
        html = f.read()
    html = html.replace("__COMMIT_HASH__", HASH)
    with open("index.html", "w") as f:
        f.write(html)
    print(f"index.html generated from template — commit {HASH}")
else:
    # Update existing index.html in-place
    with open("index.html") as f:
        html = f.read()
    html, n = re.subn(
        r'\b[a-f0-9]{7}\b',
        HASH,
        html
    )
    if n:
        with open("index.html", "w") as f:
            f.write(html)
        print(f"index.html hash updated — commit {HASH}")
    else:
        print(f"index.html unchanged (no hash to replace)")

