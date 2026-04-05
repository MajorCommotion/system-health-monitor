# System Health Monitor

A lightweight Python tool for monitoring system resources and service health. Perfect for self-hosted infrastructure running Umbrel, Nextcloud, Bitcoin nodes, or any Linux-based services.

## Features

✅ **Disk Usage Monitoring** - Track storage consumption with configurable thresholds  
✅ **Memory Usage Tracking** - Monitor RAM utilization in real-time  
✅ **CPU Load Averages** - View 1/5/15 minute load statistics  
✅ **System Uptime** - See how long your system has been running  
✅ **Service Health Checks** - Monitor systemd services (Docker, nginx, etc.)  
✅ **Docker Container Monitoring** - Track container status (running/stopped/paused)  
✅ **Docker Resource Usage** - Monitor CPU/memory usage per container  
✅ **Temperature Sensors** - Monitor CPU/GPU temperatures with auto-detection  
✅ **Multiple Output Formats** - Human-readable or JSON for automation  
✅ **Configurable Thresholds** - Set custom warning levels for disk/memory  

---

## Requirements

- Python 3.6+
- Linux system with `/proc` filesystem
- `systemctl` (for service checks)

No external dependencies required - uses only Python standard library!

---

## Installation

```bash
# Clone the repository
git clone https://github.com/lexcellent/system-health-monitor.git
cd system-health-monitor

# Make executable
chmod +x monitor.py
```

---

## Usage

### Basic Health Check
```bash
./monitor.py
```

**Output:**
```
============================================================
System Health Report - 2026-04-05T10:16:32.123456
Hostname: umbrel-pro
============================================================

✅ DISK USAGE:
  Total: 234G | Used: 89G | Available: 133G
  Usage: 38%

✅ MEMORY USAGE:
  Total: 15872.45 MB | Used: 8234.12 MB | Available: 7638.33 MB
  Usage: 51%

✅ CPU LOAD:
  1min: 0.45 | 5min: 0.62 | 15min: 0.58

✅ UPTIME:
  12d 8h 42m

============================================================
✅ OVERALL STATUS: HEALTHY
============================================================
```

---

### Monitor Specific Services
```bash
./monitor.py --services docker nginx
```

**Output:**
```
📦 SERVICES:
  ✅ docker: running
  ✅ nginx: running
```

---

### Monitor Docker Containers
```bash
./monitor.py --docker
```

**Output:**
```
✅ DOCKER CONTAINERS:
  Total: 15 | Running: 12 | Stopped: 3 | Paused: 0
  ✅ umbrel_web: running (getumbrel/umbrel:latest)
  ✅ nextcloud: running (nextcloud:latest)
  ✅ bitcoind: running (lncm/bitcoind:latest)
  ❌ old_backup: exited (backup:v1)
```

---

### Check Temperature Sensors
```bash
./monitor.py --temperature
```

**Output:**
```
✅ TEMPERATURE SENSORS:
  🌡️  x86_pkg_temp: 43.0°C (109.4°F)
  🌡️  Core 0: 40.0°C (104.0°F)
  🌡️  Core 1: 41.0°C (105.8°F)
  🌡️  GPU0: 65.0°C (149.0°F)
```

---

### Monitor Everything (--all flag)
```bash
./monitor.py --all
```

Enables:
- ✅ Docker container monitoring
- ✅ Docker resource stats
- ✅ Temperature sensors

---

### JSON Output (for automation/scripts)
```bash
./monitor.py --format json
```

**Output:**
```json
{
  "timestamp": "2026-04-05T10:16:32.123456",
  "hostname": "umbrel-pro",
  "disk": {
    "filesystem": "/dev/sda1",
    "total": "234G",
    "used": "89G",
    "available": "133G",
    "usage_percent": 38,
    "status": "ok"
  },
  "memory": {
    "total_mb": 15872.45,
    "used_mb": 8234.12,
    "available_mb": 7638.33,
    "usage_percent": 51,
    "status": "ok"
  },
  ...
}
```

