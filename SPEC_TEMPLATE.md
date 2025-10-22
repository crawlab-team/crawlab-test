# Test Specification Template

This template defines the unified format for writing test case specifications. Each test spec should be a self-contained document that includes everything needed to understand, execute, and validate the test.

## Spec Format

```markdown
# [Test ID] - [Test Title]

## Metadata
- **Category**: [api|cluster|database|dependencies|scheduler|system|ui]
- **Priority**: [critical|high|medium|low]
- **Complexity**: [simple|moderate|complex]
- **Duration**: [estimated time]
- **Environment**: [local|staging|production|any]
- **Dependencies**: [list of required components]

## Scenario
Brief description of what this test is validating and why it's important.

## Prerequisites
- List of conditions that must be met before running this test
- Required system state, data, or configuration
- Any setup steps needed

## Test Steps
Detailed steps to execute the test. Can include:
- Script executions
- AI-powered test execution
- Validation checkpoints

### Step 1: [Action Description]
**Method**: [script|copilot]
**Command**: `script-or-command-to-run`
**Expected**: What should happen
**Validation**: How to verify the step succeeded

### Step N: [Final Validation]
**Method**: [validation-approach]
**Criteria**: List of success criteria
**Failure Modes**: Known ways this could fail

## Success Criteria
Clear, measurable criteria that define test success:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion N

## Failure Scenarios
Expected failure modes and how to handle them:
- **Scenario**: Description
- **Symptoms**: How to recognize it
- **Action**: What to do

## Execution
### Automated
```bash
# Commands to run the test automatically
./helpers/category/script-name.py --spec node-disconnection
```

### Manual
Steps for manual execution when automation isn't suitable.

### Hybrid
Combination of automated and manual steps with clear handoff points.

## Cleanup
Steps to restore system state after test completion:
- Remove test data
- Reset configurations
- Stop test processes

## Notes
Additional information, known issues, or context that might be helpful.

## History
- **Created**: Date, Author
- **Modified**: Date, Author, Reason
- **Last Run**: Date, Result, Notes
```

## Field Descriptions

### Metadata
- **Category**: Groups related tests for organization
- **Priority**: Importance level for execution scheduling
- **Complexity**: Effort estimation for planning
- **Duration**: Expected time to complete
- **Environment**: Where this test can/should be run
- **Dependencies**: Other tests, components, or state required

### Scenario
A clear, concise explanation of:
- What behavior/functionality is being tested
- Why this test is important
- What could go wrong if this functionality fails

### Prerequisites
Everything that must be true before starting:
- System configuration
- Data state
- Running services
- Environment variables
- Permissions

### Test Steps
Detailed execution instructions with:
- **Method**: How this step is executed
  - `script`: Automated via helper script
  - `manual`: Human action required
  - `ai`: AI tool (MCP, Playwright, etc.)
  - `hybrid`: Combination of above
- **Command**: Exact command or instruction
- **Expected**: What should happen
- **Validation**: How to verify success

### Success Criteria
Objective, measurable outcomes that define success. Should be:
- Specific and unambiguous
- Verifiable (manually or automatically)
- Complete (covers all aspects being tested)

### Execution Methods
- **Automated**: Fully scripted execution
- **Manual**: Human-guided testing
- **Hybrid**: Mixed approach with clear handoffs

## Example Usage

See the example test specifications in the `specs/` directory for practical applications of this template.