---
description: Run pytest tests for the project
---

## Usage

- `/test` — run all tests
- `/test <file_or_dir>` — run tests in a specific file or directory
- `/test -v` — run all tests with verbose output

## Commands

```bash
# All tests
pytest

# Specific file or directory
pytest <file_or_dir>

# Verbose output
pytest -v
```

## Output

Report:

- Total tests / Passed / Failed
- Failure details with file:line and assertion message
- Suggestions for fixing failures

## On Failure

If any tests fail, ask the user if they'd like you to fix the failing tests before proceeding.
