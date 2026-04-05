# Usage Examples

Comprehensive examples demonstrating all features of the System Health Monitor.

---

## Basic Usage

### 1. Quick Health Check
```bash
./monitor.py
```

**What it shows:**
- Disk usage
- Memory usage
- CPU load averages
- System uptime

**When to use:** Daily quick check

---

### 2. Full System Scan (Recommended)
```bash
./monitor.py --all
```

**What it shows:**
- Everything from basic check
- Docker containers (all states)
- Docker resource usage (CPU/memory per container)
- Temperature sensors (all available)

**When to use:** Weekly comprehensive health audit

---

## Advanced Monitoring

### 3. Umbrel Infrastructure Check
```bash
./monitor.py --all --services docker umbrel-startup nginx
```

**Perfect for Umbrel users:**
- System resources
- Docker containers (all apps: Bitcoin, Lightning, Nextcloud, etc.)
- Container resource usage
- Temperature (important for Raspberry Pi/low-power devices)
- Key services status

**When to use:** Before/after updates, troubleshooting

---

### 4. Bitcoin Node Monitoring
```bash
./monitor.py --services bitcoind electrs \
             --docker \
             --temperature \
             --disk-threshold 75
```

**Tracks:**
- Bitcoin Core service status
- Electrs service status
- Docker containers (if using containerized Bitcoin stack)
- Disk usage (Bitcoin blockchain grows!)
- Temperature (mining/validation can heat up)

**When to use:** Daily Bitcoin node health check

---

### 5. Self-Hosted Stack
```bash
./monitor.py --services nextcloud nginx postgresql redis \
             --docker \
             --memory-threshold 80
```

**For self-hosted services:**
- Web server (nginx)
- Database (PostgreSQL)
- Cache (Redis)
- Nextcloud service
- Docker containers
- Memory usage (critical for databases)

**When to use:** Production server monitoring

---

## Automation & Integration

### 6. Cron Job (Daily Report)
```bash
# Add to /etc/crontab or crontab -e
0 2 * * * /path/to/monitor.py --all --format json >> /var/log/health-report.jsonl
```

**Creates:**
- Daily JSON logs (one line per day)
- Machine-readable format
- Easy to parse/analyze later

**When to use:** Historical tracking, trend analysis

---

### 7. Pre-Deployment Check
```bash
#!/bin/bash
# pre-deploy.sh - Run before deploying updates

echo "=== Pre-Deployment Health Check ==="
./monitor.py --all --services docker nginx postgresql

if [ $? -ne 0 ]; then
    echo "ERROR: System health check failed!"
    exit 1
fi

echo "System healthy, proceeding with deployment..."
```

**Prevents:**
- Deploying to unhealthy systems
- Compounding existing issues
- Downtime from resource exhaustion

**When to use:** Before every production deployment

---

### 8. OpenClaw Integration (Automated Alerts)
```bash
#!/bin/bash
# openclaw-health-check.sh

REPORT=$(./monitor.py --all --format json)
STATUS=$(echo "$REPORT" | jq -r '.overall_status')

if [ "$STATUS" == "warning" ]; then
    WARNINGS=$(echo "$REPORT" | jq -r '.warnings[]')
    # Send alert via OpenClaw
    echo "⚠️ System Health Alert: $WARNINGS"
fi
```

**Features:**
- Auto-notify on warnings
- Send to Discord/Telegram via OpenClaw
- No manual intervention needed

**When to use:** 24/7 automated monitoring

---

## Output Formats

### 9. Human-Readable (Default)
```bash
./monitor.py --temperature
```

**Output:**
```
✅ TEMPERATURE SENSORS:
  🌡️  x86_pkg_temp: 43.0°C (109.4°F)
  🌡️  Core 0: 40.0°C (104.0°F)
  🌡️  Core 1: 41.0°C (105.8°F)
```

**Best for:** Manual inspection, troubleshooting

---

### 10. JSON (Machine-Readable)
```bash
./monitor.py --docker --format json
```

**Output:**
```json
{
  "timestamp": "2026-04-05T10:20:12",
  "hostname": "umbrel-pro",
  "docker": {
    "total": 15,
    "running": 12,
    "stopped": 3,
    "containers": [...]
  }
}
```

**Best for:** Automation, scripting, logging

---

## Threshold Customization

### 11. Conservative Thresholds (Early Warnings)
```bash
./monitor.py --disk-threshold 60 --memory-threshold 70
```

**Triggers warnings earlier:**
- Disk: 60% (instead of default 80%)
- Memory: 70% (instead of default 85%)

**When to use:** Production servers, low-margin systems

---

### 12. Relaxed Thresholds (High-Capacity Systems)
```bash
./monitor.py --disk-threshold 90 --memory-threshold 95
```

**Allows higher usage before warnings:**
- Disk: 90%
- Memory: 95%

**When to use:** High-capacity servers, test environments

---

## Real-World Scenarios

### 13. Raspberry Pi Monitoring
```bash
./monitor.py --all --memory-threshold 75
```

**Why:**
- Temperature critical (no fan, heat throttling)
- Memory limited (1-8GB)
- Docker common (Umbrel, Home Assistant, Pi-hole)

---

### 14. Mining Rig Monitoring
```bash
./monitor.py --temperature --services cgminer
```

**Why:**
- Temperature critical (GPU/ASIC heat)
- Miner service uptime (cgminer, bfgminer, etc.)

---

### 15. Docker-Only Environment
```bash
./monitor.py --docker --docker-stats
```

**Shows:**
- All container states
- CPU usage per container
- Memory usage per container

**When to use:** Containerized infrastructure (no systemd services)

---

## Troubleshooting Examples

### 16. High Memory Warning
```bash
./monitor.py --docker-stats
```

**Diagnose:**
- Which container is using most memory?
- Is a container leaking memory?
- Need to restart/scale down?

---

### 17. Stopped Containers
```bash
./monitor.py --docker
```

**Check:**
- Which containers stopped unexpectedly?
- Are critical services down?
- Need manual restart?

---

### 18. High Temperature
```bash
./monitor.py --temperature
```

**Investigate:**
- Which component is overheating?
- CPU? GPU? Storage?
- Need better cooling?

---

## Quick Reference

| Use Case | Command |
|----------|---------|
| Daily quick check | `./monitor.py` |
| Full system scan | `./monitor.py --all` |
| Umbrel monitoring | `./monitor.py --all --services docker umbrel-startup` |
| Bitcoin node | `./monitor.py --services bitcoind electrs --temperature` |
| Temperature only | `./monitor.py --temperature` |
| Docker only | `./monitor.py --docker --docker-stats` |
| JSON output | `./monitor.py --format json` |
| Automation | `./monitor.py --all --format json >> health.log` |

---

## Tips

1. **Start with `--all`** for comprehensive overview
2. **Use JSON for logging** (`--format json`)
3. **Set lower thresholds** for production (`--disk-threshold 70`)
4. **Monitor temperature** on low-power devices (Pi, laptops)
5. **Check Docker stats** if containers consume resources
6. **Combine flags** for custom monitoring profiles

---

**Pro Tip:** Create shell aliases for common checks:
```bash
alias health='./monitor.py --all'
alias umbrel-check='./monitor.py --all --services docker umbrel-startup nginx'
alias btc-check='./monitor.py --services bitcoind electrs lnd --temperature'
```

Add to `.bashrc` or `.zshrc` for instant access!
