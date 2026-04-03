# AGENTS.md

## Project overview
SkillGauge is a Flask-based web app for resume skill extraction, industry/job analysis, and course recommendations.

## Working rules
- Keep changes scoped to the issue.
- Do not refactor unrelated modules.
- Preserve Flask route names unless the issue explicitly requires changes.
- Preserve CSV-based local data loading.
- Be careful with file paths and the uploads flow.

## Validation
- App should still start successfully.
- Changed route/page should render without obvious template errors.
- Avoid unrelated cleanup.

## Pull request expectations
- Summarize what changed
- State assumptions
- Mention validation steps