Updated the automation prompt template so issue metadata is passed as environment variables instead of unresolved `{{...}}` tokens.

- What changed: replaced placeholder tokens in the Codex issue prompt with `${...}` syntax for `REPO_NAME`, `ISSUE_NUMBER`, `ISSUE_URL`, `ISSUE_TITLE`, and `ISSUE_BODY`.
- Files changed: [.github/codex/prompts/issue-fix.md](/home/runner/work/Skillsgauge/Skillsgauge/.github/codex/prompts/issue-fix.md)
- Assumptions made: `openai/codex-action@v1` supports environment-variable interpolation in prompt files using `${VAR}` syntax, while `{{VAR}}` is not interpolated.
- Follow-up work still needed: run one labeled issue (`codex-run`) to confirm the prompt now contains real issue values in the Codex run context.