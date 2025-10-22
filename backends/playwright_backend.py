"""
Playwright Backend

This backend executes UI tests using TypeScript Playwright framework.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from .base import TestBackend


class PlaywrightBackend(TestBackend):
    """Backend for executing Playwright UI tests"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize PlaywrightBackend
        
        Args:
            base_dir: Base directory for tests (defaults to tests directory)
        """
        if base_dir is None:
            # Default to tests directory (parent of backends)
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.playwright_dir = self.base_dir / "ui-playwright"
        self.results_dir = self.base_dir / "results"
    
    def get_name(self) -> str:
        """Get backend name"""
        return "playwright"
    
    def get_description(self) -> str:
        """Get backend description"""
        return "TypeScript Playwright UI testing backend"
    
    def check_prerequisites(self) -> bool:
        """Check if Node.js and pnpm are available"""
        try:
            # Check Node.js
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print("Error: Node.js not found. Please install Node.js 18+")
                return False
            
            # Check pnpm
            result = subprocess.run(
                ['pnpm', '--version'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print("Error: pnpm not found. Install with: npm install -g pnpm")
                return False
            
            return True
            
        except FileNotFoundError:
            print("Error: Node.js or pnpm not found in PATH")
            return False
    
    def supports_spec(self, spec_path: Path) -> bool:
        """Check if this is a UI test spec"""
        # Check if category is UI
        try:
            parts = spec_path.parts
            specs_index = parts.index('specs')
            if specs_index + 1 < len(parts):
                category = parts[specs_index + 1]
                return category == 'ui'
        except (ValueError, IndexError):
            pass
        
        return False
    
    def execute(self, spec_path: Path, config: Dict) -> Dict:
        """
        Execute Playwright tests
        
        Args:
            spec_path: Path to test specification
            config: Configuration dictionary
            
        Returns:
            Result dictionary
        """
        result = {
            "backend": self.get_name(),
            "spec_path": str(spec_path),
            "start_time": datetime.now().isoformat(),
            "status": "unknown",
        }
        
        if not self.playwright_dir.exists():
            result["status"] = "error"
            result["error"] = f"Playwright directory not found: {self.playwright_dir}"
            return result
        
        print(f"Executing Playwright tests for: {spec_path}")
        
        # Install dependencies if needed
        if not self._check_dependencies_installed():
            print("Installing dependencies...")
            if not self._install_dependencies():
                result["status"] = "error"
                result["error"] = "Failed to install dependencies"
                return result
        
        # Install browsers if needed
        if not self._install_browsers():
            print("Warning: Browser installation had issues, continuing anyway")
        
        # Run tests
        test_name = spec_path.stem
        success = self._run_tests(test_name, config)
        
        # Parse results
        parsed_results = self._parse_results()
        result.update(parsed_results)
        
        result["end_time"] = datetime.now().isoformat()
        return result
    
    def _check_dependencies_installed(self) -> bool:
        """Check if node_modules exists"""
        return (self.playwright_dir / "node_modules").exists()
    
    def _install_dependencies(self) -> bool:
        """Install pnpm dependencies"""
        try:
            result = subprocess.run(
                ['pnpm', 'install'],
                cwd=self.playwright_dir,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Failed to install dependencies: {result.stderr}")
                return False
            
            print("Dependencies installed successfully")
            return True
            
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def _install_browsers(self) -> bool:
        """Install Playwright browsers"""
        try:
            result = subprocess.run(
                ['pnpm', 'run', 'install:browsers'],
                cwd=self.playwright_dir,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Browser installation warning: {result.stderr}")
            
            return True
            
        except Exception as e:
            print(f"Error installing browsers: {e}")
            return False
    
    def _run_tests(self, test_pattern: Optional[str], config: Dict) -> bool:
        """Execute Playwright tests"""
        cmd = ['pnpm', 'test']
        if test_pattern:
            cmd.append(test_pattern)
        
        # Set environment variables
        env = os.environ.copy()
        env['CI'] = 'true'
        env['CRAWLAB_BASE_URL'] = env.get('CRAWLAB_BASE_URL', 'http://localhost:8080')
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.playwright_dir,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Log output
            print("Test output:")
            print(result.stdout)
            
            if result.stderr:
                print("Test warnings/errors:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error running tests: {e}")
            return False
    
    def _parse_results(self) -> Dict:
        """Parse Playwright JSON results"""
        results_file = self.results_dir / 'playwright-results.json'
        
        if not results_file.exists():
            print(f"Results file not found: {results_file}")
            return {
                'status': 'error',
                'error': 'Results file not found',
                'total_steps': 0,
                'passed_steps': 0,
                'failed_steps': 0,
            }
        
        try:
            with open(results_file, 'r') as f:
                playwright_results = json.load(f)
            
            # Convert Playwright results to standard format
            suites = playwright_results.get('suites', [])
            total_tests = 0
            passed = 0
            failed = 0
            
            def count_tests(suite):
                nonlocal total_tests, passed, failed
                
                for spec in suite.get('specs', []):
                    total_tests += 1
                    
                    # Check if test passed
                    all_passed = all(
                        result.get('status') == 'passed'
                        for test in spec.get('tests', [])
                        for result in test.get('results', [])
                    )
                    
                    if all_passed:
                        passed += 1
                    else:
                        failed += 1
                
                # Recursively process nested suites
                for nested_suite in suite.get('suites', []):
                    count_tests(nested_suite)
            
            for suite in suites:
                count_tests(suite)
            
            status = 'passed' if failed == 0 else 'failed'
            
            return {
                'status': status,
                'total_steps': total_tests,
                'passed_steps': passed,
                'failed_steps': failed,
                'exit_code': 0 if status == 'passed' else 1
            }
            
        except Exception as e:
            print(f"Error parsing results: {e}")
            return {
                'status': 'error',
                'error': f'Failed to parse results: {e}',
                'total_steps': 0,
                'passed_steps': 0,
                'failed_steps': 0,
            }
