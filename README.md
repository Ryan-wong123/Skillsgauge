# SkillGauge: A Python-Based Web App for Fresh Grads
A Python-based web application that analyzes user skills and resumes to assess industry fit and current job trends using web scraping and natural language processing.<br/>

## Main Functions:<br/>

Resume Keyword Extractor<br/>
Web Crawler and Scraper<br/> 
Frequency Analysis<br/>
Trend Analysis<br/>
Skill Gap Identifier<br/>
Web-Based User Interface<br/>

## Technology Stack:
*Frontend*: HTML, CSS, Bootstrap, Jinja, JavaScript<br/>
*Backend*: Flask<br/>
*Web scraper*: Selenium, ThreadPoolExecutor<br/>
*Data processing/analysis*: Pandas, scikit learn, NumPy<br/> 
*Data Visualization*: Plotly<br/> 
*Dataset/ Database*: CSV files, Json files<br/> 
*Resume extraction*: PDFMiner<br/> 
*GitHub Actions*: YAML<br/>

## How to run:
pip install -r requirements.txt<br/>
python app.py

## Project Objectives
The skill database gives users a central place to review the skills already recognized by SkillGauge. It helps users understand which skills the app can match during resume extraction and which capabilities are grouped under each industry-focused area.

## Features
Users can open the Skill Database page from the main navigation or home page and browse skills by category. The page supports keyword search and category filtering, so users can quickly look up a skill such as `python`, review related aliases, and explore grouped skills across General, Engineering, Healthcare, Legal Services, Finance, and Technology.

## Implementation Guide
The feature is served by the `/skills` Flask route in `app.py`, which reads the current search query and selected category before rendering `templates/skill_database.html`. Skills are stored in the existing JSON files under `Skills/` and loaded through `resume_skills_extractor.py`, where `SKILL_SOURCE_DEFINITIONS` maps each file to a display category and `load_skill_database()` builds the structured catalog used by the template. The page displays grouped skills, category summaries, and alias terms without duplicating the existing resume skill source files.

## Conclusion
The skill database makes SkillGauge easier to understand and use because users can inspect the app's skill library directly instead of relying on hidden matching logic. That improves transparency for resume analysis, supports skill discovery, and keeps the implementation maintainable by reusing the same JSON-backed sources already used for skill extraction.
