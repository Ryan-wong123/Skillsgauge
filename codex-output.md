Implemented a scoped fix for issue #16 by improving PDF resume skill extraction quality and deduping in the extractor, while keeping the existing Flask upload flow unchanged.

**What changed**
- Updated skill extraction to match against normalized full resume text instead of only single-token matches.
- Added normalization that better handles separators/symbols used in skill names (e.g., multi-word skills, `c++`, `c#`, `node.js` style text).
- Kept alias support, including defensive handling when aliases are not always a list.
- Ensured extracted skills are de-duplicated and returned as a clean, stable list.
- Added safer handling for missing skill JSON files and missing extracted text file (`[]` returned instead of failing).
- Kept the same public functions used by Flask:
  - `extract_text_from_pdf(...)`
  - `outputSkillsExtracted(...)`

**Files changed**
- [resume_skills_extractor.py](/home/runner/work/Skillsgauge/Skillsgauge/resume_skills_extractor.py)

**Validation steps**
- Ran syntax validation successfully:
  - `python -m py_compile app.py resume_skills_extractor.py`
- Could not run end-to-end extraction in this environment because `pdfminer` is not installed (`ModuleNotFoundError`), so runtime PDF parsing could not be executed here.

**Assumptions made**
- Skill JSON files are expected to be dictionaries of `skill -> aliases`.
- Returning lowercased, unique skills is acceptable for the current `edit_resume.html` flow.
- Keeping `outputSkillsExtracted(5)` behavior (tech/default path from app) is intentional and unchanged in Flask routing.

**Follow-up work still needed**
1. Install project dependencies (including `pdfminer.six`) and run a real upload test through `/resume` -> `/upload`.
2. Verify extraction quality against representative PDF resumes and tune skill dictionaries if needed.