Run pre-commit checks to validate the codebase before committing.

Execute these checks in order, stopping on first failure:

## 1. Tests

Run `pytest` to execute all tests.

## Output

Report:

- Tests: total / passed / failed
- Failure details with file:line and assertion message

## On Failure

If any check fails:

1. List all issues found, numbered (e.g., "1. FAILED face_detector/haar_test.py:42 — assert result == (10, 20, 50, 50)")
2. Ask the user which issues they'd like to fix, with these options:
   - **Fix all** — resolve every issue automatically
   - **Select specific issues** — let the user pick by number
   - **Skip** — proceed without fixing
3. Fix the selected issues, then re-run `pytest` to confirm resolution
4. If new issues appear after fixing, repeat the process
