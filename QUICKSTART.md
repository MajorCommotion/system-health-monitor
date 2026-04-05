# Quick Start Guide

Get up and running in 60 seconds!

---

## Installation

```bash
# Clone repository
git clone https://github.com/lexcellent/system-health-monitor.git
cd system-health-monitor

# Make executable
chmod +x monitor.py

# Run it!
./monitor.py
```

**That's it!** No dependencies, no configuration required.

---

## Basic Commands

### 1. Basic Health Check
```bash
./monitor.py
```
Shows: disk, memory, CPU, uptime

---

### 2. Full System Scan (Recommended)
```bash
./monitor.py --all
```
Shows: everything (Docker, temperatures, resources)

---

### 3. Check Specific Services
```bash
./monitor.py --services docker nginx
```
Shows: are Docker and nginx running?

---

### 4. Monitor Docker Containers
```bash
./monitor.py --docker
```
Shows: all containers and their states

---

### 5. Check Temperatures
```bash
./monitor.py --temperature
```
Shows: CPU/GPU temperatures (auto-detected)

---

### 6. JSON Output (for scripts)
```bash
./monitor.py --all --format json
```
Machine-readable output

---

## Common Use Cases

### For Umbrel Users
```bash
./monitor.py --all --services docker umbrel-startup
```

### For Bitcoin Node Operators
```bash
./monitor.py --services bitcoind electrs lnd --temperature
```

### For Self-Hosters
```bash
./monitor.py --services nextcloud nginx postgresql --docker
```

---

## Set Custom Thresholds

```bash
# Warn at 70% disk, 75% memory
./monitor.py --disk-threshold 70 --memory-threshold 75
```

---

## Automation

### Add to cron (daily at 2 AM)
```bash
# Edit crontab
crontab -e

# Add this line:
0 2 * * * /path/to/monitor.py --all --format json >> /var/log/health.log
```

---

## Help

```bash
./monitor.py --help
```

---

## What's Next?

1. **Read EXAMPLES.md** - 18 real-world scenarios
2. **Read README.md** - Full documentation
3. **Integrate with OpenClaw** - Automated alerts
4. **Star the repo** - Support the project!

---

**Total time to get started:** Less than 60 seconds! 🚀
