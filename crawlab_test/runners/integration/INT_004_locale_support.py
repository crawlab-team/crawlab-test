#!/usr/bin/env python3
"""
SYS-001: Chinese Locale Support Validation Runner

This runner validates that Docker containers properly support Chinese locale (zh_CN.UTF-8)
for applications that need to display Chinese characters in screenshots, logs, or UI elements.
"""

import sys
import logging
import argparse
from pathlib import Path

# Add tests directory to path for imports
TESTS_ROOT = Path(__file__).resolve().parent.parent.parent
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from crawlab_test.helpers.testing.validators.locale_validator import LocaleValidator
from crawlab_test.helpers.infrastructure.utils import setup_logging

def run_sys_001_test(container_name: str = "master", verbose: bool = False, 
                     include_browsers: bool = True) -> bool:
    """
    Execute SYS-001 Chinese Locale Support Validation test
    
    Args:
        container_name: Target container to test (default: "master")
        verbose: Enable detailed logging
        include_browsers: Include browser-specific tests (Playwright/Selenium)
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("SYS-001: Chinese Locale Support Validation")
    if include_browsers:
        logger.info("Including browser-specific tests (Playwright/Selenium)")
    logger.info("=" * 60)
    
    try:
        # Initialize the locale validator
        validator = LocaleValidator()
        
        # Step 1: Verify Chinese Locale Installation
        logger.info("Step 1: Verifying Chinese locale installation...")
        locale_check = validator.check_locale(container_name)
        
        # Step 2: Test Chinese Character Display
        logger.info("Step 2: Testing Chinese character display...")
        display_check = validator.test_character_display(container_name)
        
        # Step 3: Validate Font Support
        logger.info("Step 3: Validating Chinese font support...")
        font_check = validator.check_fonts(container_name)
        
        # Step 4: Test Application Screenshot Scenario
        logger.info("Step 4: Testing screenshot scenario with Chinese text...")
        screenshot_check = validator.screenshot_test(container_name)
        
        # Step 5: Verify Environment Variables
        logger.info("Step 5: Verifying locale environment variables...")
        env_check = validator.check_environment(container_name)
        
        # Collect results
        results = {
            'locale_installation': locale_check,
            'character_display': display_check,
            'font_support': font_check,
            'screenshot_test': screenshot_check,
            'environment_variables': env_check
        }
        
        # Browser-specific tests
        if include_browsers:
            logger.info("\n" + "=" * 60)
            logger.info("BROWSER-SPECIFIC TESTS")
            logger.info("=" * 60)
            
            # Step 6: Check Browser Fonts
            logger.info("Step 6: Checking browser-accessible Chinese fonts...")
            browser_fonts_check = validator.check_browser_fonts(container_name)
            results['browser_fonts'] = browser_fonts_check
            
            # Step 7: Test Playwright Chinese Support
            logger.info("Step 7: Testing Playwright Chinese rendering...")
            playwright_check = validator.check_playwright_chinese_support(container_name)
            results['playwright_chinese'] = playwright_check
            
            # Step 8: Test Selenium Chinese Support
            logger.info("Step 8: Testing Selenium Chinese rendering...")
            selenium_check = validator.check_selenium_chinese_support(container_name)
            results['selenium_chinese'] = selenium_check
        
        # Summary
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        logger.info("=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        logger.info("-" * 60)
        logger.info(f"Overall: {passed_tests}/{total_tests} tests passed")
        
        # Success criteria check
        all_passed = passed_tests == total_tests
        
        if all_passed:
            logger.info("🎉 SYS-001 Chinese Locale Support Validation: PASSED")
            logger.info("All Chinese locale support requirements are met!")
        else:
            logger.error("❌ SYS-001 Chinese Locale Support Validation: FAILED")
            logger.error(f"{total_tests - passed_tests} critical tests failed")
            
            # Provide specific failure guidance
            if not results['locale_installation']:
                logger.error("- Chinese locale (zh_CN.UTF-8) is not installed")
                logger.error("  Action: Check base image locale generation in deps.sh")
            
            if not results['font_support']:
                logger.error("- Chinese fonts are not available")
                logger.error("  Action: Verify fonts-wqy-zenhei and fonts-noto-cjk installation")
            
            if not results['environment_variables']:
                logger.error("- Locale environment variables not properly configured")
                logger.error("  Action: Check LC_CTYPE and LANG environment variables")
            
            if include_browsers:
                if not results.get('browser_fonts', True):
                    logger.error("- Browser-accessible Chinese fonts not found")
                    logger.error("  Action: Ensure fonts are in /usr/share/fonts/")
                
                if not results.get('playwright_chinese', True):
                    logger.error("- Playwright Chinese rendering failed")
                    logger.error("  Action: Check Playwright installation and browser dependencies")
                
                if not results.get('selenium_chinese', True):
                    logger.error("- Selenium Chinese rendering failed")
                    logger.error("  Action: Check Selenium and ChromeDriver installation")
        
        logger.info("=" * 60)
        
        return all_passed
        
    except Exception as e:
        logger.error(f"Test execution failed with error: {e}")
        logger.error("This may indicate a configuration or environment issue")
        return False

def main():
    parser = argparse.ArgumentParser(description="SYS-001 Chinese Locale Support Validation Runner")
    parser.add_argument('--container', default='master',
                       help='Container name to test (default: master)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--spec', help='Path to test specification (for compatibility)')
    parser.add_argument('--ci', action='store_true',
                       help='CI mode - stricter validation')
    parser.add_argument('--skip-browsers', action='store_true',
                       help='Skip browser-specific tests (Playwright/Selenium)')
    
    args = parser.parse_args()
    
    try:
        success = run_sys_001_test(
            container_name=args.container,
            verbose=args.verbose,
            include_browsers=not args.skip_browsers
        )
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Runner failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()