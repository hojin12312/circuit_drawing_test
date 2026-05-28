"""build.py — Generate index.html with current commit hash."""
import subprocess, os
from string import Template

HASH = subprocess.run(
    ["git", "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True, check=True
).stdout.strip()

os.makedirs("output", exist_ok=True)

with open("index.html") as f:
    html = f.read()

# Replace only the commit hash placeholder
html = html.replace("$COMMIT_HASH", HASH)

with open("index.html", "w") as f:
    f.write(html)

print(f"index.html updated — commit {HASH}")
