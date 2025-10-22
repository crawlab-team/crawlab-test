#!/usr/bin/env python3
"""
Diagnostic Collection Tool

Collects Docker logs, system information, and test artifacts for troubleshooting.
Useful for debugging test failures both locally and in CI environments.

Usage:
    ./helpers/tools/collect_diagnostics.py
    ./helpers/tools/collect_diagnostics.py --output-dir /tmp/diagnostics
    ./helpers/tools/collect_diagnostics.py --containers master worker
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class DiagnosticsCollector:
    """Collects comprehensive diagnostics for troubleshooting"""
    
    def __init__(self, output_dir: Optional[Path] = None, namespace: Optional[str] = None):
        """
        Initialize diagnostics collector
        
        Args:
            output_dir: Directory to save diagnostics (default: results/)
            namespace: Docker compose namespace (default: auto-detect from env)
        """
        self.base_dir = Path(__file__).parent.parent.parent
        
        if output_dir is None:
            self.output_dir = self.base_dir / "results"
        else:
            self.output_dir = Path(output_dir)
        
        self.logs_dir = self.output_dir / "docker-logs"
        self.system_dir = self.output_dir / "system-info"
        
        # Create output directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.system_dir.mkdir(parents=True, exist_ok=True)
        
        # Get namespace from environment or use default
        import os
        self.namespace = namespace or os.getenv('CRAWLAB_COMPOSE_NAMESPACE', 'crawlab_test')
        
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🏷️  Namespace: {self.namespace}")
    
    def _run_command(self, cmd: List[str], capture: bool = True) -> Optional[str]:
        """
        Run a shell command and return output
        
        Args:
            cmd: Command and arguments as list
            capture: Whether to capture and return output
            
        Returns:
            Command output if capture=True, None otherwise
        """
        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                return result.stdout + result.stderr
            else:
                subprocess.run(cmd, check=False)
                return None
        except Exception as e:
            print(f"⚠️  Command failed: {' '.join(cmd)}: {e}")
            return None
    
    def collect_container_logs(self, containers: Optional[List[str]] = None):
        """
        Collect logs from Docker containers
        
        Args:
            containers: List of container names (without namespace prefix)
                       If None, collects from all known containers
        """
        if containers is None:
            containers = ['master', 'worker', 'mongo', 'mysql', 'postgres', 'mssql', 'elasticsearch']
        
        print("\n📋 Collecting container logs...")
        
        for container in containers:
            full_name = f"{self.namespace}_{container}"
            
            # Check if container exists
            check_cmd = ['docker', 'ps', '-a', '--format', '{{.Names}}']
            output = self._run_command(check_cmd)
            
            if output and full_name in output:
                print(f"  📄 Collecting logs from {full_name}...")
                
                # Get container logs
                logs = self._run_command(['docker', 'logs', full_name])
                if logs:
                    log_file = self.logs_dir / f"{container}.log"
                    log_file.write_text(logs)
                    print(f"     ✅ Saved to {log_file}")
                
                # Get container inspect data
                inspect = self._run_command(['docker', 'inspect', full_name])
                if inspect:
                    inspect_file = self.logs_dir / f"{container}-inspect.json"
                    inspect_file.write_text(inspect)
            else:
                print(f"  ⏭️  Skipping {full_name} (not found)")
    
    def collect_compose_status(self):
        """Collect Docker Compose service status"""
        print("\n🐳 Collecting Docker Compose status...")
        
        compose_file = self.base_dir / "docker-compose.test.yml"
        if not compose_file.exists():
            compose_file = self.base_dir / "docker-compose.yml"
        
        if compose_file.exists():
            status = self._run_command(['docker', 'compose', '-f', str(compose_file), 'ps'])
            if status:
                status_file = self.logs_dir / "compose-status.txt"
                status_file.write_text(status)
                print(f"  ✅ Saved to {status_file}")
        else:
            print("  ⚠️  No docker-compose file found")
    
    def collect_network_info(self):
        """Collect Docker network information"""
        print("\n🌐 Collecting network information...")
        
        # Try different network names
        network_names = [
            'crawlab-test_crawlab_test',
            'crawlab_test',
            'crawlab_default'
        ]
        
        for network_name in network_names:
            inspect = self._run_command(['docker', 'network', 'inspect', network_name])
            if inspect and 'Error' not in inspect:
                network_file = self.logs_dir / "network-inspect.json"
                network_file.write_text(inspect)
                print(f"  ✅ Network '{network_name}' saved to {network_file}")
                break
        else:
            print("  ⚠️  No Crawlab network found")
    
    def collect_system_info(self):
        """Collect system information"""
        print("\n💻 Collecting system information...")
        
        info_lines = []
        
        # System info
        info_lines.append("=== System Info ===")
        uname = self._run_command(['uname', '-a'])
        if uname:
            info_lines.append(uname)
        
        # Docker version
        info_lines.append("\n=== Docker Version ===")
        docker_version = self._run_command(['docker', '--version'])
        if docker_version:
            info_lines.append(docker_version)
        compose_version = self._run_command(['docker', 'compose', 'version'])
        if compose_version:
            info_lines.append(compose_version)
        
        # Disk usage
        info_lines.append("\n=== Disk Usage ===")
        df = self._run_command(['df', '-h'])
        if df:
            info_lines.append(df)
        
        # Memory usage
        info_lines.append("\n=== Memory Usage ===")
        free = self._run_command(['free', '-h'])
        if free:
            info_lines.append(free)
        
        # Docker system info
        info_lines.append("\n=== Docker System Info ===")
        docker_df = self._run_command(['docker', 'system', 'df'])
        if docker_df:
            info_lines.append(docker_df)
        
        # Running containers
        info_lines.append("\n=== Running Containers ===")
        docker_ps = self._run_command(['docker', 'ps', '-a'])
        if docker_ps:
            info_lines.append(docker_ps)
        
        # Save to file
        system_file = self.system_dir / "system.txt"
        system_file.write_text('\n'.join(info_lines))
        print(f"  ✅ Saved to {system_file}")
    
    def collect_test_results(self):
        """Copy/link test result files to diagnostics directory"""
        print("\n📊 Checking for test results...")
        
        results_pattern = self.base_dir / "results" / "result_*.json"
        result_files = list(results_pattern.parent.glob("result_*.json"))
        
        if result_files:
            print(f"  ✅ Found {len(result_files)} test result files")
        else:
            print("  ℹ️  No test result files found")
    
    def generate_summary(self):
        """Generate a summary report"""
        print("\n📝 Generating summary report...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary_lines = [
            "# Diagnostics Collection Summary",
            f"\n**Timestamp**: {timestamp}",
            f"**Namespace**: {self.namespace}",
            f"**Output Directory**: {self.output_dir}",
            "\n## Collected Files\n",
            "### Docker Logs"
        ]
        
        # List collected log files
        log_files = list(self.logs_dir.glob("*"))
        if log_files:
            for log_file in sorted(log_files):
                size = log_file.stat().st_size / 1024  # KB
                summary_lines.append(f"- `{log_file.name}` ({size:.1f} KB)")
        else:
            summary_lines.append("- *(none)*")
        
        summary_lines.append("\n### System Information")
        
        # List system info files
        system_files = list(self.system_dir.glob("*"))
        if system_files:
            for sys_file in sorted(system_files):
                size = sys_file.stat().st_size / 1024  # KB
                summary_lines.append(f"- `{sys_file.name}` ({size:.1f} KB)")
        else:
            summary_lines.append("- *(none)*")
        
        # Save summary
        summary_file = self.output_dir / f"diagnostics-summary-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        summary_file.write_text('\n'.join(summary_lines))
        print(f"  ✅ Summary saved to {summary_file}")
    
    def collect_all(self, containers: Optional[List[str]] = None):
        """
        Collect all diagnostics
        
        Args:
            containers: Optional list of specific containers to collect logs from
        """
        print(f"\n🔍 Starting diagnostics collection...")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.collect_container_logs(containers)
        self.collect_compose_status()
        self.collect_network_info()
        self.collect_system_info()
        self.collect_test_results()
        self.generate_summary()
        
        print(f"\n✅ Diagnostics collection complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"\nTo view logs:")
        print(f"  ls -lh {self.logs_dir}/")
        print(f"  cat {self.logs_dir}/master.log")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Collect diagnostics for Crawlab test troubleshooting",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for diagnostics (default: results/)'
    )
    
    parser.add_argument(
        '--namespace',
        type=str,
        help='Docker Compose namespace (default: from CRAWLAB_COMPOSE_NAMESPACE env or "crawlab_test")'
    )
    
    parser.add_argument(
        '--containers',
        nargs='+',
        help='Specific containers to collect logs from (default: all known containers)'
    )
    
    args = parser.parse_args()
    
    try:
        collector = DiagnosticsCollector(
            output_dir=args.output_dir,
            namespace=args.namespace
        )
        collector.collect_all(containers=args.containers)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
