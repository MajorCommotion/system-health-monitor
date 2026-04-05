# Changelog

All notable changes to System Health Monitor.

---

## [1.1.0] - 2026-04-05

### Added ✨
- **Docker Container Monitoring** (`--docker`)
  - Track all containers (running, stopped, paused)
  - Show container state, image, and health status
  - Warning alerts when containers are stopped/paused
  - Limit display to first 10 containers (prevents output overflow)

- **Docker Resource Statistics** (`--docker-stats`)
  - CPU usage per container
  - Memory usage per container (absolute + percentage)
  - Real-time stats via `docker stats` integration

- **Temperature Sensor Monitoring** (`--temperature`)
  - Auto-detect CPU temperature sensors (`/sys/class/thermal/thermal_zone*`)
  - Auto-detect hwmon sensors (`/sys/class/hwmon/hwmon*`)
  - NVIDIA GPU support via `nvidia-smi` (if available)
  - Per-sensor warnings (>80°C threshold)
  - Display in both Celsius and Fahrenheit
  - Overall temperature status (warning if any sensor > 80°C)

- **Convenience Flag** (`--all`)
  - Enable all monitoring features at once
  - Equivalent to: `--docker --docker-stats --temperature`

### Changed 🔄
- Enhanced `run_full_check()` method with optional feature flags
- Improved `print_report()` with new sections for Docker and temperature
- Updated help text with new command-line options

### Technical Details 🔧
- Added `glob` import for sensor path discovery
- Temperature detection supports multiple sensor types:
  - `/sys/class/thermal/thermal_zone*/temp` (most common)
  - `/sys/class/hwmon/hwmon*/temp*_input` (hwmon sensors)
  - `nvidia-smi` (NVIDIA GPUs)
- Docker commands have 10-second timeout (prevents hanging)
- Graceful error handling when Docker/sensors unavailable

---

## [1.0.0] - 2026-04-05

### Initial Release 🎉

**Core Features:**
- Disk usage monitoring
- Memory usage tracking
- CPU load averages (1/5/15 min)
- System uptime
- systemd service health checks
- Multiple output formats (human/JSON)
- Configurable thresholds (disk/memory)
- Overall health status with warnings
- Clean, professional Python code
- Comprehensive documentation

**Stats:**
- 312 lines of Python code
- 301 lines of README documentation
- Zero external dependencies
- MIT License

---

## Version Comparison

### v1.0.0 → v1.1.0

**Lines of Code:**
- v1.0.0: 312 lines
- v1.1.0: 489 lines (+177 lines, +56% code growth)

**Features:**
- v1.0.0: 5 core features
- v1.1.0: 8 features (+3 major additions)

**Sensor Coverage:**
- v1.0.0: System resources only
- v1.1.0: System + Docker + Temperature (multi-layer monitoring)

---

## Roadmap

### Planned for v1.2.0
- [ ] Network bandwidth monitoring
- [ ] Email/webhook alerts
- [ ] Historical data tracking (SQLite)

### Planned for v2.0.0
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Prometheus exporter
- [ ] Multi-host monitoring
- [ ] Custom plugin system

---

**Upgrade Instructions:**

```bash
# Update repository
git pull origin main

# Test new features
./monitor.py --all

# Update any scripts using old flags
# (No breaking changes - all v1.0 commands still work!)
```

**Migration:** No breaking changes. All v1.0.0 commands remain compatible.
