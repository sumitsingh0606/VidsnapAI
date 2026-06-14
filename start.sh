#!/bin/bash
set -e

# Ensure the virtualenv created during the install phase is on PATH,
# even if this shell doesn't source /root/.profile.
export PATH="/opt/venv/bin:$PATH"

# This script runs both the Flask web server and the background worker
# inside a SINGLE Railway service, sharing ONE persistent volume.
#
# The volume is mounted at /app/persistent (set this as the Mount Path
# in Railway's volume settings). We symlink the folders our code
# actually uses (user_uploads, static/reels) into that volume so
# everything survives restarts and redeploys.

PERSIST_DIR="/app/persistent"

mkdir -p "$PERSIST_DIR/user_uploads"
mkdir -p "$PERSIST_DIR/reels"

# Remove the default (empty/code-shipped) folders and replace with symlinks
rm -rf /app/user_uploads
ln -s "$PERSIST_DIR/user_uploads" /app/user_uploads

rm -rf /app/static/reels
ln -s "$PERSIST_DIR/reels" /app/static/reels

# Re-create done.txt tracking file on the volume if it doesn't exist
touch "$PERSIST_DIR/done.txt"
rm -f /app/done.txt
ln -s "$PERSIST_DIR/done.txt" /app/done.txt

echo "Persistent storage linked. Starting services..."

# Start the background worker (reel generation) in the background
python generate_process.py &

# Start the web server in the foreground (keeps the container alive)
exec gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
