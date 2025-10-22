#!/usr/bin/env python3
"""
Database Integration Test Helper

This script provides utilities for running database integration tests,
checking database service status, and managing test data.

Features:
- Check status of all database services (MongoDB, MySQL, PostgreSQL, Elasticsearch)
- Verify mongosh CLI availability for MongoDB query tests
- Run database integration tests with proper environment configuration
- Clean up test data
- Generate test reports

Usage:
    ./database-test-helper.py check-services
    ./database-test-helper.py run-tests [--database <type>] [--test <name>]
    ./database-test-helper.py cleanup
    ./database-test-helper.py report
"""

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

# Database configuration
# Note: MSSQL Server is excluded from integration tests as it is not a primary supported database
DATABASE_CONFIGS = {
    'mongo': {
        'name': 'MongoDB',
        'host': 'localhost',
        'port': 27017,
        'check_command': ['mongosh', '--host', 'localhost:27017', '-u', 'admin', '-p', 'admin', '--authenticationDatabase', 'admin', '--eval', 'db.adminCommand("ping")'],
    },
    'mysql': {
        'name': 'MySQL',
        'host': 'localhost',
        'port': 3307,
        'check_command': ['mysql', '-h', 'localhost', '-P', '3307', '-u', 'root', '-padmin', '-e', 'SELECT 1'],
    },
    'postgres': {
        'name': 'PostgreSQL',
        'host': 'localhost',
        'port': 5433,
        'check_command': ['psql', '-h', 'localhost', '-p', '5433', '-U', 'admin', '-c', 'SELECT 1'],
    },
    # 'mssql': {  # DISABLED: Not a primary supported database for integration tests
    #     'name': 'MSSQL Server',
    #     'host': 'localhost',
    #     'port': 1434,
    #     'check_command': ['sqlcmd', '-S', 'localhost,1434', '-U', 'sa', '-P', 'Admin123456', '-Q', 'SELECT 1'],
    # },
    'elasticsearch': {
        'name': 'Elasticsearch',
        'host': 'localhost',
        'port': 9200,
        'check_command': ['curl', '-s', 'http://localhost:9200/_cluster/health'],
    },
}


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def check_port(host: str, port: int, timeout: int = 5) -> bool:
    """Check if a port is open"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_mongosh_available() -> bool:
    """Check if mongosh CLI is available"""
    try:
        result = subprocess.run(['mongosh', '--version'], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_database_service(db_type: str, config: Dict) -> Tuple[bool, str]:
    """
    Check if a database service is running and accessible
    
    Returns:
        Tuple of (is_running, status_message)
    """
    # First check if port is open
    if not check_port(config['host'], config['port']):
        return False, f"Port {config['port']} is not accessible"
    
    # Try service-specific check command
    try:
        result = subprocess.run(
            config['check_command'],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'PGPASSWORD': 'admin'}  # For postgres
        )
        
        if result.returncode == 0:
            return True, "Service is running and accessible"
        else:
            return False, f"Service check failed: {result.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return False, "Service check timed out"
    except FileNotFoundError:
        # CLI tool not found, but port is open
        return True, "Port is open (CLI tool not found for verification)"
    except Exception as e:
        return False, f"Check failed: {str(e)[:100]}"


def check_all_services() -> Dict[str, bool]:
    """
    Check status of all database services
    
    Returns:
        Dictionary mapping database type to status (True if running)
    """
    print_header("Checking Database Services")
    
    statuses = {}
    for db_type, config in DATABASE_CONFIGS.items():
        print(f"\nChecking {config['name']}...")
        is_running, message = check_database_service(db_type, config)
        statuses[db_type] = is_running
        
        if is_running:
            print_success(f"{config['name']}: {message}")
        else:
            print_error(f"{config['name']}: {message}")
    
    # Summary
    print_header("Summary")
    running_count = sum(statuses.values())
    total_count = len(statuses)
    
    if running_count == total_count:
        print_success(f"All {total_count} database services are running")
    else:
        print_warning(f"{running_count}/{total_count} database services are running")
        print_info("\nTo start missing services:")
        print_info("  docker-compose -f tests/docker-compose.test.yml up -d")
    
    # Check mongosh availability
    print("\n")
    print_info("Checking MongoDB Shell (mongosh) availability...")
    if check_mongosh_available():
        print_success("mongosh is installed and available")
    else:
        print_warning("mongosh is not installed - some MongoDB query tests may be skipped")
        print_info("\nTo install mongosh:")
        print_info("  # Ubuntu/Debian:")
        print_info("  wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -")
        print_info("  echo 'deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list")
        print_info("  sudo apt-get update && sudo apt-get install -y mongodb-mongosh")
        print_info("")
        print_info("  # macOS:")
        print_info("  brew install mongosh")
        print_info("")
        print_info("  # Or download from: https://www.mongodb.com/try/download/shell")
    
    return statuses


def run_database_tests(database: Optional[str] = None, test_name: Optional[str] = None, 
                       verbose: bool = True, timeout: int = 1800) -> bool:
    """
    Run database integration tests
    
    Args:
        database: Specific database type to test (e.g., 'mysql', 'mongo')
        test_name: Specific test function to run
        verbose: Print detailed output
        timeout: Test timeout in seconds (default 30 minutes)
    
    Returns:
        True if tests passed, False otherwise
    """
    print_header("Running Database Integration Tests")
    
    # Check if we're in the right directory
    if not os.path.exists('core/database'):
        print_error("Must be run from project root directory")
        return False
    
    # Set environment variables for database connections
    print_info("Setting up database connection environment variables...")
    os.environ['MONGO_TEST_HOST'] = 'localhost'
    os.environ['MONGO_TEST_PORT'] = '27017'
    os.environ['MONGO_TEST_USER'] = 'admin'
    os.environ['MONGO_TEST_PASSWORD'] = 'admin'
    os.environ['MONGO_TEST_DB'] = 'test'
    
    os.environ['MYSQL_TEST_HOST'] = 'localhost'
    os.environ['MYSQL_TEST_PORT'] = '3307'
    os.environ['MYSQL_TEST_USER'] = 'root'
    os.environ['MYSQL_TEST_PASSWORD'] = 'admin'
    os.environ['MYSQL_TEST_DB'] = 'test'
    
    os.environ['POSTGRES_TEST_HOST'] = 'localhost'
    os.environ['POSTGRES_TEST_PORT'] = '5433'
    os.environ['POSTGRES_TEST_USER'] = 'admin'
    os.environ['POSTGRES_TEST_PASSWORD'] = 'admin'
    os.environ['POSTGRES_TEST_DB'] = 'test'
    
    os.environ['ELASTICSEARCH_TEST_HOST'] = 'localhost'
    os.environ['ELASTICSEARCH_TEST_PORT'] = '9200'
    
    # Build test command
    cmd = ['go', 'test', '-v', f'-timeout={timeout}s']
    
    if test_name:
        cmd.extend(['-run', test_name])
    elif database:
        # Map database type to service name in tests
        db_service_map = {
            'mongo': 'MongoService',
            'mysql': 'MySQLService',
            'postgres': 'PostgresService',
            # 'mssql': 'MSSQLServerService',  # DISABLED: Not a primary supported database
            'elasticsearch': 'ElasticSearchService',
        }
        service_name = db_service_map.get(database.lower())
        if service_name:
            cmd.extend(['-run', f'.*{service_name}'])
        else:
            print_error(f"Unknown database type: {database}")
            return False
    
    # Change to database directory
    os.chdir('core/database')
    
    try:
        print_info(f"Running: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, text=True, capture_output=not verbose)
        
        if result.returncode == 0:
            print_success("\nAll tests passed!")
            return True
        else:
            print_error("\nSome tests failed!")
            if not verbose and result.stdout:
                print("\n--- Test Output ---")
                print(result.stdout)
            if result.stderr:
                print("\n--- Errors ---")
                print(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print_error(f"Test execution failed: {e}")
        return False
    except KeyboardInterrupt:
        print_warning("\nTest execution interrupted by user")
        return False
    finally:
        os.chdir('../..')


def cleanup_test_data() -> None:
    """Clean up test databases and tables"""
    print_header("Cleaning Up Test Data")
    
    cleanup_sql = {
        'mysql': [
            "DROP DATABASE IF EXISTS test_drop_db;",
            "DROP DATABASE IF EXISTS test_create_db;",
        ],
        'postgres': [
            "DROP DATABASE IF EXISTS test_drop_db;",
            "DROP DATABASE IF EXISTS test_create_db;",
        ],
        # 'mssql': [  # DISABLED: Not a primary supported database
        #     "IF EXISTS(SELECT * FROM sys.databases WHERE name='test_drop_db') DROP DATABASE test_drop_db;",
        #     "IF EXISTS(SELECT * FROM sys.databases WHERE name='test_create_db') DROP DATABASE test_create_db;",
        # ],
    }
    
    for db_type, commands in cleanup_sql.items():
        config = DATABASE_CONFIGS[db_type]
        print(f"\nCleaning {config['name']}...")
        
        for cmd in commands:
            try:
                if db_type == 'mysql':
                    result = subprocess.run(
                        ['mysql', '-h', 'localhost', '-P', str(config['port']), 
                         '-u', 'root', '-padmin', '-e', cmd],
                        capture_output=True, text=True, timeout=10
                    )
                elif db_type == 'postgres':
                    result = subprocess.run(
                        ['psql', '-h', 'localhost', '-p', str(config['port']),
                         '-U', 'admin', '-c', cmd],
                        capture_output=True, text=True, timeout=10,
                        env={**os.environ, 'PGPASSWORD': 'admin'}
                    )
                # elif db_type == 'mssql':  # DISABLED: Not a primary supported database
                #     result = subprocess.run(
                #         ['sqlcmd', '-S', f'localhost,{config["port"]}',
                #          '-U', 'sa', '-P', 'Admin123456', '-Q', cmd],
                #         capture_output=True, text=True, timeout=10
                #     )
                
                if result.returncode == 0:
                    print_success(f"Executed: {cmd[:50]}...")
                else:
                    print_warning(f"Command failed (may be expected): {cmd[:50]}...")
            except Exception as e:
                print_warning(f"Cleanup failed: {str(e)[:100]}")
    
    print_success("\nCleanup completed")


def generate_report(output_file: str = 'test-report.json') -> None:
    """Generate a test report from test output"""
    print_header("Generating Test Report")
    
    # Run tests with JSON output
    os.chdir('core/database')
    try:
        result = subprocess.run(
            ['go', 'test', '-v', '-json', '-timeout=30m'],
            capture_output=True, text=True
        )
        
        # Parse JSON output
        test_results = []
        for line in result.stdout.split('\n'):
            if line.strip():
                try:
                    test_results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        
        # Analyze results
        passed = sum(1 for t in test_results if t.get('Action') == 'pass' and 'Test' in t)
        failed = sum(1 for t in test_results if t.get('Action') == 'fail' and 'Test' in t)
        skipped = sum(1 for t in test_results if t.get('Action') == 'skip' and 'Test' in t)
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total': passed + failed + skipped,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
            },
            'tests': test_results,
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print_success(f"Report saved to {output_file}")
        print_info(f"\nSummary: {passed} passed, {failed} failed, {skipped} skipped")
        
    except Exception as e:
        print_error(f"Failed to generate report: {e}")
    finally:
        os.chdir('../..')


def main():
    parser = argparse.ArgumentParser(
        description='Database Integration Test Helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check-services                    # Check all database services
  %(prog)s run-tests                         # Run all tests
  %(prog)s run-tests --database mysql        # Test only MySQL
  %(prog)s run-tests --test TestService_CRUD # Run specific test
  %(prog)s cleanup                           # Clean up test data
  %(prog)s report                            # Generate test report
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # check-services command
    subparsers.add_parser('check-services', help='Check status of all database services')
    
    # run-tests command
    test_parser = subparsers.add_parser('run-tests', help='Run database integration tests')
    test_parser.add_argument('--database', '-d', choices=['mongo', 'mysql', 'postgres', 'elasticsearch'],
                             help='Specific database type to test (note: mssql excluded as not primary supported)')
    test_parser.add_argument('--test', '-t', help='Specific test function to run')
    test_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress detailed output')
    test_parser.add_argument('--timeout', type=int, default=1800, help='Test timeout in seconds (default: 1800)')
    
    # cleanup command
    subparsers.add_parser('cleanup', help='Clean up test databases and tables')
    
    # report command
    report_parser = subparsers.add_parser('report', help='Generate test report')
    report_parser.add_argument('--output', '-o', default='test-report.json', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'check-services':
        statuses = check_all_services()
        sys.exit(0 if all(statuses.values()) else 1)
    
    elif args.command == 'run-tests':
        success = run_database_tests(
            database=args.database,
            test_name=args.test,
            verbose=not args.quiet,
            timeout=args.timeout
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'cleanup':
        cleanup_test_data()
        sys.exit(0)
    
    elif args.command == 'report':
        generate_report(args.output)
        sys.exit(0)


if __name__ == '__main__':
    main()
