#!/bin/bash
#
# Kiwi_AI Model Retraining Script
# Automatically retrains ML models with recent market data
#
# Usage:
#   ./retrain_models.sh [symbols]
#
# Example:
#   ./retrain_models.sh AAPL MSFT GOOGL
#
# Cron (weekly on Sunday at 2 AM):
#   0 2 * * 0 /path/to/Kiwi_AI/scripts/retrain_models.sh AAPL MSFT GOOGL AMZN TSLA

set -e

# Configuration
CONTAINER_NAME="kiwi-ai-trading"
BACKUP_DIR="/home/ubuntu/Kiwi_AI/models/backups"
DATE_SUFFIX=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/home/ubuntu/Kiwi_AI/logs/retrain_${DATE_SUFFIX}.log"

# Default symbols if none provided
DEFAULT_SYMBOLS="AAPL MSFT GOOGL AMZN TSLA"
SYMBOLS="${@:-$DEFAULT_SYMBOLS}"

echo "[$(date)] Starting model retraining..." | tee -a "$LOG_FILE"
echo "Symbols: $SYMBOLS" | tee -a "$LOG_FILE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup existing models
echo "[$(date)] Backing up existing models..." | tee -a "$LOG_FILE"
if [ -d "/home/ubuntu/Kiwi_AI/models" ]; then
    tar -czf "${BACKUP_DIR}/models_backup_${DATE_SUFFIX}.tar.gz" \
        -C /home/ubuntu/Kiwi_AI models/ 2>/dev/null || true
    echo "Backup saved to: ${BACKUP_DIR}/models_backup_${DATE_SUFFIX}.tar.gz" | tee -a "$LOG_FILE"
fi

# Stop container (optional, for safety)
# echo "[$(date)] Stopping container..." | tee -a "$LOG_FILE"
# docker stop "$CONTAINER_NAME"

# Retrain models
echo "[$(date)] Retraining models..." | tee -a "$LOG_FILE"
docker exec -i "$CONTAINER_NAME" python train_models.py \
    --mode all \
    --symbols $SYMBOLS 2>&1 | tee -a "$LOG_FILE"

RETRAIN_STATUS=$?

if [ $RETRAIN_STATUS -eq 0 ]; then
    echo "[$(date)] Model retraining completed successfully" | tee -a "$LOG_FILE"
    
    # Remove old backups (keep last 5)
    echo "[$(date)] Cleaning old backups..." | tee -a "$LOG_FILE"
    ls -t "${BACKUP_DIR}"/models_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f || true
    
else
    echo "[$(date)] ERROR: Model retraining failed!" | tee -a "$LOG_FILE"
    
    # Restore from backup
    echo "[$(date)] Restoring models from backup..." | tee -a "$LOG_FILE"
    tar -xzf "${BACKUP_DIR}/models_backup_${DATE_SUFFIX}.tar.gz" \
        -C /home/ubuntu/Kiwi_AI || true
    
    exit 1
fi

# Restart container to load new models
echo "[$(date)] Restarting container..." | tee -a "$LOG_FILE"
docker restart "$CONTAINER_NAME"

echo "[$(date)] Retraining process completed" | tee -a "$LOG_FILE"
exit 0
