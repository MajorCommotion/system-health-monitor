# Demo: System Health Monitor

## What It Does

This Python script monitors your system health in real-time:

- **Disk usage** (with warnings when threshold exceeded)
- **Memory usage** (track RAM consumption)
- **CPU load averages** (1/5/15 minute stats)
- **System uptime** (how long since last reboot)
- **Service health checks** (Docker, nginx, Bitcoin node, etc.)

## Why It's Useful

Perfect for self-hosted infrastructure:
- Monitor Umbrel Pro server health
- Check if critical services are running
- Automate daily health reports (via cron)
- Integrate with OpenClaw for automated alerts

## Quick Demo

### Run basic health check:
```bash
./monitor.py
```

**Output:**
```
✅ DISK USAGE:
  Total: 3.6T | Used: 943G | Available: 2.6T
  Usage: 27%

✅ MEMORY USAGE:
  Total: 15732.46 MB | Used: 10419.72 MB | Available: 5312.74 MB
  Usage: 66%

✅ OVERALL STATUS: HEALTHY
```

### Monitor specific services:
```bash
./monitor.py --services docker nginx
```

### JSON output (for automation):
```bash
./monitor.py --format json
```

## Real-World Use Cases

### 1. OpenClaw Heartbeat Integration
Add to `HEARTBEAT.md`:
```markdown
- Check system health: run `/data/.openclaw/workspace/system-health-monitor/monitor.py`
- If warnings: notify owner
```

### 2. Daily Cron Report
```bash
# /etc/crontab
0 2 * * * /data/.openclaw/workspace/system-health-monitor/monitor.py --format json >> /var/log/health.log
```

### 3. Pre-Deployment Check
Before updating Umbrel or services:
```bash
./monitor.py --services docker umbrel-startup bitcoin lightning
```

## Tech Highlights

- **Zero dependencies** - Pure Python 3 standard library
- **Cross-platform** - Works on any Linux system
- **Extensible** - Easy to add custom checks
- **Professional** - Clean code, type hints, docstrings
- **MIT License** - Free to use and modify

## Next Steps

1. Test on your Umbrel Pro
2. Integrate with OpenClaw automation
3. Add custom service checks
4. Contribute improvements on GitHub

---

**Author:** lexcellent  
**License:** MIT  
**Status:** Ready for production use
