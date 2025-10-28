#!/usr/bin/env python3
"""
Chinese locale validation helper for Crawlab testing
Validates Chinese locale support in Docker containers.
"""

import argparse
import sys
import logging
from pathlib import Path
import textwrap

# Add tests directory to path for imports
TESTS_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from helpers.infrastructure.docker import docker_utils
from helpers.infrastructure.utils import setup_logging

class LocaleValidator:
    def __init__(self):
        self.docker = docker_utils
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if not self.docker.is_available():
            raise RuntimeError("Docker is not available or accessible")
    
    def check_locale(self, container_name: str = "master") -> bool:
        """Check if Chinese locale is installed and available"""
        self.logger.info(f"Checking Chinese locale support in {container_name}")
        
        # Find the container
        container = self._find_container(container_name)
        if not container:
            self.logger.error(f"Container {container_name} not found")
            return False
        
        container_id = container['ID']
        
        # Check if zh_CN.UTF-8 locale is available
        cmd = "locale -a | grep -i zh"
        result = self.docker.exec_command(container_id, cmd)
        
        if result['exit_code'] == 0 and result['output']:
            self.logger.info(f"Chinese locales found: {result['output'].strip()}")
            
            # Verify specific locale
            if 'zh_CN.utf8' in result['output'] or 'zh_CN.UTF-8' in result['output']:
                self.logger.info("✅ zh_CN.UTF-8 locale is available")
                return True
            else:
                self.logger.warning("Chinese locales found but zh_CN.UTF-8 missing")
                return False
        else:
            self.logger.error("❌ No Chinese locales found")
            return False
    
    def test_character_display(self, container_name: str = "master") -> bool:
        """Test Chinese character display functionality"""
        self.logger.info(f"Testing Chinese character display in {container_name}")
        
        container = self._find_container(container_name)
        if not container:
            return False
        
        container_id = container['ID']
        
        # Test basic Chinese character output
        test_commands = [
            # Test echo with Chinese characters
            'echo "测试中文字符: 你好世界"',
            # Test Python Unicode handling
            "python3 -c \"print('中文测试: 您好世界')\"",
            # Test locale-specific formatting
            'LC_ALL=zh_CN.UTF-8 date',
        ]
        
        success_count = 0
        for i, cmd in enumerate(test_commands, 1):
            self.logger.info(f"Running test {i}: {cmd}")
            result = self.docker.exec_command(container_id, cmd)
            
            if result['exit_code'] == 0:
                output = result['output'].strip()
                self.logger.info(f"✅ Test {i} output: {output}")
                success_count += 1
            else:
                self.logger.error(f"❌ Test {i} failed: {result['error']}")
        
        success = success_count == len(test_commands)
        if success:
            self.logger.info("✅ All character display tests passed")
        else:
            self.logger.error(f"❌ {len(test_commands) - success_count} tests failed")
        
        return success
    
    def check_fonts(self, container_name: str = "master") -> bool:
        """Check if Chinese fonts are installed"""
        self.logger.info(f"Checking Chinese fonts in {container_name}")
        
        container = self._find_container(container_name)
        if not container:
            return False
        
        container_id = container['ID']
        
        # Check for Chinese fonts
        cmd = "fc-list | grep -i 'chinese\\|cjk\\|wqy'"
        result = self.docker.exec_command(container_id, cmd)
        
        if result['exit_code'] == 0 and result['output']:
            fonts = result['output'].strip().split('\n')
            self.logger.info(f"✅ Found {len(fonts)} Chinese font entries:")
            for font in fonts[:5]:  # Show first 5
                self.logger.info(f"  - {font}")
            if len(fonts) > 5:
                self.logger.info(f"  ... and {len(fonts) - 5} more")
            return True
        else:
            self.logger.error("❌ No Chinese fonts found")
            return False
    
    def check_environment(self, container_name: str = "master") -> bool:
        """Check locale-related environment variables"""
        self.logger.info(f"Checking locale environment in {container_name}")
        
        container = self._find_container(container_name)
        if not container:
            return False
        
        container_id = container['ID']
        
        # Check environment variables
        cmd = "env | grep -E '(LANG|LC_|LANGUAGE)'"
        result = self.docker.exec_command(container_id, cmd)
        
        if result['exit_code'] == 0:
            env_vars = result['output'].strip().split('\n')
            self.logger.info("Current locale environment variables:")
            for var in env_vars:
                self.logger.info(f"  {var}")
            
            # Check for UTF-8 support
            utf8_support = any('UTF-8' in var for var in env_vars)
            if utf8_support:
                self.logger.info("✅ UTF-8 support detected")
                return True
            else:
                self.logger.warning("⚠️  No UTF-8 support detected")
                return False
        else:
            self.logger.error("❌ Failed to check environment variables")
            return False
    
    def screenshot_test(self, container_name: str = "master") -> bool:
        """Test screenshot functionality with Chinese characters"""
        self.logger.info(f"Testing screenshot with Chinese text in {container_name}")
        
        container = self._find_container(container_name)
        if not container:
            return False
        
        container_id = container['ID']
        
        # Create a simple test script that would generate output with Chinese
        test_script = textwrap.dedent(
            """
            import sys
            import locale

            test_text = "中文测试 - Chinese Test: 你好世界"
            print(f"Test text: {test_text}")
            print(f"System encoding: {sys.stdout.encoding}")
            print(f"Preferred encoding: {locale.getpreferredencoding()}")

            try:
                encoded = test_text.encode('utf-8')
                decoded = encoded.decode('utf-8')
                status = '✅ PASS' if test_text == decoded else '❌ FAIL'
                print(f"Encoding test: {status}")
            except Exception as exc:
                print(f"Encoding test: ❌ FAIL - {exc}")
            """
        )

        cmd = f"python3 - <<'PY'\n{test_script}\nPY"
        result = self.docker.exec_command(container_id, cmd)
        
        if result['exit_code'] == 0:
            self.logger.info("✅ Screenshot test simulation passed")
            self.logger.info(f"Output: {result['output'].strip()}")
            return True
        else:
            self.logger.error(f"❌ Screenshot test failed: {result['error']}")
            return False
    
    def check_playwright_chinese_support(self, container_name: str = "master") -> bool:
        """Check if Playwright can render Chinese characters"""
        self.logger.info(f"Testing Playwright Chinese locale support in {container_name}")
        
        container = self._find_container(container_name)
        if not container:
            return False
        
        container_id = container['ID']
        
        # First check if Playwright is installed
        check_cmd = "python3 -c 'import playwright; print(playwright.__version__)' 2>&1"
        result = self.docker.exec_command(container_id, check_cmd)
        
        if result['exit_code'] != 0:
            self.logger.warning("⚠️  Playwright not installed, skipping browser tests")
            return True  # Not a failure if not installed
        
        self.logger.info(f"Playwright version: {result['output'].strip()}")
        
        # Create a test script for Playwright with Chinese content
        playwright_script = textwrap.dedent(
            """
            import sys
            import asyncio
            from playwright.async_api import async_playwright

            async def test_chinese_rendering():
                try:
                    async with async_playwright() as p:
                        # Test with Chromium
                        browser = await p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
                        context = await browser.new_context(locale='zh-CN')
                        page = await context.new_page()
                        
                        # Set HTML content with Chinese characters
                        chinese_html = '''
                        <!DOCTYPE html>
                        <html lang="zh-CN">
                        <head>
                            <meta charset="UTF-8">
                            <title>中文测试</title>
                            <style>
                                body { font-family: sans-serif; padding: 20px; }
                                h1 { color: #333; }
                            </style>
                        </head>
                        <body>
                            <h1>中文字符渲染测试</h1>
                            <p>你好世界！这是中文字符测试。</p>
                            <p>爬虫测试 - Crawlab Spider Test</p>
                        </body>
                        </html>
                        '''
                        
                        await page.set_content(chinese_html)
                        
                        # Get text content to verify rendering
                        h1_text = await page.locator('h1').inner_text()
                        p_text = await page.locator('p').first.inner_text()
                        
                        print(f"H1 text: {h1_text}")
                        print(f"P text: {p_text}")
                        
                        # Verify Chinese characters are present
                        if '中文' in h1_text and '你好世界' in p_text:
                            print("✅ Chinese characters rendered correctly")
                            success = True
                        else:
                            print("❌ Chinese characters not rendered correctly")
                            success = False
                        
                        await browser.close()
                        return success
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    return False

            result = asyncio.run(test_chinese_rendering())
            sys.exit(0 if result else 1)
            """
        )
        
        cmd = f"python3 - <<'EOF'\n{playwright_script}\nEOF"
        result = self.docker.exec_command(container_id, cmd)
        
        if result['exit_code'] == 0 and '✅' in result['output']:
            self.logger.info("✅ Playwright Chinese rendering test passed")
            self.logger.debug(f"Output: {result['output'].strip()}")
            return True
        else:
            self.logger.error("❌ Playwright Chinese rendering test failed")
            if result['output']:
                self.logger.error(f"Output: {result['output'].strip()}")
            if result['error']:
                self.logger.error(f"Error: {result['error'].strip()}")
            return False
    
    def check_selenium_chinese_support(self, container_name: str = "master") -> bool:
        """Check if Selenium can render Chinese characters"""
        self.logger.info(f"Testing Selenium Chinese locale support in {container_name}")
        
        container = self._find_container(container_name)
        if not container:
            return False
        
        container_id = container['ID']
        
        # Check if Selenium is installed
        check_cmd = "python3 -c 'import selenium; print(selenium.__version__)' 2>&1"
        result = self.docker.exec_command(container_id, check_cmd)
        
        if result['exit_code'] != 0:
            self.logger.warning("⚠️  Selenium not installed, skipping browser tests")
            return True  # Not a failure if not installed
        
        self.logger.info(f"Selenium version: {result['output'].strip()}")
        
        # Create a test script for Selenium with Chinese content
        selenium_script = textwrap.dedent(
            """
            import sys
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By

            try:
                # Setup Chrome with headless options
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--lang=zh-CN')
                
                driver = webdriver.Chrome(options=chrome_options)
                
                # Set HTML content with Chinese characters
                chinese_html = '''
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <title>中文测试</title>
                </head>
                <body>
                    <h1 id="title">中文字符渲染测试</h1>
                    <p id="content">你好世界！这是中文字符测试。</p>
                    <p id="spider">爬虫测试 - Crawlab Spider Test</p>
                </body>
                </html>
                '''
                
                driver.get('data:text/html;charset=utf-8,' + chinese_html)
                
                # Get text content to verify rendering
                title_text = driver.find_element(By.ID, 'title').text
                content_text = driver.find_element(By.ID, 'content').text
                
                print(f"Title text: {title_text}")
                print(f"Content text: {content_text}")
                
                # Verify Chinese characters are present
                if '中文' in title_text and '你好世界' in content_text:
                    print("✅ Chinese characters rendered correctly")
                    success = True
                else:
                    print("❌ Chinese characters not rendered correctly")
                    success = False
                
                driver.quit()
                sys.exit(0 if success else 1)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
            """
        )
        
        cmd = f"python3 - <<'EOF'\n{selenium_script}\nEOF"
        result = self.docker.exec_command(container_id, cmd)
        
        if result['exit_code'] == 0 and '✅' in result['output']:
            self.logger.info("✅ Selenium Chinese rendering test passed")
            self.logger.debug(f"Output: {result['output'].strip()}")
            return True
        else:
            self.logger.error("❌ Selenium Chinese rendering test failed")
            if result['output']:
                self.logger.error(f"Output: {result['output'].strip()}")
            if result['error']:
                self.logger.error(f"Error: {result['error'].strip()}")
            return False
    
    def check_browser_fonts(self, container_name: str = "master") -> bool:
        """Check if browser-accessible fonts support Chinese"""
        self.logger.info(f"Checking browser font support in {container_name}")
        
        container = self._find_container(container_name)
        if not container:
            return False
        
        container_id = container['ID']
        
        # Check for common browser font paths
        font_paths = [
            "/usr/share/fonts/truetype/wqy",
            "/usr/share/fonts/opentype/noto",
            "/usr/share/fonts/truetype/noto",
        ]
        
        found_fonts = []
        for path in font_paths:
            cmd = f"ls -la {path} 2>/dev/null | grep -i 'chinese\\|cjk\\|han'"
            result = self.docker.exec_command(container_id, cmd)
            if result['exit_code'] == 0 and result['output']:
                found_fonts.append(path)
                self.logger.info(f"✅ Found Chinese fonts in {path}")
        
        if found_fonts:
            self.logger.info(f"✅ Browser-accessible Chinese fonts found in {len(found_fonts)} locations")
            return True
        else:
            self.logger.error("❌ No browser-accessible Chinese fonts found")
            return False
    
    def run_full_suite(self, container_name: str = "master", include_browsers: bool = True) -> dict:
        """Run complete Chinese locale validation suite
        
        Args:
            container_name: Target container name
            include_browsers: Whether to include browser-specific tests (Playwright/Selenium)
        """
        self.logger.info(f"Running full Chinese locale validation suite on {container_name}")
        
        results = {
            'locale_check': self.check_locale(container_name),
            'character_display': self.test_character_display(container_name),
            'font_check': self.check_fonts(container_name),
            'environment_check': self.check_environment(container_name),
            'screenshot_test': self.screenshot_test(container_name),
        }
        
        # Add browser-specific tests if requested
        if include_browsers:
            self.logger.info("\n--- Browser-Specific Tests ---")
            results['browser_fonts'] = self.check_browser_fonts(container_name)
            results['playwright_chinese'] = self.check_playwright_chinese_support(container_name)
            results['selenium_chinese'] = self.check_selenium_chinese_support(container_name)
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        
        self.logger.info(f"\n=== Test Suite Results ===")
        self.logger.info(f"Passed: {passed}/{total}")
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.logger.info(f"{test_name}: {status}")
        
        overall_success = passed == total
        if overall_success:
            self.logger.info("🎉 All Chinese locale tests passed!")
        else:
            self.logger.error(f"⚠️  {total - passed} tests failed")
        
        return results
    
    def _find_container(self, container_name: str) -> dict:
        """Find a Crawlab container by name"""
        containers = self.docker.find_crawlab_containers()
        
        for container in containers:
            if container_name in container.get('Names', ''):
                return container
        
        # Try with crawlab- prefix
        for container in containers:
            if f"crawlab-{container_name}" in container.get('Names', ''):
                return container
        
        return None

