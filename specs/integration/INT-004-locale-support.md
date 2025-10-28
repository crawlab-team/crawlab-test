# INT-004 - Chinese Locale Support Validation

## Metadata
- **Category**: integration
- **Priority**: high
- **Complexity**: simple
- **Duration**: 5-10 minutes
- **Environment**: docker
- **Dependencies**: Docker container with base image, Chinese fonts

## Scenario
Validates that Docker containers properly support Chinese locale (zh_CN.UTF-8) for applications that need to display Chinese characters in screenshots, logs, or UI elements. This addresses user complaints about Chinese characters not displaying correctly in generated screenshots and reports.

## Prerequisites
- Docker environment running
- Crawlab containers built with updated base image
- Access to container shell for testing
- Chinese test text samples available

## Test Steps

### Step 1: Verify Chinese Locale Installation
**Method**: script
**Command**: Check if Chinese locale (zh_CN.UTF-8) is installed and available in target container
**Expected**: zh_CN.UTF-8 locale is installed and available
**Validation**: `locale -a` shows zh_CN.utf8 in output

### Step 2: Test Chinese Character Display
**Method**: script  
**Command**: Test Chinese character display functionality in target container
**Expected**: Chinese characters render without question marks or boxes
**Validation**: Python Unicode test prints Chinese characters correctly

### Step 3: Validate Font Support
**Method**: script
**Command**: Check if Chinese fonts are installed and accessible in target container
**Expected**: Chinese fonts (WenQuanYi, Noto CJK) are installed and accessible
**Validation**: fc-list shows Chinese font families available

### Step 4: Test Application Screenshot Scenario
**Method**: hybrid
**Command**: Test screenshot functionality with Chinese text in target container
**Expected**: Screenshots containing Chinese text render properly
**Validation**: Generated screenshot file contains readable Chinese characters

### Step 5: Verify Environment Variables
**Method**: script
**Command**: Verify locale environment variables support Chinese display
**Expected**: Locale environment variables support Chinese display
**Validation**: LC_CTYPE=zh_CN.UTF-8 is set and functional

## Success Criteria
- [ ] zh_CN.UTF-8 locale is properly installed and listed in `locale -a`
- [ ] Chinese characters display correctly in terminal output
- [ ] Chinese fonts are available via fontconfig
- [ ] Python can encode/decode Chinese text without errors
- [ ] Screenshots with Chinese text render readably
- [ ] Environment variables support Chinese locale

## Failure Scenarios
- **Missing Locale**: zh_CN.UTF-8 not in locale list
  - **Symptoms**: `locale -a` doesn't show Chinese locale
  - **Action**: Check base image locale generation in deps.sh
- **Font Issues**: Chinese characters show as boxes/question marks
  - **Symptoms**: Text displays but unreadable
  - **Action**: Verify fonts-wqy-zenhei and fonts-noto-cjk installation
- **Environment Problems**: Locale set but not functional
  - **Symptoms**: Commands fail with encoding errors
  - **Action**: Check LC_CTYPE and LANG environment variables

## Execution

### Automated
```bash
# Execute via test-runner (auto-discovers runner script)
./test-runner.py --spec specs/infrastructure/INF-004-chinese-locale-support-validation.md

# Or specify script method explicitly
./test-runner.py --spec specs/infrastructure/INF-004-chinese-locale-support-validation.md --method script
```

### Manual
1. Access container shell: `docker exec -it crawlab-master bash`
2. Check available locales: `locale -a | grep zh`
3. Test character display: `echo "测试中文字符: 你好世界"`
4. Verify fonts: `fc-list | grep -i chinese`
5. Test Python Unicode: `python3 -c "print('中文测试: 您好')"`

### Hybrid
1. Use script to setup test environment
2. Manual verification of visual character rendering
3. Script validation of technical locale configuration

## Cleanup
- Remove any temporary test files created during screenshot testing
- No persistent state changes - containers remain in original state

## Notes
- This test validates the fix for user-reported Chinese character display issues
- Chinese locale support is essential for international users
- Test covers both simplified (zh_CN) and traditional Chinese character support
- Screenshot functionality is critical for spider monitoring and debugging

## History
- **Created**: 2025-09-17, GitHub Copilot
- **Modified**: N/A
- **Last Run**: N/A