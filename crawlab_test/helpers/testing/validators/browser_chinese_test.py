#!/usr/bin/env python3
"""
Standalone browser Chinese locale test script
Can be executed directly in containers to test Playwright/Selenium Chinese rendering
"""

import sys
import argparse
import logging

def test_playwright_chinese():
    """Test Playwright Chinese character rendering"""
    print("=" * 60)
    print("Testing Playwright Chinese Character Rendering")
    print("=" * 60)
    
    try:
        import asyncio
        from playwright.async_api import async_playwright
        
        async def run_test():
            try:
                async with async_playwright() as p:
                    print("Launching Chromium browser...")
                    browser = await p.chromium.launch(
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
                    
                    # Create context with Chinese locale
                    context = await browser.new_context(locale='zh-CN')
                    page = await context.new_page()
                    
                    # Test HTML with Chinese content
                    chinese_html = '''
                    <!DOCTYPE html>
                    <html lang="zh-CN">
                    <head>
                        <meta charset="UTF-8">
                        <title>中文测试</title>
                        <style>
                            body { 
                                font-family: sans-serif; 
                                padding: 20px;
                                font-size: 16px;
                            }
                            h1 { color: #333; }
                            .test-section { 
                                margin: 20px 0; 
                                padding: 10px; 
                                border: 1px solid #ddd; 
                            }
                        </style>
                    </head>
                    <body>
                        <h1 id="title">中文字符渲染测试</h1>
                        <div class="test-section">
                            <h2>基本测试</h2>
                            <p id="hello">你好世界！这是中文字符测试。</p>
                        </div>
                        <div class="test-section">
                            <h2>爬虫专用测试</h2>
                            <p id="spider">爬虫测试 - Crawlab Spider Test</p>
                            <ul>
                                <li id="task">任务执行</li>
                                <li id="schedule">定时调度</li>
                                <li id="data">数据采集</li>
                            </ul>
                        </div>
                        <div class="test-section">
                            <h2>特殊字符</h2>
                            <p id="special">繁體字測試：測試、檢查、確認</p>
                        </div>
                    </body>
                    </html>
                    '''
                    
                    print("Setting page content with Chinese text...")
                    await page.set_content(chinese_html)
                    
                    # Verify different elements
                    print("\nVerifying element contents:")
                    
                    title = await page.locator('#title').inner_text()
                    print(f"  Title: {title}")
                    
                    hello = await page.locator('#hello').inner_text()
                    print(f"  Hello: {hello}")
                    
                    spider = await page.locator('#spider').inner_text()
                    print(f"  Spider: {spider}")
                    
                    task = await page.locator('#task').inner_text()
                    print(f"  Task: {task}")
                    
                    special = await page.locator('#special').inner_text()
                    print(f"  Special: {special}")
                    
                    # Validation checks
                    checks = [
                        ('中文' in title, "Title contains Chinese"),
                        ('你好世界' in hello, "Hello message correct"),
                        ('爬虫' in spider, "Spider text correct"),
                        ('任务' in task, "Task text correct"),
                        ('繁體' in special, "Traditional Chinese supported"),
                    ]
                    
                    print("\nValidation Results:")
                    passed = 0
                    for check, description in checks:
                        status = "✅ PASS" if check else "❌ FAIL"
                        print(f"  {status}: {description}")
                        if check:
                            passed += 1
                    
                    # Take screenshot for visual verification
                    screenshot_path = '/tmp/playwright_chinese_test.png'
                    try:
                        await page.screenshot(path=screenshot_path)
                        print(f"\n📸 Screenshot saved to: {screenshot_path}")
                    except Exception as e:
                        print(f"\n⚠️  Screenshot failed: {e}")
                    
                    await browser.close()
                    
                    print(f"\n{'='*60}")
                    print(f"Playwright Test: {passed}/{len(checks)} checks passed")
                    print(f"{'='*60}")
                    
                    return passed == len(checks)
                    
            except Exception as e:
                print(f"❌ Error during test: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        result = asyncio.run(run_test())
        return result
        
    except ImportError as e:
        print(f"⚠️  Playwright not installed: {e}")
        print("Install with: pip install playwright && playwright install chromium")
        return None

def test_selenium_chinese():
    """Test Selenium Chinese character rendering"""
    print("=" * 60)
    print("Testing Selenium Chinese Character Rendering")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        
        print("Setting up Chrome with headless options...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--lang=zh-CN')
        
        print("Launching Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Test HTML with Chinese content
            chinese_html = '''
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <title>中文测试</title>
                <style>
                    body { font-family: sans-serif; padding: 20px; }
                    .section { margin: 15px 0; padding: 10px; border: 1px solid #ccc; }
                </style>
            </head>
            <body>
                <h1 id="title">中文字符渲染测试</h1>
                <div class="section">
                    <h2>基本测试</h2>
                    <p id="content">你好世界！这是中文字符测试。</p>
                </div>
                <div class="section">
                    <h2>爬虫测试</h2>
                    <p id="spider">爬虫测试 - Crawlab Spider Test</p>
                    <ul>
                        <li id="node">节点管理</li>
                        <li id="task">任务执行</li>
                        <li id="schedule">定时调度</li>
                    </ul>
                </div>
            </body>
            </html>
            '''
            
            print("Loading HTML content with Chinese text...")
            # Use data URI to load HTML directly
            import urllib.parse
            html_encoded = urllib.parse.quote(chinese_html)
            driver.get(f'data:text/html;charset=utf-8,{html_encoded}')
            
            # Give time for rendering
            import time
            time.sleep(1)
            
            print("\nVerifying element contents:")
            
            title_text = driver.find_element(By.ID, 'title').text
            print(f"  Title: {title_text}")
            
            content_text = driver.find_element(By.ID, 'content').text
            print(f"  Content: {content_text}")
            
            spider_text = driver.find_element(By.ID, 'spider').text
            print(f"  Spider: {spider_text}")
            
            node_text = driver.find_element(By.ID, 'node').text
            print(f"  Node: {node_text}")
            
            # Validation checks
            checks = [
                ('中文' in title_text, "Title contains Chinese"),
                ('你好世界' in content_text, "Content message correct"),
                ('爬虫' in spider_text, "Spider text correct"),
                ('节点' in node_text, "Node text correct"),
            ]
            
            print("\nValidation Results:")
            passed = 0
            for check, description in checks:
                status = "✅ PASS" if check else "❌ FAIL"
                print(f"  {status}: {description}")
                if check:
                    passed += 1
            
            # Take screenshot
            screenshot_path = '/tmp/selenium_chinese_test.png'
            try:
                driver.save_screenshot(screenshot_path)
                print(f"\n📸 Screenshot saved to: {screenshot_path}")
            except Exception as e:
                print(f"\n⚠️  Screenshot failed: {e}")
            
            print(f"\n{'='*60}")
            print(f"Selenium Test: {passed}/{len(checks)} checks passed")
            print(f"{'='*60}")
            
            return passed == len(checks)
            
        finally:
            driver.quit()
            
    except ImportError as e:
        print(f"⚠️  Selenium not installed: {e}")
        print("Install with: pip install selenium")
        return None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_info():
    """Display system locale and encoding information"""
    print("=" * 60)
    print("System Locale & Encoding Information")
    print("=" * 60)
    
    import locale
    import os
    
    print(f"\nPython Version: {sys.version}")
    print(f"\nDefault Encoding: {sys.getdefaultencoding()}")
    print(f"File System Encoding: {sys.getfilesystemencoding()}")
    print(f"Preferred Encoding: {locale.getpreferredencoding()}")
    
    print("\nLocale Settings:")
    try:
        loc = locale.getlocale()
        print(f"  Current Locale: {loc}")
    except Exception as e:
        print(f"  Error getting locale: {e}")
    
    print("\nEnvironment Variables:")
    for var in ['LANG', 'LC_ALL', 'LC_CTYPE', 'LANGUAGE']:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")
    
    print("\nChinese Character Test:")
    test_text = "中文测试 - 你好世界 - Crawlab爬虫"
    print(f"  Original: {test_text}")
    print(f"  UTF-8 Encoded: {test_text.encode('utf-8')}")
    print(f"  Length: {len(test_text)} characters")

def main():
    parser = argparse.ArgumentParser(
        description="Browser Chinese locale test script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Playwright
  python browser_chinese_test.py --browser playwright
  
  # Test Selenium
  python browser_chinese_test.py --browser selenium
  
  # Test both
  python browser_chinese_test.py --browser both
  
  # Show system info only
  python browser_chinese_test.py --info
        """
    )
    
    parser.add_argument('--browser', 
                       choices=['playwright', 'selenium', 'both'],
                       default='both',
                       help='Browser automation tool to test')
    parser.add_argument('--info', action='store_true',
                       help='Display system locale information')
    
    args = parser.parse_args()
    
    # Always show system info first
    test_system_info()
    
    if args.info:
        return 0
    
    print("\n\n")
    
    # Run browser tests
    results = {}
    
    if args.browser in ['playwright', 'both']:
        result = test_playwright_chinese()
        if result is not None:
            results['playwright'] = result
    
    if args.browser in ['selenium', 'both']:
        print("\n\n")
        result = test_selenium_chinese()
        if result is not None:
            results['selenium'] = result
    
    # Summary
    if results:
        print("\n\n")
        print("=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        
        for tool, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{tool.capitalize()}: {status}")
        
        all_passed = all(results.values())
        print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️  Some tests failed"))
        
        return 0 if all_passed else 1
    else:
        print("\n⚠️  No browser tests were run (tools not installed)")
        return 0

if __name__ == '__main__':
    sys.exit(main())
