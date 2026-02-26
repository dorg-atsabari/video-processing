Analyze all changes in the working tree and create a well-structured commit.

Follow these steps:

1. Run `git status` to see all untracked and modified files. Never use the `-uall` flag.
2. Run `git diff` to see unstaged changes and `git diff --cached` to see staged changes.
3. Run `git diff origin/main...HEAD` and `git log origin/main..HEAD --oneline` to understand all changes since diverging from main.
4. Run `git log --oneline -5` to see recent commit message style.

5. Analyze ALL changes (staged, unstaged, and untracked) and determine:
   - The type of change using Conventional Commits: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`, `ci`, `build`
   - An optional scope in parentheses if the change is localized (e.g., `feat(auth)`, `fix(api)`)
   - A concise description (imperative mood, lowercase, no period)
   - If the change spans multiple types, use the most significant one

6. Stage all relevant files by name. Do NOT use `git add -A` or `git add .`. Do not stage files that contain secrets (.env, credentials, API keys).

7. Create the commit using this format:
   ```
   <type>[optional scope]: <description>

   [optional body explaining WHY, not WHAT]

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   ```

   Pass the message via HEREDOC:
   ```bash
   git commit -m "$(cat <<'EOF'
   <type>[optional scope]: <description>

   <optional body>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```

8. Run `git status` after the commit to verify success.

Rules:
- Do NOT push to remote unless explicitly asked.
- Do NOT amend previous commits.
- If a pre-commit hook fails, fix the issue and create a NEW commit.
- If there are no changes to commit, say so and stop.