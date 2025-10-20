#!/bin/bash
#
# Kiwi_AI Health Check Script
# Monitors container health and alerts on failures
#
# Usage:
#   ./health_check.sh
#
# Cron (check every 5 minutes):
#   */5 * * * * /path/to/Kiwi_AI/scripts/health_check.sh

set -e

# Configuration
CONTAINER_NAME="kiwi-ai-trading"
LOG_FILE="/var/log/kiwi-ai-health.log"
ALERT_EMAIL="your-email@example.com"  # Set your email for alerts
MAX_RESTART_ATTEMPTS=3

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "${RED}ERROR: Container ${CONTAINER_NAME} not found${NC}"
    exit 1
fi

# Check container status
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME")
CONTAINER_HEALTH=$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "none")

log "Container Status: $CONTAINER_STATUS | Health: $CONTAINER_HEALTH"

# Check if container is running
if [ "$CONTAINER_STATUS" != "running" ]; then
    log "${RED}WARNING: Container is not running. Attempting restart...${NC}"
    
    # Attempt restart
    docker start "$CONTAINER_NAME"
    sleep 10
    
    # Verify restart
    NEW_STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME")
    if [ "$NEW_STATUS" == "running" ]; then
        log "${GREEN}SUCCESS: Container restarted successfully${NC}"
    else
        log "${RED}ERROR: Failed to restart container${NC}"
        # Send alert (if mail is configured)
        # echo "Kiwi_AI container failed to restart" | mail -s "ALERT: Kiwi_AI Down" "$ALERT_EMAIL"
        exit 1
    fi
fi

# Check health status
if [ "$CONTAINER_HEALTH" == "unhealthy" ]; then
    log "${YELLOW}WARNING: Container health check failed${NC}"
    
    # Get container logs
    log "Recent container logs:"
    docker logs --tail 50 "$CONTAINER_NAME" >> "$LOG_FILE"
    
    # Send alert
    # echo "Kiwi_AI container is unhealthy" | mail -s "ALERT: Kiwi_AI Health Check Failed" "$ALERT_EMAIL"
fi

# Check memory usage
MEM_USAGE=$(docker stats --no-stream --format "{{.MemPerc}}" "$CONTAINER_NAME" | sed 's/%//')
MEM_THRESHOLD=85

if (( $(echo "$MEM_USAGE > $MEM_THRESHOLD" | bc -l) )); then
    log "${YELLOW}WARNING: High memory usage: ${MEM_USAGE}%${NC}"
fi

# Check CPU usage
CPU_USAGE=$(docker stats --no-stream --format "{{.CPUPerc}}" "$CONTAINER_NAME" | sed 's/%//')
CPU_THRESHOLD=90

if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    log "${YELLOW}WARNING: High CPU usage: ${CPU_USAGE}%${NC}"
fi

# Check disk space
DISK_USAGE=$(df -h /home/ubuntu/Kiwi_AI | tail -1 | awk '{print $5}' | sed 's/%//')
DISK_THRESHOLD=85

if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    log "${YELLOW}WARNING: High disk usage: ${DISK_USAGE}%${NC}"
fi

# Check log file sizes
LOG_DIR="/home/ubuntu/Kiwi_AI/logs"
if [ -d "$LOG_DIR" ]; then
    LARGE_LOGS=$(find "$LOG_DIR" -type f -size +100M)
    if [ -n "$LARGE_LOGS" ]; then
        log "${YELLOW}WARNING: Large log files detected:${NC}"
        echo "$LARGE_LOGS" | tee -a "$LOG_FILE"
    fi
fi

log "${GREEN}Health check completed${NC}"
exit 0
