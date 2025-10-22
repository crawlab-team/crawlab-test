import { defineConfig, devices } from '@playwright/test';

/**
 * Crawlab UI Test Configuration
 * 
 * This configuration provides:
 * - Headless CI-friendly defaults
 * - Screenshot/video on failure
 * - JSON reporter for Python integration
 * - Retry logic for flaky tests
 * - Multiple browser support
 */

// Read from environment or use defaults
const BASE_URL = process.env.CRAWLAB_BASE_URL || 'http://localhost:8080';
const HEADLESS = process.env.CI === 'true' || process.env.HEADLESS !== 'false';
const WORKERS = process.env.CI === 'true' ? 1 : undefined; // Serial in CI, parallel locally

export default defineConfig({
  // Test directory
  testDir: './tests',
  
  // Test file patterns
  testMatch: '**/*.spec.ts',
  
  // Timeout for each test
  timeout: 60 * 1000, // 60 seconds
  
  // Expect timeout for assertions
  expect: {
    timeout: 10 * 1000, // 10 seconds
  },
  
  // Run tests in files in parallel
  fullyParallel: !process.env.CI,
  
  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Workers
  workers: WORKERS,
  
  // Reporter configuration
  reporter: [
    // List reporter for console output
    ['list'],
    // JSON reporter for Python integration
    ['json', { outputFile: '../results/playwright-results.json' }],
    // HTML reporter for detailed reports
    ['html', { outputFolder: '../results/playwright-report', open: 'never' }],
  ],
  
  // Shared settings for all the projects below
  use: {
    // Base URL
    baseURL: BASE_URL,
    
    // Browser context options
    viewport: { width: 1920, height: 1080 },
    
    // Collect trace on first retry
    trace: process.env.CI ? 'on-first-retry' : 'retain-on-failure',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
    
    // Timeout for actions
    actionTimeout: 15 * 1000, // 15 seconds
    
    // Navigation timeout
    navigationTimeout: 30 * 1000, // 30 seconds
    
    // Locale
    locale: 'en-US',
    
    // Timezone
    timezoneId: 'UTC',
  },
  
  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        headless: HEADLESS,
      },
    },
    
    // Uncomment to test in Firefox and WebKit
    // {
    //   name: 'firefox',
    //   use: { 
    //     ...devices['Desktop Firefox'],
    //     headless: HEADLESS,
    //   },
    // },
    
    // {
    //   name: 'webkit',
    //   use: { 
    //     ...devices['Desktop Safari'],
    //     headless: HEADLESS,
    //   },
    // },
    
    // Mobile viewports
    // {
    //   name: 'Mobile Chrome',
    //   use: { 
    //     ...devices['Pixel 5'],
    //     headless: HEADLESS,
    //   },
    // },
  ],
  
  // Webserver configuration - start Crawlab if not running
  // webServer: {
  //   command: 'cd ../.. && docker-compose up',
  //   url: BASE_URL,
  //   reuseExistingServer: true,
  //   timeout: 120 * 1000,
  // },
  
  // Output folder for test artifacts
  outputDir: '../results/playwright-artifacts',
});
