#!/bin/bash
#
# Kiwi_AI Monitoring Scripts
# 
# This directory contains operational scripts for maintaining Kiwi_AI in production.
#

## 📋 Available Scripts

### 1. health_check.sh
**Purpose**: Monitor container health and restart if needed

**Usage**:
```bash
./health_check.sh
```

**Cron Schedule** (every 5 minutes):
```bash
*/5 * * * * /home/ubuntu/Kiwi_AI/scripts/health_check.sh
```

**Features**:
- Container status monitoring
- Automatic restart on failure
- Memory/CPU usage alerts
- Disk space monitoring
- Log file size checks

---

### 2. rotate_logs.sh
**Purpose**: Rotate and compress old log files

**Usage**:
```bash
./rotate_logs.sh
```

**Cron Schedule** (daily at 2 AM):
```bash
0 2 * * * /home/ubuntu/Kiwi_AI/scripts/rotate_logs.sh
```

**Features**:
- Compresses logs older than 1 day
- Stores archives in `logs/archive/`
- Deletes archives older than 30 days
- Frees up disk space

---

### 3. retrain_models.sh
**Purpose**: Retrain ML models with fresh market data

**Usage**:
```bash
./retrain_models.sh [SYMBOLS...]

# Examples:
./retrain_models.sh AAPL MSFT GOOGL
./retrain_models.sh  # Uses default symbols
```

**Cron Schedule** (weekly on Sunday at 2 AM):
```bash
0 2 * * 0 /home/ubuntu/Kiwi_AI/scripts/retrain_models.sh AAPL MSFT GOOGL AMZN TSLA
```

**Features**:
- Backs up existing models
- Retrains all models (regime, performance)
- Restores backup on failure
- Restarts container with new models
- Keeps last 5 model backups

---

### 4. backup.sh
**Purpose**: Create compressed backups of critical data

**Usage**:
```bash
./backup.sh
```

**Cron Schedule** (daily at 3 AM):
```bash
0 3 * * * /home/ubuntu/Kiwi_AI/scripts/backup.sh
```

**Features**:
- Backs up models, logs, config, reports
- Creates full system backup
- Retains backups for 14 days
- Stores in `/home/ubuntu/kiwi-ai-backups/`

---

## 🚀 Setup Instructions

### 1. Make Scripts Executable
```bash
chmod +x scripts/*.sh
```

### 2. Install Cron Jobs
```bash
crontab -e
```

Add these lines:
```bash
# Kiwi_AI Maintenance Tasks
*/5 * * * * /home/ubuntu/Kiwi_AI/scripts/health_check.sh
0 2 * * * /home/ubuntu/Kiwi_AI/scripts/rotate_logs.sh
0 2 * * 0 /home/ubuntu/Kiwi_AI/scripts/retrain_models.sh AAPL MSFT GOOGL AMZN TSLA
0 3 * * * /home/ubuntu/Kiwi_AI/scripts/backup.sh
```

### 3. Test Scripts
```bash
# Test each script
./scripts/health_check.sh
./scripts/rotate_logs.sh
./scripts/retrain_models.sh AAPL
./scripts/backup.sh
```

---

## 📊 Monitoring

### View Health Check Logs
```bash
tail -f /var/log/kiwi-ai-health.log
```

### View Retrain Logs
```bash
ls -lht logs/retrain_*.log | head -5
tail -f logs/retrain_<date>.log
```

### View Backups
```bash
ls -lht /home/ubuntu/kiwi-ai-backups/
```

---

## 🔧 Customization

### Adjust Retention Periods

**Log Rotation** (`rotate_logs.sh`):
```bash
RETENTION_DAYS=30  # Change to desired days
```

**Backups** (`backup.sh`):
```bash
RETENTION_DAYS=14  # Change to desired days
```

### Modify Health Thresholds

**Memory** (`health_check.sh`):
```bash
MEM_THRESHOLD=85  # Alert at 85% memory usage
```

**CPU** (`health_check.sh`):
```bash
CPU_THRESHOLD=90  # Alert at 90% CPU usage
```

**Disk** (`health_check.sh`):
```bash
DISK_THRESHOLD=85  # Alert at 85% disk usage
```

---

## 📧 Email Alerts (Optional)

### Install mail utility
```bash
sudo apt install mailutils
```

### Configure email
Edit scripts and uncomment email lines:
```bash
ALERT_EMAIL="your-email@example.com"
echo "Alert message" | mail -s "Subject" "$ALERT_EMAIL"
```

---

## 🛠️ Troubleshooting

### Scripts not executing
```bash
# Check permissions
ls -l scripts/*.sh

# Make executable
chmod +x scripts/*.sh
```

### Cron not running
```bash
# Check cron service
sudo systemctl status cron

# View cron logs
grep CRON /var/log/syslog
```

### Path issues in cron
Add full paths to all commands in scripts:
```bash
/usr/bin/docker instead of docker
/usr/local/bin/docker-compose instead of docker-compose
```

---

## 📝 Best Practices

1. **Test before scheduling**: Run each script manually first
2. **Monitor logs**: Check script outputs regularly
3. **Adjust schedules**: Modify cron times based on your needs
4. **Keep backups**: Store critical backups offsite
5. **Review alerts**: Act on health check warnings promptly

---

**Ready for Production! 🚀**
