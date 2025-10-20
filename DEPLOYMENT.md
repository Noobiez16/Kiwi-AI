# Kiwi_AI Deployment Guide

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Methods](#deployment-methods)
  - [Docker Compose (Recommended)](#docker-compose-recommended)
  - [Manual Deployment](#manual-deployment)
  - [Cloud Deployment (AWS EC2)](#cloud-deployment-aws-ec2)
- [Configuration](#configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 2GB, Recommended 4GB+
- **CPU**: 2+ cores recommended
- **Storage**: 10GB+ free space
- **Python**: 3.11+ (if not using Docker)

### Required Accounts
- **Alpaca Account**: Sign up at [alpaca.markets](https://alpaca.markets)
  - Paper trading: Free account
  - Live trading: Funded brokerage account

### Software Dependencies
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 1.29+ (for multi-container setup)
- **Git**: For cloning the repository

---

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/Noobiez16/Kiwi_AI.git
cd Kiwi_AI
```

### 2. Create Environment File
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Trading Mode: MOCK, PAPER, or LIVE
TRADING_MODE=PAPER

# Alpaca API Credentials
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Risk Management
RISK_PER_TRADE=0.02
MAX_PORTFOLIO_RISK=0.06
MAX_POSITION_SIZE=0.25

# Trading Symbols (comma-separated)
SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA
```

**⚠️ SECURITY WARNING**: Never commit `.env` to version control!

---

## Deployment Methods

### Docker Compose (Recommended)

#### Quick Start
```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f kiwi-ai

# Stop the container
docker-compose down
```

#### Production Deployment
```bash
# Build the image
docker-compose build

# Start in detached mode
docker-compose up -d

# Check status
docker-compose ps

# View real-time logs
docker-compose logs -f

# Restart container
docker-compose restart kiwi-ai

# Stop and remove containers
docker-compose down
```

#### Enable Dashboard (Optional)
Edit `docker-compose.yml` and uncomment the `dashboard` service:
```bash
docker-compose up -d dashboard
```
Access at: `http://localhost:8501`

---

### Manual Deployment

#### 1. Install Python Dependencies
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Train Models (First-time setup)
```bash
python train_models.py --mode all --symbols AAPL MSFT GOOGL
```

#### 3. Run Trading Bot
```bash
# Paper trading
export TRADING_MODE=PAPER
python main.py

# Live trading (BE CAREFUL!)
export TRADING_MODE=LIVE
python main.py
```

#### 4. Run Dashboard (Optional)
```bash
streamlit run dashboard.py
```

---

### Cloud Deployment (AWS EC2)

#### 1. Launch EC2 Instance
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM)
- **Storage**: 20GB GP3
- **Security Group**: 
  - SSH (22) - Your IP only
  - HTTP (80) - Optional for dashboard
  - HTTPS (443) - Optional for dashboard

#### 2. Connect and Setup
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply docker group
exit
# SSH back in
```

#### 3. Deploy Application
```bash
# Clone repository
git clone https://github.com/yourusername/Kiwi_AI.git
cd Kiwi_AI

# Create and configure .env
nano .env
# (Paste your configuration)

# Deploy with Docker Compose
docker-compose up -d

# Verify deployment
docker-compose logs -f
```

#### 4. Setup Systemd Service (Auto-start on boot)
See [Systemd Service Configuration](#systemd-service-configuration) below.

---

## Configuration

### Trading Modes

#### MOCK Mode (Testing)
- **Purpose**: Test strategy logic without real API calls
- **Data**: Simulated market data
- **Orders**: Fake execution
- **Use Case**: Development and debugging

```env
TRADING_MODE=MOCK
```

#### PAPER Mode (Recommended for Testing)
- **Purpose**: Test with real market data, simulated orders
- **Data**: Real-time from Alpaca
- **Orders**: Simulated (no real money)
- **Use Case**: Strategy validation

```env
TRADING_MODE=PAPER
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

#### LIVE Mode (Production)
- **Purpose**: Real trading with real money
- **Data**: Real-time market data
- **Orders**: Real executions
- **Use Case**: Production trading

```env
TRADING_MODE=LIVE
ALPACA_BASE_URL=https://api.alpaca.markets
```

**⚠️ WARNING**: Start with MOCK/PAPER mode. Test thoroughly before LIVE!

### Risk Parameters

```env
# Risk 2% of portfolio per trade
RISK_PER_TRADE=0.02

# Maximum 6% total portfolio risk
MAX_PORTFOLIO_RISK=0.06

# Maximum 25% of portfolio in single position
MAX_POSITION_SIZE=0.25
```

---

## Monitoring & Maintenance

### Systemd Service Configuration

Create `/etc/systemd/system/kiwi-ai.service`:
```ini
[Unit]
Description=Kiwi_AI Trading Bot
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Kiwi_AI
ExecStart=/usr/local/bin/docker-compose up
ExecStop=/usr/local/bin/docker-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kiwi-ai
sudo systemctl start kiwi-ai

# Check status
sudo systemctl status kiwi-ai

# View logs
sudo journalctl -u kiwi-ai -f
```

### Log Management

#### View Logs
```bash
# Docker Compose
docker-compose logs -f kiwi-ai

# Systemd
sudo journalctl -u kiwi-ai -f

# Application logs (if mounted)
tail -f logs/kiwi_ai.log
```

#### Log Rotation
Docker automatically rotates logs (configured in `docker-compose.yml`):
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Model Retraining

#### Manual Retraining
```bash
# Enter container
docker-compose exec kiwi-ai bash

# Retrain models
python train_models.py --mode all --symbols AAPL MSFT GOOGL AMZN TSLA

# Exit container
exit

# Restart to load new models
docker-compose restart kiwi-ai
```

#### Automated Retraining (Cron)
Add to crontab (`crontab -e`):
```bash
# Retrain models every Sunday at 2 AM
0 2 * * 0 cd /home/ubuntu/Kiwi_AI && docker-compose exec -T kiwi-ai python train_models.py --mode all --symbols AAPL MSFT GOOGL AMZN TSLA
```

### Health Monitoring

#### Check Container Health
```bash
docker ps
docker inspect kiwi-ai-trading | grep -i health
```

#### Monitor System Resources
```bash
docker stats kiwi-ai-trading
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs kiwi-ai

# Rebuild container
docker-compose build --no-cache
docker-compose up -d

# Check environment variables
docker-compose exec kiwi-ai env | grep -i alpaca
```

### API Connection Errors
- Verify API keys in `.env`
- Check `ALPACA_BASE_URL` (paper vs live)
- Ensure network connectivity
- Check Alpaca API status

### Model Not Found
```bash
# Train models
docker-compose exec kiwi-ai python train_models.py --mode all --symbols AAPL MSFT
```

### High Memory Usage
- Reduce number of trading symbols
- Adjust resource limits in `docker-compose.yml`
- Monitor with `docker stats`

### Permission Errors
```bash
# Fix ownership
sudo chown -R 1000:1000 logs/ models/ market_data/ backtest_reports/
```

---

## Security Best Practices

### 1. Environment Variables
- **Never** commit `.env` to Git
- Use strong, unique API keys
- Rotate keys regularly
- Use different keys for paper/live trading

### 2. Firewall Configuration
```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow from YOUR_IP to any port 8501  # Dashboard (optional)
```

### 3. SSH Security
```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no

sudo systemctl restart ssh
```

### 4. Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 5. Backup Important Data
```bash
# Backup models and configuration
tar -czf kiwi-ai-backup-$(date +%Y%m%d).tar.gz \
  models/ .env docker-compose.yml
```

### 6. Monitor API Rate Limits
- Alpaca has rate limits (200 requests/minute)
- Kiwi_AI implements caching to minimize API calls
- Monitor logs for rate limit warnings

---

## Performance Optimization

### 1. Resource Allocation
Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Increase for more symbols
      memory: 4G       # Increase for larger datasets
```

### 2. Data Caching
Market data is cached in `market_data/` directory to reduce API calls.

### 3. Model Performance
- Train on recent data (default: 60 days)
- Retrain weekly or monthly
- Monitor performance metrics in dashboard

---

## Scaling to Multiple Symbols

### 1. Update Configuration
```env
SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX,AMD,INTC
```

### 2. Increase Resources
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # More symbols = more memory
```

### 3. Retrain Models
```bash
docker-compose exec kiwi-ai python train_models.py --mode all \
  --symbols AAPL MSFT GOOGL AMZN TSLA NVDA META NFLX AMD INTC
```

---

## Support & Resources

- **Documentation**: `README.md`, `CHANGELOG.md`
- **Phase Completion**: `ALL_PHASES_COMPLETED.md`
- **Roadmap**: `RoadMap.txt`
- **Issues**: GitHub Issues
- **Alpaca Docs**: https://docs.alpaca.markets

---

## Quick Reference

```bash
# Start trading bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down

# Restart bot
docker-compose restart

# Retrain models
docker-compose exec kiwi-ai python train_models.py --mode all --symbols AAPL MSFT

# View dashboard
docker-compose up -d dashboard
# Access: http://localhost:8501

# Backup data
tar -czf backup.tar.gz models/ logs/ .env

# Check health
docker ps
docker stats kiwi-ai-trading
```

---

**🚀 Ready to Deploy!**

Start with **PAPER** mode, test thoroughly, then graduate to **LIVE** trading when confident.

Good luck, and trade responsibly! 📈
