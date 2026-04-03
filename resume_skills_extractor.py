'''
Author: Devin 
Extracts the skills from the resume that the user upload
'''

import os
import json
import re
from pdfminer.high_level import extract_text

# Define the list of industry JSON files
industry_files = [
    "Skills/engineering_skills.json",
    "Skills/healthcare_skills.json",
    "Skills/legal_service_skills.json",
    "Skills/finance_skills.json",
    "Skills/tech_skills.json"
]

# Define the general skills JSON file
general_skills_file = "Skills/general_skills.json"
file_path = os.path.join('uploads', 'results.txt')


def _normalize_text(text):
    # Keep symbols often used in skill names (e.g., c++, c#), normalize other separators.
    text = text.lower()
    text = re.sub(r"[./_-]", " ", text)
    text = re.sub(r"[^\w\s+#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _load_skills(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data if isinstance(data, dict) else {}


def _alias_list(aliases):
    if isinstance(aliases, list):
        return aliases
    if isinstance(aliases, str):
        return [aliases]
    return []


def _contains_skill(text, term):
    if not term:
        return False
    escaped = re.escape(term).replace(r"\ ", r"\s+")
    pattern = rf"(?<!\w){escaped}(?!\w)"
    return re.search(pattern, text) is not None

# Extract text from PDF and output as TXT file
def extract_text_from_pdf(pdf_file, output_file=file_path):
    try:
        # Open the PDF file in read-binary mode
        with open(pdf_file, 'rb') as f:
            # Extract text from the PDF using a library function
            text = extract_text(f)
            
            # Normalize extracted text for skill matching
            text = _normalize_text(text)
            
            # Open the output TXT file in write mode with UTF-8 encoding
            with open(output_file, 'w', encoding='utf-8') as output:
                # Write the cleaned text to the output file
                output.write(text)
    except Exception as e:
        # Print an error message if an exception occurs during the extraction process
        print(f"Error extracting text: {e}")

# Define the function to extract skills from a text file
def extract_skills_from_text(text, industry_file, general_skills_file):
    industry_skills = _load_skills(industry_file)
    general_skills = _load_skills(general_skills_file)

    # Combine industry-specific and general skills into a single dictionary
    combined_skills = {**industry_skills, **general_skills}
    normalized_text = _normalize_text(text)
    
    # Create a set to store unique extracted skills
    extracted_skills = set()

    # Check each skill and aliases against the full resume text to support multi-word matching.
    for skill, aliases in combined_skills.items():
        variants = [skill] + _alias_list(aliases)
        normalized_variants = {_normalize_text(str(variant)) for variant in variants}

        if any(_contains_skill(normalized_text, variant) for variant in normalized_variants):
            extracted_skills.add(skill.lower().strip())

    # Return a stable, de-duplicated list
    return sorted(extracted_skills)

def outputSkillsExtracted(industry_choice):
    text_file = file_path

    if not os.path.exists(text_file):
        print("Text file not found. Please check the file path and try again.")
        return []
    else:
        with open(text_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Extract skills from the text using the selected industry and general skills files
        industry_index = max(0, min(industry_choice - 1, len(industry_files) - 1))
        industry_file = industry_files[industry_index]
        extracted_skills = extract_skills_from_text(text, industry_file, general_skills_file)

        industry_data = _load_skills(industry_file)
        industry_skills = []
        general_skills = []

        # Append skills into different list
        for skill in extracted_skills:
            if skill in {item.lower() for item in industry_data.keys()}:
                industry_skills.append(skill)
            else:
                general_skills.append(skill)

    # Combine industry and general skills, preserving order and uniqueness
    final_skills = list(dict.fromkeys(industry_skills + general_skills))
    return final_skills
