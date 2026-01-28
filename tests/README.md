# Test Documentation

This directory contains test-related documentation and summaries.

## Purpose

Document test infrastructure, status, coverage, and improvement efforts for the project.

## Types of Documentation

### Test Status
- Format: `TEST-STATUS.md`
- Content: Current test coverage, passing/failing tests, coverage percentages

### Test Summaries
- Format: `TEST-SUMMARY.txt`, `TEST-SUMMARY.md`
- Content: Test run results, detailed output from test executions

### Test Enhancements
- Format: `TEST-ENHANCEMENT-SUMMARY.md`
- Content: Documentation of test infrastructure improvements, new test additions

## Guidelines

- **When to use**: When documenting testing strategy, results, or improvements
- **Scope**: Unit tests, integration tests, test coverage analysis
- **Updates**: Keep TEST-STATUS.md current with each test suite update
- **Format**: Clear metrics, percentages, and actionable information

## Relation to Code Tests

This directory contains **documentation** about tests. The actual test code is located in:
- `src/tests/` - Unit tests and test infrastructure
- `pytest.ini` - Test configuration
- `run-tests.sh` - Test runner script

## Best Practices

1. Update TEST-STATUS.md after significant test changes
2. Include coverage percentages and trends
3. Document any test failures and resolutions
4. Link to relevant issue documentation when applicable
