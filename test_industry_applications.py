"""Tests for industry application shortlist helpers."""

import builtins
from io import StringIO

import pandas as pd

import app as skillsgauge_app
from data_analysis import (
    build_application_shortlist,
    create_application_shortlist_csv,
    process_bulk_applications,
)


def test_build_application_shortlist_sorts_and_deduplicates():
    df = pd.DataFrame(
        [
            {
                "Job Title": "Data Analyst",
                "Company": "Alpha",
                "Location": "Singapore",
                "Job Posting Date": "2026-04-01",
                "Job URL": "https://example.com/alpha-1",
            },
            {
                "Job Title": "Data Analyst",
                "Company": "Alpha",
                "Location": "Singapore",
                "Job Posting Date": "2026-03-20",
                "Job URL": "https://example.com/alpha-1",
            },
            {
                "Job Title": "BI Analyst",
                "Company": "Beta",
                "Location": "Remote",
                "Job Posting Date": "2026-04-05",
                "Job URL": "https://example.com/beta-1",
            },
        ]
    )

    shortlist = build_application_shortlist(df)

    assert len(shortlist) == 2
    assert shortlist[0]["job_title"] == "BI Analyst"
    assert shortlist[0]["company"] == "Beta"
    assert shortlist[0]["status"] == "To Apply"


def test_create_application_shortlist_csv_contains_header_and_rows():
    shortlist = [
        {
            "job_title": "Data Analyst",
            "company": "Alpha",
            "location": "Singapore",
            "posted_date": "2026-04-01",
            "job_url": "https://example.com/alpha-1",
            "status": "To Apply",
            "notes": "",
        }
    ]

    csv_content = create_application_shortlist_csv(shortlist)

    assert "job_title,company,location,posted_date,job_url,status,notes" in csv_content
    assert "Data Analyst,Alpha,Singapore,2026-04-01,https://example.com/alpha-1,To Apply," in csv_content


def test_process_bulk_applications_reports_partial_failures():
    shortlist = [
        {
            "job_title": "Data Analyst",
            "company": "Alpha",
            "location": "Singapore",
            "posted_date": "2026-04-01",
            "job_url": "https://example.com/alpha-1",
            "status": "To Apply",
            "notes": "",
        },
        {
            "job_title": "BI Analyst",
            "company": "Beta",
            "location": "Remote",
            "posted_date": "2026-04-02",
            "job_url": "",
            "status": "To Apply",
            "notes": "",
        },
    ]

    result = process_bulk_applications(
        shortlist,
        selected_indexes=["0", "1"],
        user_profile={"industry": "Technology", "skills": ["SQL", "Python"]},
    )

    assert result["success_count"] == 1
    assert result["failure_count"] == 1
    assert result["results"][0]["application_status"] == "Submitted"
    assert result["results"][1]["application_status"] == "Failed"


def test_bulk_industry_applications_route_shows_submission_results(monkeypatch):
    csv_df = pd.DataFrame(
        [
            {
                "Job Title": "Data Analyst",
                "Company": "Alpha",
                "Location": "Singapore",
                "Job Posting Date": "2026-04-01",
                "Job URL": "https://example.com/alpha-1",
            },
            {
                "Job Title": "BI Analyst",
                "Company": "Beta",
                "Location": "Remote",
                "Job Posting Date": "2026-04-02",
                "Job URL": "",
            },
        ]
    )

    original_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if path == "bronze_datasets/(Final)_past_Technology.csv":
            return StringIO("placeholder")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(skillsgauge_app.pd, "read_csv", lambda *args, **kwargs: csv_df.copy())

    client = skillsgauge_app.app.test_client()
    with client.session_transaction() as session:
        session["industry"] = "Technology"
        session["userSkills"] = ["SQL", "Python"]
        session["resume_uploaded"] = True

    response = client.post(
        "/industry_applications/bulk",
        data={"selected_jobs": ["0", "1"]},
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Bulk Apply for Technology" in page
    assert "Submitted 1 application(s) successfully." in page
    assert "1 application(s) failed." in page
