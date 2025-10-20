#!/bin/bash
#
# Kiwi_AI Backup Script
# Creates compressed backups of critical data
#
# Usage:
#   ./backup.sh
#
# Cron (daily at 3 AM):
#   0 3 * * * /path/to/Kiwi_AI/scripts/backup.sh

set -e

# Configuration
BACKUP_BASE="/home/ubuntu/kiwi-ai-backups"
PROJECT_DIR="/home/ubuntu/Kiwi_AI"
DATE_SUFFIX=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=14

# Create backup directory
mkdir -p "$BACKUP_BASE"

echo "[$(date)] Starting backup..."

# Backup models
echo "Backing up models..."
tar -czf "${BACKUP_BASE}/models_${DATE_SUFFIX}.tar.gz" \
    -C "$PROJECT_DIR" models/ 2>/dev/null || true

# Backup logs (last 7 days)
echo "Backing up recent logs..."
find "$PROJECT_DIR/logs" -type f -mtime -7 | \
    tar -czf "${BACKUP_BASE}/logs_${DATE_SUFFIX}.tar.gz" \
    -T - 2>/dev/null || true

# Backup configuration
echo "Backing up configuration..."
tar -czf "${BACKUP_BASE}/config_${DATE_SUFFIX}.tar.gz" \
    -C "$PROJECT_DIR" \
    .env config.py docker-compose.yml 2>/dev/null || true

# Backup backtest reports (last 30 days)
echo "Backing up recent backtest reports..."
find "$PROJECT_DIR/backtest_reports" -type f -mtime -30 | \
    tar -czf "${BACKUP_BASE}/reports_${DATE_SUFFIX}.tar.gz" \
    -T - 2>/dev/null || true

# Create full backup
echo "Creating full backup..."
tar -czf "${BACKUP_BASE}/full_backup_${DATE_SUFFIX}.tar.gz" \
    --exclude='market_data' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    -C "$(dirname $PROJECT_DIR)" \
    "$(basename $PROJECT_DIR)" 2>/dev/null || true

# Remove old backups
echo "Cleaning old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_BASE" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

# Calculate backup size
TOTAL_SIZE=$(du -sh "$BACKUP_BASE" | cut -f1)
echo "Total backup size: $TOTAL_SIZE"

# List recent backups
echo "Recent backups:"
ls -lht "$BACKUP_BASE"/*.tar.gz 2>/dev/null | head -10 || echo "No backups found"

echo "[$(date)] Backup completed successfully"
exit 0
