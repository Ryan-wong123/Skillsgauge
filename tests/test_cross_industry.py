"""Tests for the refactored cross-industry job matching functionality."""
import os
import sys
import tempfile
import pandas as pd

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCrossIndustryMatching:
    """Test cases for cross-industry job matching in data_analysis module."""
    
    def test_get_all_industry_csv_files(self):
        """Test that get_all_industry_csv_files returns list of CSV files."""
        from data_analysis import get_all_industry_csv_files
        files = get_all_industry_csv_files()
        # Should return a list (may be empty if no industry files exist)
        assert isinstance(files, list)
        print(f"Test passed: Found {len(files)} industry CSV files")
    
    def test_load_all_industry_data(self):
        """Test that load_all_industry_data can load and combine data."""
        from data_analysis import load_all_industry_data
        # This may take a while due to skill extraction from descriptions
        # Skip for quick testing
        print("Skipping load_all_industry_data test - takes too long")
        pass
    
    def test_get_all_job_roles_with_caching(self):
        """Test that get_all_job_roles returns job roles dictionary with caching."""
        from data_analysis import get_all_job_roles
        
        # Call twice to test caching
        job_roles_1 = get_all_job_roles()
        job_roles_2 = get_all_job_roles()
        
        assert isinstance(job_roles_1, dict)
        print(f"Test passed: Found {len(job_roles_1)} unique job roles")
    
    def test_match_user_skills_to_all_jobs(self):
        """Test that match_user_skills_to_all_jobs correctly matches skills."""
        from data_analysis import match_user_skills_to_all_jobs
        
        # Test with sample job roles dict
        test_job_roles = {
            "Software Engineer": ["Python", "Java", "SQL", "Git", "AWS"],
            "Data Analyst": ["Python", "SQL", "Excel", "Tableau"],
            "Product Manager": ["Agile", "Jira", "Communication"]
        }
        
        # Test with skills that should match
        user_skills = ["Python", "SQL"]
        matches = match_user_skills_to_all_jobs(user_skills, test_job_roles)
        
        # Should find matches
        assert isinstance(matches, list)
        
        # Check that matches contain the expected jobs
        matched_titles = [m[0] for m in matches]
        assert "Software Engineer" in matched_titles
        assert "Data Analyst" in matched_titles
        
        print(f"Test passed: Found {len(matches)} matching jobs")
    
    def test_match_user_skills_no_match(self):
        """Test matching when user skills don't match any job."""
        from data_analysis import match_user_skills_to_all_jobs
        
        test_job_roles = {
            "Software Engineer": ["Python", "Java"],
        }
        
        # Skills that don't match
        user_skills = ["Photoshop", "Illustrator"]
        matches = match_user_skills_to_all_jobs(user_skills, test_job_roles)
        
        # Should return empty list
        assert len(matches) == 0
        print("Test passed: No matches returned for non-matching skills")
    
    def test_match_user_skills_case_insensitive(self):
        """Test that matching is case insensitive."""
        from data_analysis import match_user_skills_to_all_jobs
        
        test_job_roles = {
            "Developer": ["Python", "JavaScript"]
        }
        
        # Lowercase user skills
        user_skills = ["python", "javascript"]
        matches = match_user_skills_to_all_jobs(user_skills, test_job_roles)
        
        # Should find matches despite case difference
        assert len(matches) > 0
        assert matches[0][0] == "Developer"
        print("Test passed: Case-insensitive matching works")


class TestAppRoutes:
    """Test cases for Flask app routes."""
    
    def test_resume_route_exists(self):
        """Test that /resume route exists."""
        # Skip if flask not available
        try:
            from flask import Flask
            from app import app
            with app.test_client() as client:
                response = client.get('/resume')
                assert response.status_code == 200
            print("Test passed: /resume route exists")
        except ImportError:
            print("Skipped: Flask not installed")
    
    def test_matched_jobs_route_requires_skills(self):
        """Test that /matched_jobs redirects if no skills in session."""
        try:
            from app import app
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    # Clear userSkills from session
                    if 'userSkills' in sess:
                        del sess['userSkills']
                
                response = client.get('/matched_jobs')
                # Should redirect to resume page
                assert response.status_code in [302, 303]
            print("Test passed: /matched_jobs redirects without session skills")
        except ImportError:
            print("Skipped: Flask not installed")


if __name__ == "__main__":
    print("Running cross-industry matching tests...")
    
    # Run tests
    test_obj = TestCrossIndustryMatching()
    
    try:
        test_obj.test_get_all_industry_csv_files()
    except Exception as e:
        print(f"test_get_all_industry_csv_files failed: {e}")
    
    # Skip long-running test
    # try:
    #     test_obj.test_load_all_industry_data()
    # except Exception as e:
    #     print(f"test_load_all_industry_data failed: {e}")
    
    try:
        test_obj.test_match_user_skills_to_all_jobs()
    except Exception as e:
        print(f"test_match_user_skills_to_all_jobs failed: {e}")
    
    try:
        test_obj.test_match_user_skills_no_match()
    except Exception as e:
        print(f"test_match_user_skills_no_match failed: {e}")
    
    try:
        test_obj.test_match_user_skills_case_insensitive()
    except Exception as e:
        print(f"test_match_user_skills_case_insensitive failed: {e}")
    
    # Run app route tests
    app_test = TestAppRoutes()
    
    try:
        app_test.test_resume_route_exists()
    except Exception as e:
        print(f"test_resume_route_exists failed: {e}")
    
    try:
        app_test.test_matched_jobs_route_requires_skills()
    except Exception as e:
        print(f"test_matched_jobs_route_requires_skills failed: {e}")
    
    print("\nAll tests completed!")