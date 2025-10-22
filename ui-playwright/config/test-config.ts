/**
 * Test Configuration and Data
 * 
 * Centralized configuration for all UI tests.
 * Environment variables override these defaults.
 */

export const config = {
  // Base URL for Crawlab application
  baseUrl: process.env.CRAWLAB_BASE_URL || 'http://localhost:8080',
  
  // Default credentials
  credentials: {
    admin: {
      username: process.env.CRAWLAB_ADMIN_USERNAME || 'admin',
      password: process.env.CRAWLAB_ADMIN_PASSWORD || 'admin',
    },
  },
  
  // Timeouts
  timeouts: {
    short: 5_000,      // 5 seconds
    medium: 15_000,    // 15 seconds
    long: 30_000,      // 30 seconds
    extraLong: 60_000, // 60 seconds
  },
  
  // API endpoints
  api: {
    login: '/api/login',
    logout: '/api/logout',
    spiders: '/api/spiders',
    tasks: '/api/tasks',
    nodes: '/api/nodes',
  },
};

/**
 * Test data generators
 */
export const testData = {
  spider: {
    name: (prefix = 'test-spider') => `${prefix}-${Date.now()}`,
    description: 'Test spider created by automated tests',
  },
  
  task: {
    name: (prefix = 'test-task') => `${prefix}-${Date.now()}`,
  },
  
  schedule: {
    name: (prefix = 'test-schedule') => `${prefix}-${Date.now()}`,
    cron: '0 9 * * *', // Daily at 9 AM
  },
};

/**
 * Common selectors
 */
export const selectors = {
  // Common UI elements
  dialog: '.el-dialog, [role="dialog"]',
  dialogTitle: '.el-dialog__title',
  dialogFooter: '.el-dialog__footer',
  confirmButton: 'button:has-text("Confirm"), button:has-text("确定"), button:has-text("OK")',
  cancelButton: 'button:has-text("Cancel"), button:has-text("取消")',
  saveButton: 'button:has-text("Save"), button:has-text("保存")',
  deleteButton: 'button:has-text("Delete"), button:has-text("删除")',
  createButton: 'button:has-text("Create"), button:has-text("新建"), button:has-text("创建")',
  
  // Forms
  input: (name: string) => `input[name="${name}"], input[placeholder*="${name}" i]`,
  select: (name: string) => `select[name="${name}"], .el-select:has-text("${name}")`,
  
  // Tables
  table: '.el-table',
  tableRow: '.el-table__row',
  tableCell: '.el-table__cell',
  
  // Messages
  successMessage: '.el-message--success',
  errorMessage: '.el-message--error',
  warningMessage: '.el-message--warning',
  infoMessage: '.el-message--info',
};
