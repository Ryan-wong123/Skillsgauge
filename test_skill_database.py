"""Tests for the skill database feature."""

import app as skillsgauge_app
import resume_skills_extractor


def test_load_skill_database_groups_existing_skill_files():
    catalog = resume_skills_extractor.load_skill_database()

    assert catalog["total_skills"] > 0
    assert "Technology" in catalog["categories"]
    assert any(group["category"] == "Technology" for group in catalog["groups"])


def test_load_skill_database_filters_by_query_and_category():
    catalog = resume_skills_extractor.load_skill_database(
        search_query="python",
        selected_category="Technology",
    )

    assert catalog["selected_category"] == "Technology"
    assert catalog["total_skills"] >= 1
    assert len(catalog["groups"]) == 1
    assert catalog["groups"][0]["category"] == "Technology"
    assert any(skill["name"] == "python" for skill in catalog["groups"][0]["skills"])


def test_skill_database_route_renders_filtered_results():
    client = skillsgauge_app.app.test_client()

    response = client.get("/skills?q=python&category=Technology")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Skill Database" in page
    assert "Technology" in page
    assert "python" in page
