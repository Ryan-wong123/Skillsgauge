"""Tests for industry application shortlist helpers."""

import pandas as pd

from data_analysis import build_application_shortlist, create_application_shortlist_csv


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