---

### Custom Thresholds
```bash
# Warn when disk > 70% or memory > 75%
./monitor.py --disk-threshold 70 --memory-threshold 75
```

---

## Use Cases

### 1. **Cron Job (daily health check)**
```bash
# Add to crontab (run every day at 2 AM)
0 2 * * * /path/to/monitor.py --format json >> /var/log/health-report.log
```

### 2. **Pre-deployment check**
```bash
# Verify system health before deploying updates
./monitor.py --services docker nginx bitcoin lightning
```

### 3. **Automation integration**
```python
import subprocess
import json

result = subprocess.run(
    ["./monitor.py", "--format", "json"],
    capture_output=True,
    text=True
)
health = json.loads(result.stdout)

if health["overall_status"] == "warning":
    send_alert(health["warnings"])
```

### 4. **OpenClaw integration**
```bash
# Run via OpenClaw heartbeat or cron job
# Automatically notify when thresholds exceeded
```

---

## Example Scenarios

### Scenario 1: High Disk Usage
```
⚠️  OVERALL STATUS: WARNING
  - Disk usage high: 87%
```

**Action:** Clean up logs, remove old Docker images, archive data

### Scenario 2: Service Down
```
📦 SERVICES:
  ✅ docker: running
  ❌ nginx: stopped
```

**Action:** `sudo systemctl start nginx`

---

## Configuration Examples

### Monitor Bitcoin/Lightning Stack
```bash
./monitor.py --services bitcoind lnd electrs --disk-threshold 85 --temperature
```

### Monitor Umbrel Services (Full Check)
```bash
./monitor.py --all --services docker umbrel-startup nginx
```

**Output includes:**
- System resources (disk, memory, CPU)
- Service status (systemd services)
- Docker containers (all Umbrel apps)
- Docker resource usage (CPU/memory per container)
- Temperature sensors (CPU cores, package temp)

### Monitor Self-Hosted Services
```bash
./monitor.py --services nextcloud postgresql nginx redis --docker
```

---

## Advanced Usage

### Create a wrapper script for common checks
```bash
#!/bin/bash
# health-check.sh

echo "=== Umbrel Health Check ==="
./monitor.py --services docker umbrel-startup nginx \
             --disk-threshold 80 \
             --memory-threshold 85

# Send to Discord via webhook if warnings
# (integrate with OpenClaw messaging)
```

---

## Output Fields

### Disk
- `total` - Total disk space
- `used` - Used disk space
- `available` - Available disk space
- `usage_percent` - Usage percentage
- `status` - "ok" or "warning"

### Memory
- `total_mb` - Total RAM in MB
- `used_mb` - Used RAM in MB
- `available_mb` - Available RAM in MB
- `usage_percent` - Usage percentage
- `status` - "ok" or "warning"

### CPU
- `1min` - 1-minute load average
- `5min` - 5-minute load average
- `15min` - 15-minute load average

### Services
- `service` - Service name
- `status` - "running" or "stopped"
- `active` - Boolean (true/false)

---

## Troubleshooting

### Permission Denied Errors
```bash
# If checking services requires elevated permissions
sudo ./monitor.py --services docker
```

### Service Not Found
```bash
# List all available services
systemctl list-units --type=service
```

---

## Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## License

MIT License - See LICENSE file for details

---

## Author

**lexcellent** - Self-hosting enthusiast | Building sovereign infrastructure

---

## Roadmap

- [x] ~~Temperature sensors (CPU/GPU)~~ **DONE!**
- [x] ~~Docker container health checks~~ **DONE!**
- [x] ~~Docker resource usage monitoring~~ **DONE!**
- [ ] Add network bandwidth monitoring
- [ ] Email/SMS alerts via webhooks
- [ ] Historical data tracking (SQLite)
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Prometheus exporter support
- [ ] GPU-specific monitoring (CUDA usage, VRAM)

---

**Star this repo if you find it useful!** ⭐