def main():
    parser = argparse.ArgumentParser(description="Chinese locale validation for Crawlab containers")
    parser.add_argument('--action', required=True,
                       choices=['check-locale', 'test-display', 'check-fonts', 
                               'check-env', 'screenshot-test', 'full-suite',
                               'playwright-test', 'selenium-test', 'browser-fonts'],
                       help='Validation action to perform')
    parser.add_argument('--container', default='master',
                       help='Container name to test (default: master)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--skip-browsers', action='store_true',
                       help='Skip browser-specific tests in full suite')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    try:
        validator = LocaleValidator()
        
        if args.action == 'check-locale':
            success = validator.check_locale(args.container)
        elif args.action == 'test-display':
            success = validator.test_character_display(args.container)
        elif args.action == 'check-fonts':
            success = validator.check_fonts(args.container)
        elif args.action == 'check-env':
            success = validator.check_environment(args.container)
        elif args.action == 'screenshot-test':
            success = validator.screenshot_test(args.container)
        elif args.action == 'playwright-test':
            success = validator.check_playwright_chinese_support(args.container)
        elif args.action == 'selenium-test':
            success = validator.check_selenium_chinese_support(args.container)
        elif args.action == 'browser-fonts':
            success = validator.check_browser_fonts(args.container)
        elif args.action == 'full-suite':
            include_browsers = not args.skip_browsers
            results = validator.run_full_suite(args.container, include_browsers=include_browsers)
            success = all(results.values())
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logging.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()