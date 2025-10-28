#!/usr/bin/env python3
"""
Quick Pressure Test Launcher

Convenient wrapper for running pressure tests with common configurations.
"""

import sys
import os
import subprocess
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_command(cmd, description):
    """Run a command and display output."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Quick launcher for Crawlab pressure tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick smoke test
  %(prog)s --quick
  
  # Standard capacity test
  %(prog)s --standard
  
  # Full stress test
  %(prog)s --stress
  
  # Custom configuration
  %(prog)s --custom --load heavy --monitor
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--quick', action='store_true',
                      help='Quick smoke test (light load, no monitoring)')
    group.add_argument('--standard', action='store_true',
                      help='Standard capacity test (heavy load with monitoring)')
    group.add_argument('--stress', action='store_true',
                      help='Full stress test (extreme load)')
    group.add_argument('--custom', action='store_true',
                      help='Custom configuration')
    
    parser.add_argument('--load', choices=['light', 'medium', 'heavy', 'extreme'],
                       help='Load level (for custom mode)')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor execution (for custom mode)')
    parser.add_argument('--output', help='Save results to file')
    
    args = parser.parse_args()
    
    # Get the test runner path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    runner_path = os.path.join(script_dir, '..', 'runners', 'scheduler', 
                               'SCH-002_task_execution_pressure_test.py')
    
    # Build command
    base_cmd = f"python {runner_path}"
    
    if args.quick:
        cmd = f"{base_cmd} --load light --no-monitor"
        description = "Quick Smoke Test (100 tasks)"
    elif args.standard:
        cmd = f"{base_cmd} --load heavy --monitor"
        description = "Standard Capacity Test (1000 tasks)"
    elif args.stress:
        cmd = f"{base_cmd} --load extreme --monitor"
        description = "Full Stress Test (5000 tasks)"
    elif args.custom:
        if not args.load:
            print("Error: --load required for custom mode")
            return 1
        
        cmd = f"{base_cmd} --load {args.load}"
        if args.monitor:
            cmd += " --monitor"
        description = f"Custom Test ({args.load} load)"
    else:
        # Default to standard
        cmd = f"{base_cmd} --load heavy --monitor"
        description = "Standard Capacity Test (1000 tasks)"
    
    # Add output if specified
    if args.output:
        cmd += f" --output {args.output}"
    
    # Run the test
    success = run_command(cmd, description)
    
    if success:
        print("\n✅ Pressure test completed successfully!")
        return 0
    else:
        print("\n❌ Pressure test failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
