#!/usr/bin/env python3
"""
System Health Monitor
A lightweight tool for monitoring system resources and service health.
Perfect for self-hosted infrastructure (Umbrel, Nextcloud, etc.)

Author: lexcellent
License: MIT
"""

import os
import subprocess
import json
import glob
from datetime import datetime
from typing import Dict, List, Optional


class SystemMonitor:
    """Monitor system health metrics and service status."""
    
    def __init__(self, threshold_disk: int = 80, threshold_memory: int = 85):
        """
        Initialize system monitor with configurable thresholds.
        
        Args:
            threshold_disk: Disk usage warning threshold (%)
            threshold_memory: Memory usage warning threshold (%)
        """
        self.threshold_disk = threshold_disk
        self.threshold_memory = threshold_memory
        self.timestamp = datetime.utcnow().isoformat()
    
    def get_disk_usage(self) -> Dict[str, any]:
        """
        Get disk usage statistics.
        
        Returns:
            Dictionary with usage percentage, used/total space
        """
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return {"error": "Unable to parse df output"}
            
            parts = lines[1].split()
            usage_pct = int(parts[4].rstrip('%'))
            
            return {
                "filesystem": parts[0],
                "total": parts[1],
                "used": parts[2],
                "available": parts[3],
                "usage_percent": usage_pct,
                "status": "warning" if usage_pct >= self.threshold_disk else "ok"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_memory_usage(self) -> Dict[str, any]:
        """
        Get memory usage statistics.
        
        Returns:
            Dictionary with memory metrics
        """
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            lines = meminfo.split('\n')
            mem_data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':')
                    mem_data[key.strip()] = value.strip()
            
            total_kb = int(mem_data.get('MemTotal', '0').split()[0])
            available_kb = int(mem_data.get('MemAvailable', '0').split()[0])
            used_kb = total_kb - available_kb
            usage_pct = int((used_kb / total_kb) * 100) if total_kb > 0 else 0
            
            return {
                "total_mb": round(total_kb / 1024, 2),
                "used_mb": round(used_kb / 1024, 2),
                "available_mb": round(available_kb / 1024, 2),
                "usage_percent": usage_pct,
                "status": "warning" if usage_pct >= self.threshold_memory else "ok"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_cpu_load(self) -> Dict[str, any]:
        """
        Get CPU load averages.
        
        Returns:
            Dictionary with 1/5/15 minute load averages
        """
        try:
            with open('/proc/loadavg', 'r') as f:
                load_avg = f.read().strip().split()[:3]
            
            return {
                "1min": float(load_avg[0]),
                "5min": float(load_avg[1]),
                "15min": float(load_avg[2]),
                "status": "ok"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_service_status(self, service_name: str) -> Dict[str, any]:
        """
        Check if a systemd service is running.
        
        Args:
            service_name: Name of the service (e.g., 'docker', 'nginx')
        
        Returns:
            Dictionary with service status
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True,
                text=True
            )
            is_active = result.stdout.strip() == "active"
            
            return {
                "service": service_name,
                "status": "running" if is_active else "stopped",
                "active": is_active
            }
        except Exception as e:
            return {"service": service_name, "error": str(e)}
    
    def get_uptime(self) -> Dict[str, any]:
        """
        Get system uptime.
        
        Returns:
            Dictionary with uptime in seconds and human-readable format
        """
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                "seconds": uptime_seconds,
                "human_readable": f"{days}d {hours}h {minutes}m",
                "status": "ok"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_docker_containers(self) -> Dict[str, any]:
        """
        Get Docker container status (running, stopped, paused).
        
        Returns:
            Dictionary with container statistics and details
        """
        try:
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}|{{.State}}|{{.Status}}|{{.Image}}"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    name, state, status, image = parts
                    containers.append({
                        "name": name,
                        "state": state,
                        "status": status,
                        "image": image,
                        "healthy": state == "running"
                    })
            
            running = sum(1 for c in containers if c['state'] == 'running')
            stopped = sum(1 for c in containers if c['state'] == 'exited')
            paused = sum(1 for c in containers if c['state'] == 'paused')
            
            return {
                "total": len(containers),
                "running": running,
                "stopped": stopped,
                "paused": paused,
                "containers": containers,
                "status": "warning" if stopped > 0 or paused > 0 else "ok"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Docker command timed out"}
        except subprocess.CalledProcessError as e:
            return {"error": f"Docker not available or permission denied: {e}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_temperature_sensors(self) -> Dict[str, any]:
        """
        Get CPU/GPU temperature readings from available sensors.
        Checks multiple common sensor paths.
        
        Returns:
            Dictionary with temperature readings in Celsius
        """
        temps = {}
        
        # Method 1: /sys/class/thermal/thermal_zone* (most common)
        try:
            thermal_zones = glob.glob('/sys/class/thermal/thermal_zone*/temp')
            for zone_path in thermal_zones:
                zone_name = os.path.basename(os.path.dirname(zone_path))
                try:
                    with open(zone_path, 'r') as f:
                        temp_millidegrees = int(f.read().strip())
                        temp_celsius = temp_millidegrees / 1000.0
                        
                        # Read zone type if available
                        type_path = zone_path.replace('/temp', '/type')
                        zone_type = zone_name
                        if os.path.exists(type_path):
                            with open(type_path, 'r') as tf:
                                zone_type = tf.read().strip()
                        
                        temps[zone_type] = {
                            "celsius": round(temp_celsius, 1),
                            "fahrenheit": round((temp_celsius * 9/5) + 32, 1),
                            "status": "warning" if temp_celsius > 80 else "ok"
                        }
                except (IOError, ValueError):
                    continue
        except Exception:
            pass
        
        # Method 2: /sys/class/hwmon/hwmon* (hwmon sensors)
        try:
            hwmon_paths = glob.glob('/sys/class/hwmon/hwmon*/temp*_input')
            for temp_path in hwmon_paths:
                try:
                    with open(temp_path, 'r') as f:
                        temp_millidegrees = int(f.read().strip())
                        temp_celsius = temp_millidegrees / 1000.0
                        
                        # Try to read sensor label
                        label_path = temp_path.replace('_input', '_label')
                        sensor_name = os.path.basename(temp_path)
                        if os.path.exists(label_path):
                            with open(label_path, 'r') as lf:
                                sensor_name = lf.read().strip()
                        
                        # Avoid duplicates
                        if sensor_name not in temps:
                            temps[sensor_name] = {
                                "celsius": round(temp_celsius, 1),
                                "fahrenheit": round((temp_celsius * 9/5) + 32, 1),
                                "status": "warning" if temp_celsius > 80 else "ok"
                            }
                except (IOError, ValueError):
                    continue
        except Exception:
            pass
        
        # Method 3: nvidia-smi for NVIDIA GPUs
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for idx, line in enumerate(result.stdout.strip().split('\n')):
                    if line:
                        temp_celsius = float(line)
                        temps[f"GPU{idx}"] = {
                            "celsius": round(temp_celsius, 1),
                            "fahrenheit": round((temp_celsius * 9/5) + 32, 1),
                            "status": "warning" if temp_celsius > 85 else "ok"
                        }
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        if not temps:
            return {"error": "No temperature sensors found"}
        
        # Calculate overall status
        has_warning = any(t.get("status") == "warning" for t in temps.values() if isinstance(t, dict))
        
        return {
            "sensors": temps,
            "count": len(temps),
            "status": "warning" if has_warning else "ok"
        }
    
    def get_docker_stats(self) -> Dict[str, any]:
        """
        Get resource usage statistics for running Docker containers.
        
        Returns:
            Dictionary with CPU/memory usage per container
        """
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", 
                 "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            container_stats = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    name, cpu, mem_usage, mem_pct = parts
                    container_stats.append({
                        "name": name,
                        "cpu_percent": cpu.strip(),
                        "memory_usage": mem_usage.strip(),
                        "memory_percent": mem_pct.strip()
                    })
            
            return {
                "containers": container_stats,
                "count": len(container_stats),
                "status": "ok"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Docker stats command timed out"}
        except subprocess.CalledProcessError:
            return {"error": "Docker stats not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_full_check(
        self, 
        services: Optional[List[str]] = None,
        check_docker: bool = False,
        check_docker_stats: bool = False,
        check_temps: bool = False
    ) -> Dict[str, any]:
        """
        Run complete system health check.
        
        Args:
            services: Optional list of service names to check
            check_docker: Enable Docker container monitoring
            check_docker_stats: Enable Docker resource usage stats
            check_temps: Enable temperature sensor monitoring
        
        Returns:
            Complete health report dictionary
        """
        report = {
            "timestamp": self.timestamp,
            "hostname": os.uname().nodename,
            "disk": self.get_disk_usage(),
            "memory": self.get_memory_usage(),
            "cpu": self.get_cpu_load(),
            "uptime": self.get_uptime()
        }
        
        if services:
            report["services"] = [
                self.check_service_status(svc) for svc in services
            ]
        
        if check_docker:
            report["docker"] = self.get_docker_containers()
        
        if check_docker_stats:
            report["docker_stats"] = self.get_docker_stats()
        
        if check_temps:
            report["temperature"] = self.get_temperature_sensors()
        
        # Overall health status
        warnings = []
        if report["disk"].get("status") == "warning":
            warnings.append(f"Disk usage high: {report['disk']['usage_percent']}%")
        if report["memory"].get("status") == "warning":
            warnings.append(f"Memory usage high: {report['memory']['usage_percent']}%")
        if check_docker and report.get("docker", {}).get("status") == "warning":
            docker_info = report["docker"]
            if docker_info.get("stopped", 0) > 0:
                warnings.append(f"Docker: {docker_info['stopped']} container(s) stopped")
            if docker_info.get("paused", 0) > 0:
                warnings.append(f"Docker: {docker_info['paused']} container(s) paused")
        if check_temps and report.get("temperature", {}).get("status") == "warning":
            warnings.append("Temperature sensors show high readings (>80°C)")
        
        report["overall_status"] = "warning" if warnings else "healthy"
        report["warnings"] = warnings
        
        return report


def print_report(report: Dict[str, any], format: str = "human") -> None:
    """
    Print health report in specified format.
    
    Args:
        report: Health report dictionary
        format: Output format ('human' or 'json')
    """
    if format == "json":
        print(json.dumps(report, indent=2))
        return
    
    # Human-readable format
    print("=" * 60)
    print(f"System Health Report - {report['timestamp']}")
    print(f"Hostname: {report['hostname']}")
    print("=" * 60)
    
    # Disk
    disk = report.get('disk', {})
    if 'error' not in disk:
        status_icon = "⚠️ " if disk.get('status') == 'warning' else "✅"
        print(f"\n{status_icon} DISK USAGE:")
        print(f"  Total: {disk['total']} | Used: {disk['used']} | Available: {disk['available']}")
        print(f"  Usage: {disk['usage_percent']}%")
    
    # Memory
    mem = report.get('memory', {})
    if 'error' not in mem:
        status_icon = "⚠️ " if mem.get('status') == 'warning' else "✅"
        print(f"\n{status_icon} MEMORY USAGE:")
        print(f"  Total: {mem['total_mb']} MB | Used: {mem['used_mb']} MB | Available: {mem['available_mb']} MB")
        print(f"  Usage: {mem['usage_percent']}%")
    
    # CPU
    cpu = report.get('cpu', {})
    if 'error' not in cpu:
        print(f"\n✅ CPU LOAD:")
        print(f"  1min: {cpu['1min']} | 5min: {cpu['5min']} | 15min: {cpu['15min']}")
    
    # Uptime
    uptime = report.get('uptime', {})
    if 'error' not in uptime:
        print(f"\n✅ UPTIME:")
        print(f"  {uptime['human_readable']}")
    
    # Services
    if 'services' in report:
        print(f"\n📦 SERVICES:")
        for svc in report['services']:
            if 'error' not in svc:
                status_icon = "✅" if svc['active'] else "❌"
                print(f"  {status_icon} {svc['service']}: {svc['status']}")
    
    # Docker containers
    if 'docker' in report:
        docker = report['docker']
        if 'error' not in docker:
            status_icon = "⚠️ " if docker.get('status') == 'warning' else "✅"
            print(f"\n{status_icon} DOCKER CONTAINERS:")
            print(f"  Total: {docker['total']} | Running: {docker['running']} | Stopped: {docker['stopped']} | Paused: {docker['paused']}")
            
            # Show first 10 containers
            for container in docker['containers'][:10]:
                state_icon = "✅" if container['healthy'] else "❌"
                print(f"  {state_icon} {container['name']}: {container['state']} ({container['image']})")
            
            if len(docker['containers']) > 10:
                print(f"  ... and {len(docker['containers']) - 10} more")
    
    # Docker stats
    if 'docker_stats' in report:
        stats = report['docker_stats']
        if 'error' not in stats and stats.get('count', 0) > 0:
            print(f"\n📊 DOCKER RESOURCE USAGE:")
            for container in stats['containers'][:10]:
                print(f"  {container['name']}: CPU {container['cpu_percent']} | Memory {container['memory_usage']} ({container['memory_percent']})")
    
    # Temperature sensors
    if 'temperature' in report:
        temps = report['temperature']
        if 'error' not in temps:
            status_icon = "⚠️ " if temps.get('status') == 'warning' else "✅"
            print(f"\n{status_icon} TEMPERATURE SENSORS:")
            for sensor_name, data in temps.get('sensors', {}).items():
                temp_icon = "🔥" if data.get('status') == 'warning' else "🌡️ "
                print(f"  {temp_icon} {sensor_name}: {data['celsius']}°C ({data['fahrenheit']}°F)")
    
    # Overall status
    print("\n" + "=" * 60)
    if report['overall_status'] == 'healthy':
        print("✅ OVERALL STATUS: HEALTHY")
    else:
        print("⚠️  OVERALL STATUS: WARNING")
        for warning in report['warnings']:
            print(f"  - {warning}")
    print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Monitor system health and service status"
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format (default: human)"
    )
    parser.add_argument(
        "--services",
        nargs="+",
        help="Services to check (e.g., docker nginx)"
    )
    parser.add_argument(
        "--disk-threshold",
        type=int,
        default=80,
        help="Disk usage warning threshold (default: 80)"
    )
    parser.add_argument(
        "--memory-threshold",
        type=int,
        default=85,
        help="Memory usage warning threshold (default: 85)"
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Monitor Docker containers"
    )
    parser.add_argument(
        "--docker-stats",
        action="store_true",
        help="Include Docker container resource usage"
    )
    parser.add_argument(
        "--temperature",
        action="store_true",
        help="Monitor temperature sensors"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Enable all monitoring features"
    )
    
    args = parser.parse_args()
    
    # If --all is used, enable everything
    if args.all:
        check_docker = True
        check_docker_stats = True
        check_temps = True
    else:
        check_docker = args.docker
        check_docker_stats = args.docker_stats
        check_temps = args.temperature
    
    monitor = SystemMonitor(
        threshold_disk=args.disk_threshold,
        threshold_memory=args.memory_threshold
    )
    
    report = monitor.run_full_check(
        services=args.services,
        check_docker=check_docker,
        check_docker_stats=check_docker_stats,
        check_temps=check_temps
    )
    print_report(report, format=args.format)


if __name__ == "__main__":
    main()
