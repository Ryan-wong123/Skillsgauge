You are Codex working on the repository: {{REPO_NAME}}

A GitHub issue has been labeled for automation.

Issue number: {{ISSUE_NUMBER}}
Issue URL: {{ISSUE_URL}}

Issue title:
{{ISSUE_TITLE}}

Issue body:
{{ISSUE_BODY}}

Repository instructions:
- Read and follow AGENTS.md if present
- Keep changes scoped to this issue
- Avoid unrelated refactors
- Prefer minimal, reviewable changes
- Preserve existing route names and current user flow unless the issue explicitly requires otherwise
- Preserve existing CSV/data path expectations unless the issue explicitly requires changes

Project-specific expectations for SkillGauge:
- Main Flask app entry point is app.py
- templates/ contains Flask HTML templates
- static/ contains frontend assets
- data_analysis.py contains analysis and matching logic
- Analysis_Visualisation.py contains charts and visualizations
- resume_skills_extractor.py handles resume extraction
- uploads/ is used for temporary uploaded files

Your task:
1. Read the issue carefully
2. Inspect the repository and identify the smallest correct change
3. Implement the fix or feature
4. Do not refactor unrelated code
5. If the issue is ambiguous, make the safest minimal assumption
6. Stop after making the code changes needed for a PR

When done, summarize:
- what changed
- which files changed
- any assumptions made
- any follow-up work still needed