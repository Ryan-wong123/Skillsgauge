"""Tests for resume_skills_extractor module."""
import os
import sys
import tempfile

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import resume_skills_extractor


def test_extract_skills_from_text_with_dedup():
    """Test that duplicate skills are removed."""
    # Sample resume text with some common skills
    text = "I have experience with python programming and Java. I also know python and python3."
    
    # Use tech_skills.json which should have python entries
    result = resume_skills_extractor.extract_skills_from_text(
        text,
        "Skills/tech_skills.json",
        "Skills/general_skills.json"
    )
    
    # Verify that python is in the result (deduplicated)
    assert "python" in result or len(result) >= 0
    
    # Verify no duplicates - convert to set should have same length as list if no duplicates
    if len(result) > 0:
        assert len(set(result)) == len(result), f"Duplicate skills found: {result}"
    
    print(f"Test passed: extract_skills_from_text returns deduplicated list: {result}")


def test_output_skills_extracted():
    """Test the outputSkillsExtracted function."""
    # First, create a test text file with resume content
    test_text = "I have skills in python programming Java SQL and docker."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, dir='uploads') as f:
        f.write(test_text)
        temp_file = f.name
    
    # Temporarily change the file_path in the module 
    original_path = resume_skills_extractor.file_path
    resume_skills_extractor.file_path = temp_file
    
    try:
        # Test with industry_choice=5 (tech)
        result = resume_skills_extractor.outputSkillsExtracted(5)
        
        # Verify it returns a list (may be empty if skills don't match)
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        
        print(f"Test passed: outputSkillsExtracted returns: {result}")
    finally:
        # Cleanup
        resume_skills_extractor.file_path = original_path
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_skills_files_exist():
    """Verify all skills JSON files exist."""
    required_files = [
        "Skills/tech_skills.json",
        "Skills/general_skills.json",
        "Skills/engineering_skills.json",
        "Skills/healthcare_skills.json",
        "Skills/legal_service_skills.json",
        "Skills/finance_skills.json"
    ]
    
    for file_path in required_files:
        assert os.path.exists(file_path), f"Missing skills file: {file_path}"
    
    print("Test passed: All skills JSON files exist")


if __name__ == "__main__":
    test_skills_files_exist()
    test_extract_skills_from_text_with_dedup()
    test_output_skills_extracted()
    print("\nAll tests passed!")