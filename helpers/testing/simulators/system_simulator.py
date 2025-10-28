#!/usr/bin/env python3
"""
System-Level Simulation for Reconciliation Testing
Uses real network controls (firewalls, iptables) and process management to simulate
actual disconnection scenarios that trigger genuine reconciliation behavior.
"""

import argparse
import logging
import sys
import os
import time
import subprocess
import psutil
import signal
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

# Add the helpers directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.infrastructure.api_client import CrawlabAPIClient
from helpers.infrastructure.database import (DatabaseHelper, TASK_STATUS_RUNNING, TASK_STATUS_FINISHED,
                           TASK_STATUS_ERROR, TASK_STATUS_NODE_DISCONNECTED, TASK_STATUS_PENDING)
from helpers.infrastructure.utils import setup_logging, TestMetrics, format_duration, load_config

class NetworkSimulator:
    """Network-level simulation for testing reconciliation"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.blocked_rules = []  # Track iptables rules we add
        self.requires_sudo = self._check_sudo_requirements()
    
    def _check_sudo_requirements(self) -> bool:
        """Check if we need sudo for network operations"""
        try:
            # Try to list iptables rules (read-only operation)
            result = subprocess.run(['iptables', '-L'], capture_output=True, text=True)
            return result.returncode != 0
        except FileNotFoundError:
            self.logger.warning("iptables not found - network simulation may be limited")
            return False
    
    def block_port(self, port: int, protocol: str = 'tcp') -> bool:
        """Block network traffic to/from a specific port using iptables"""
        try:
            if self.requires_sudo:
                self.logger.warning("Network blocking requires sudo privileges - skipping")
                return False
            
            # Block incoming traffic to the port
            cmd_in = ['iptables', '-A', 'INPUT', '-p', protocol, '--dport', str(port), '-j', 'DROP']
            # Block outgoing traffic from the port  
            cmd_out = ['iptables', '-A', 'OUTPUT', '-p', protocol, '--sport', str(port), '-j', 'DROP']
            
            for cmd in [cmd_in, cmd_out]:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Failed to block port {port}: {result.stderr}")
                    return False
                
            self.blocked_rules.append((port, protocol))
            self.logger.info(f"✓ Blocked {protocol} traffic on port {port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Port blocking failed: {e}")
            return False
    
    def unblock_port(self, port: int, protocol: str = 'tcp') -> bool:
        """Remove iptables rules blocking a port"""
        try:
            if self.requires_sudo:
                return True  # Nothing to clean up if we couldn't block
            
            # Remove the rules we added (use -D instead of -A)
            cmd_in = ['iptables', '-D', 'INPUT', '-p', protocol, '--dport', str(port), '-j', 'DROP']
            cmd_out = ['iptables', '-D', 'OUTPUT', '-p', protocol, '--sport', str(port), '-j', 'DROP']
            
            for cmd in [cmd_in, cmd_out]:
                subprocess.run(cmd, capture_output=True, text=True)
                # Don't fail if rule doesn't exist
                
            if (port, protocol) in self.blocked_rules:
                self.blocked_rules.remove((port, protocol))
            
            self.logger.info(f"✓ Unblocked {protocol} traffic on port {port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Port unblocking failed: {e}")
            return False
    
    def simulate_network_partition(self, duration: int = 30) -> Dict[str, Any]:
        """Simulate network partition by blocking MongoDB and gRPC ports"""
        self.logger.info(f"Simulating network partition for {duration}s...")
        
        # Common Crawlab ports to block
        ports_to_block = [
            (27017, 'tcp'),  # MongoDB default
            (27018, 'tcp'),  # MongoDB (custom)
            (9666, 'tcp'),   # Crawlab gRPC default
            (8080, 'tcp'),   # Crawlab API default
        ]
        
        blocked_ports = []
        
        # Block the ports
        for port, protocol in ports_to_block:
            if self.block_port(port, protocol):
                blocked_ports.append((port, protocol))
        
        if not blocked_ports:
            self.logger.warning("Could not block any ports - simulation may not be effective")
        
        # Wait for the specified duration
        self.logger.info(f"Network partition active - waiting {duration}s...")
        time.sleep(duration)
        
        # Restore connectivity
        self.logger.info("Restoring network connectivity...")
        for port, protocol in blocked_ports:
            self.unblock_port(port, protocol)
        
        return {
            'simulation_type': 'network_partition',
            'duration': duration,
            'blocked_ports': blocked_ports,
            'effective': len(blocked_ports) > 0
        }
    
    def cleanup_all_rules(self):
        """Clean up all iptables rules we created"""
        for port, protocol in self.blocked_rules.copy():
            self.unblock_port(port, protocol)

class ProcessSimulator:
    """Process-level simulation for testing reconciliation"""
    
    def __init__(self, db_helper: DatabaseHelper):
        self.db = db_helper
        self.logger = logging.getLogger(self.__class__.__name__)
        self.killed_processes = []
    
    def find_crawlab_processes(self) -> List[Dict[str, Any]]:
        """Find actual Crawlab worker processes"""
        crawlab_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                pinfo = proc.info
                cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                
                # Look for Crawlab-related processes
                if any(keyword in cmdline.lower() for keyword in ['crawlab-server']):
                    crawlab_processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cmdline': cmdline
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.logger.info(f"Found {len(crawlab_processes)} Crawlab-related processes")
        return crawlab_processes
    
    def simulate_process_crashes(self, max_processes: int = 3) -> Dict[str, Any]:
        """Simulate process crashes by killing actual processes"""
        self.logger.info(f"Simulating process crashes (max {max_processes} processes)...")
        
        # Find Crawlab processes
        processes = self.find_crawlab_processes()
        
        if not processes:
            self.logger.warning("No Crawlab processes found - creating dummy processes for simulation")
            return self._simulate_dummy_process_crashes(max_processes)
        
        # Kill some processes (but be careful not to kill critical ones)
        killed_count = 0
        killed_pids = []
        
        for proc in processes[:max_processes]:
            try:
                pid = proc['pid']
                
                # Skip if it looks like a critical master process
                if 'master' in proc['cmdline'].lower():
                    continue
                
                # Send SIGTERM first (graceful)
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                
                # Check if still running, then SIGKILL
                if psutil.pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                
                killed_pids.append(pid)
                killed_count += 1
                self.logger.info(f"Killed process {pid}: {proc['name']}")
                
            except (ProcessLookupError, PermissionError) as e:
                self.logger.warning(f"Could not kill process {proc['pid']}: {e}")
        
        self.killed_processes.extend(killed_pids)
        
        return {
            'simulation_type': 'process_crashes',
            'processes_found': len(processes),
            'processes_killed': killed_count,
            'killed_pids': killed_pids
        }
    
    def _simulate_dummy_process_crashes(self, count: int) -> Dict[str, Any]:
        """Create dummy processes and kill them to simulate crashes"""
        dummy_pids = []
        
        for i in range(count):
            # Create a simple background process
            proc = subprocess.Popen(['sleep', '3600'])  # Sleep for 1 hour
            dummy_pids.append(proc.pid)
            
            # Create a corresponding task in the database
            task = self.db.create_test_task(
                status=TASK_STATUS_RUNNING,
                pid=proc.pid
            )
            
            # Kill the process after a short delay
            time.sleep(1)
            proc.terminate()
            
            self.logger.info(f"Created and killed dummy process {proc.pid} with task {task['_id']}")
        
        return {
            'simulation_type': 'dummy_process_crashes',
            'dummy_processes_created': len(dummy_pids),
            'dummy_pids': dummy_pids
        }

class SystemSimulator:
    """Main system-level simulator that combines network and process simulation"""
    
    def __init__(self, api_client: CrawlabAPIClient, db_helper: DatabaseHelper):
        self.api = api_client
        self.db = db_helper
        self.logger = logging.getLogger(self.__class__.__name__)
        self.network_sim = NetworkSimulator()
        self.process_sim = ProcessSimulator(db_helper)
        self.start_time = None
    
    def simulate_worker_disconnection(self, duration: int = 30) -> Dict[str, Any]:
        """Simulate worker disconnection using network controls"""
        self.logger.info(f"Starting realistic worker disconnection simulation...")
        self.start_time = time.time()
        
        # Record initial state
        initial_state = self._capture_system_state()
        
        # Simulate network issues
        network_result = self.network_sim.simulate_network_partition(duration)
        
        # Wait a bit more to observe reconciliation
        self.logger.info("Waiting for reconciliation to detect the disconnection...")
        time.sleep(30)
        
        # Record final state
        final_state = self._capture_system_state()
        
        # Analyze what changed
        changes = self._analyze_state_changes(initial_state, final_state)
        
        return {
            'simulation_type': 'realistic_worker_disconnection',
            'network_simulation': network_result,
            'initial_state': initial_state,
            'final_state': final_state,
            'detected_changes': changes,
            'total_duration': time.time() - self.start_time,
            'reconciliation_triggered': len(changes.get('status_changes', [])) > 0
        }
    
    def simulate_zombie_processes(self) -> Dict[str, Any]:
        """Simulate zombie processes using real process killing"""
        self.logger.info("Starting realistic zombie process simulation...")
        self.start_time = time.time()
        
        # Record initial state
        initial_state = self._capture_system_state()
        
        # Kill some processes
        process_result = self.process_sim.simulate_process_crashes()
        
        # Wait for reconciliation to detect zombie processes
        self.logger.info("Waiting for reconciliation to detect zombie processes...")
        time.sleep(60)  # Give reconciliation time to detect
        
        # Record final state
        final_state = self._capture_system_state()
        
        # Analyze changes
        changes = self._analyze_state_changes(initial_state, final_state)
        
        return {
            'simulation_type': 'realistic_zombie_processes',
            'process_simulation': process_result,
            'initial_state': initial_state,
            'final_state': final_state,
            'detected_changes': changes,
            'total_duration': time.time() - self.start_time,
            'zombie_detection_rate': self._calculate_zombie_detection_rate(changes)
        }
    
    def simulate_mixed_scenario(self) -> Dict[str, Any]:
        """Simulate a complex mixed scenario with multiple real issues"""
        self.logger.info("Starting complex mixed scenario simulation...")
        self.start_time = time.time()
        
        results = {
            'simulation_type': 'realistic_mixed_scenario',
            'scenarios': [],
            'total_duration': 0
        }
        
        # 1. First simulate some process crashes
        process_result = self.process_sim.simulate_process_crashes(2)
        results['scenarios'].append(process_result)
        
        time.sleep(30)  # Let reconciliation work
        
        # 2. Then simulate network issues
        network_result = self.network_sim.simulate_network_partition(20)
        results['scenarios'].append(network_result)
        
        time.sleep(30)  # Let reconciliation work
        
        # 3. Monitor overall system recovery
        recovery_state = self._capture_system_state()
        results['final_system_state'] = recovery_state
        results['total_duration'] = time.time() - self.start_time
        
        return results
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state for comparison"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'running_tasks': len(self.db.get_tasks_by_status(TASK_STATUS_RUNNING)),
                'disconnected_tasks': len(self.db.get_tasks_by_status(TASK_STATUS_NODE_DISCONNECTED)),
                'error_tasks': len(self.db.get_tasks_by_status(TASK_STATUS_ERROR)),
                'finished_tasks': len(self.db.get_tasks_by_status(TASK_STATUS_FINISHED)),
                'active_processes': len(self.process_sim.find_crawlab_processes()),
                'system_load': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent
            }
        except Exception as e:
            self.logger.error(f"Failed to capture system state: {e}")
            return {'error': str(e)}
    
    def _analyze_state_changes(self, initial: Dict, final: Dict) -> Dict[str, Any]:
        """Analyze changes between two system states"""
        if 'error' in initial or 'error' in final:
            return {'error': 'Could not analyze due to state capture errors'}
        
        changes = {
            'task_status_changes': {
                'running': final['running_tasks'] - initial['running_tasks'],
                'disconnected': final['disconnected_tasks'] - initial['disconnected_tasks'],
                'error': final['error_tasks'] - initial['error_tasks'],
                'finished': final['finished_tasks'] - initial['finished_tasks']
            },
            'process_changes': final['active_processes'] - initial['active_processes'],
            'system_impact': {
                'cpu_change': final['system_load'] - initial['system_load'],
                'memory_change': final['memory_usage'] - initial['memory_usage']
            }
        }
        
        # Determine if reconciliation was likely active
        status_changes = sum(abs(v) for v in changes['task_status_changes'].values())
        changes['reconciliation_activity_detected'] = status_changes > 0
        
        return changes
    
    def _calculate_zombie_detection_rate(self, changes: Dict) -> float:
        """Calculate the rate at which zombie processes were detected"""
        killed_count = len(self.process_sim.killed_processes)
        if killed_count == 0:
            return 0.0
        
        # Look for tasks that changed from running to error/finished
        detected_changes = abs(changes['task_status_changes'].get('running', 0))
        return (detected_changes / killed_count) * 100 if killed_count > 0 else 0.0
    
    def cleanup_simulation(self) -> bool:
        """Clean up all simulation resources"""
        try:
            self.logger.info("Cleaning up system simulation...")
            
            # Clean up network rules
            self.network_sim.cleanup_all_rules()
            
            # Clean up any test data
            self.db.cleanup_all_test_data()
            
            self.logger.info("System simulation cleanup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Simulation cleanup failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='System-level simulation for reconciliation testing')
    parser.add_argument('--scenario', choices=['disconnect', 'zombie', 'mixed'],
                       help='Type of scenario to simulate')
    parser.add_argument('--duration', type=int, default=30,
                       help='Duration of disconnection simulation in seconds')
    parser.add_argument('--check-sudo', action='store_true',
                       help='Check if we have the required privileges for network simulation')
    parser.add_argument('--cleanup-only', action='store_true',
                       help='Only perform cleanup operations')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually doing it')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--master-url', default='http://localhost:8080',
                       help='Crawlab master URL')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger('system-simulation')
    
    if args.check_sudo:
        logger.info("Checking system privileges for network simulation...")
        net_sim = NetworkSimulator()
        if net_sim.requires_sudo:
            logger.warning("⚠️  Network simulation requires sudo privileges")
            logger.info("Run with: sudo python3 system-simulation.py --scenario disconnect")
        else:
            logger.info("✅ Network simulation privileges available")
        return
    
    if not any([args.scenario, args.cleanup_only]):
        parser.print_help()
        logger.info("\n💡 Tip: Use --check-sudo to verify privileges for network simulation")
        return
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No actual changes will be made")
        return
    
    try:
        # Load configuration
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        config = load_config(config_file)
        
        # Initialize components
        api_client = CrawlabAPIClient(args.master_url)
        try:
            api_client.ensure_authenticated()
            logger.info("✅ Successfully authenticated with Crawlab API")
        except Exception as e:
            logger.warning(f"⚠️  API authentication failed: {e}")
            logger.info("Continuing with system-level simulation only")
        
        db_helper = DatabaseHelper(config['mongodb']['uri'])
        db_helper.database_name = config['mongodb']['database']
        db_helper.connect()
        
        simulator = SystemSimulator(api_client, db_helper)
        
        if args.cleanup_only:
            success = simulator.cleanup_simulation()
            sys.exit(0 if success else 1)
        
        # Run realistic system simulation
        logger.info(f"🚀 Starting realistic {args.scenario} simulation...")
        
        if args.scenario == 'disconnect':
            logger.info("🌐 Using network-level disconnection simulation")
            result = simulator.simulate_worker_disconnection(args.duration)
        elif args.scenario == 'zombie':
            logger.info("💀 Using process-level zombie simulation")
            result = simulator.simulate_zombie_processes()
        elif args.scenario == 'mixed':
            logger.info("🔄 Using combined network and process simulation")
            result = simulator.simulate_mixed_scenario()
        
        # Report results
        logger.info("📊 Simulation Results:")
        logger.info("=" * 50)
        
        if result.get('reconciliation_triggered'):
            logger.info("✅ Reconciliation service responded to the simulation")
        else:
            logger.info("⚠️  No clear reconciliation activity detected")
        
        if args.scenario == 'zombie':
            detection_rate = result.get('zombie_detection_rate', 0)
            logger.info(f"🎯 Zombie detection rate: {detection_rate:.1f}%")
            if detection_rate >= 80:
                logger.info("✅ Excellent zombie detection")
            elif detection_rate >= 50:
                logger.info("⚠️  Moderate zombie detection")
            else:
                logger.info("❌ Poor zombie detection")
        
        total_duration = result.get('total_duration', 0)
        logger.info(f"⏱️  Total simulation time: {total_duration:.1f}s")
        
        # Cleanup
        logger.info("\n🧹 Cleaning up simulation...")
        simulator.cleanup_simulation()
        
        logger.info("✅ System simulation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Simulation interrupted by user")
        try:
            simulator.cleanup_simulation()
        except:
            pass
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        try:
            simulator.cleanup_simulation()
        except:
            pass
        sys.exit(1)

if __name__ == '__main__':
    main()