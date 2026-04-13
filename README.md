# SkillGauge: A Python-Based Web App for Fresh Grads
A Python-based web application that analyzes user skills and resumes to assess industry fit and current job trends using web scraping and natural language processing.<br/>

## Project objectives
The skill database gives users a single place to inspect the skills SkillGauge already understands during resume parsing, industry analysis, and job-role exploration. It helps users verify which skills exist in the system before uploading a resume or reviewing career recommendations.

## Main Functions:<br/>

Resume Keyword Extractor<br/>
Web Crawler and Scraper<br/> 
Frequency Analysis<br/>
Trend Analysis<br/>
Skill Gap Identifier<br/>
Web-Based User Interface<br/>
Skill Database<br/>

## Features
Users can open the Skill Database from the main navigation and browse skills grouped into General, Engineering, Healthcare, Legal Services, Finance, and Technology categories. The page supports keyword search and category filtering so users can quickly look up a skill and review related aliases or matching terms stored in the app.

## Technology Stack:
*Frontend*: HTML, CSS, Bootstrap, Jinja, JavaScript<br/>
*Backend*: Flask<br/>
*Web scraper*: Selenium, ThreadPoolExecutor<br/>
*Data processing/analysis*: Pandas, scikit learn, NumPy<br/> 
*Data Visualization*: Plotly<br/> 
*Dataset/ Database*: CSV files, Json files<br/> 
*Resume extraction*: PDFMiner<br/> 
*GitHub Actions*: YAML<br/>

## Implementation guide
The feature is exposed through the `/skills` Flask route in `app.py` and rendered with `templates/skill_database.html`. Skill data is loaded from the existing JSON files in `Skills/` through helper logic in `resume_skills_extractor.py`, which now centralizes the category-to-file mapping for both resume extraction and the skill database. The loader builds grouped catalog data, supports optional search and category filters, removes duplicate self-aliases for cleaner display, and passes the structured result into the Jinja template for rendering.

## How to run:
pip install -r requirements.txt<br/>
python app.py

## Conclusion
The skill database improves transparency in SkillGauge by showing users the structured skill library behind the app’s recommendations and resume matching. It is useful as a lightweight reference page and does so without changing the existing CSV-based analysis flows.
