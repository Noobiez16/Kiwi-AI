#!/bin/bash
#
# Kiwi_AI Log Rotation Script
# Rotates and compresses old log files
#
# Usage:
#   ./rotate_logs.sh
#
# Cron (daily at 2 AM):
#   0 2 * * * /path/to/Kiwi_AI/scripts/rotate_logs.sh

set -e

# Configuration
LOG_DIR="/home/ubuntu/Kiwi_AI/logs"
ARCHIVE_DIR="${LOG_DIR}/archive"
RETENTION_DAYS=30
DATE_SUFFIX=$(date +%Y%m%d_%H%M%S)

# Create archive directory if it doesn't exist
mkdir -p "$ARCHIVE_DIR"

echo "[$(date)] Starting log rotation..."

# Find log files older than 1 day
find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f -mtime +1 | while read -r logfile; do
    if [ -f "$logfile" ]; then
        filename=$(basename "$logfile")
        
        # Compress and move to archive
        echo "Archiving: $filename"
        gzip -c "$logfile" > "${ARCHIVE_DIR}/${filename%.log}_${DATE_SUFFIX}.log.gz"
        
        # Truncate original log file
        > "$logfile"
    fi
done

# Remove archives older than retention period
echo "Removing archives older than $RETENTION_DAYS days..."
find "$ARCHIVE_DIR" -name "*.log.gz" -type f -mtime +$RETENTION_DAYS -delete

# Calculate space saved
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | cut -f1 || echo "0")
echo "Archive directory size: $ARCHIVE_SIZE"

echo "[$(date)] Log rotation completed"
exit 0
