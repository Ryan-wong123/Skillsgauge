"""Tests for industry-level application links."""
import pandas as pd

from data_analysis import get_industry_application_links


def test_get_industry_application_links_filters_and_deduplicates():
    today = pd.Timestamp.today().normalize()
    df = pd.DataFrame(
        [
            {
                "Job Title": "Data Analyst",
                "Company": "Alpha",
                "Job URL": "https://example.com/alpha-old",
                "Job Posting Date": (today - pd.Timedelta(days=4)).strftime("%Y-%m-%d"),
            },
            {
                "Job Title": "Senior Data Analyst",
                "Company": "Alpha",
                "Job URL": "https://example.com/alpha-new",
                "Job Posting Date": (today - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            },
            {
                "Job Title": "BI Developer",
                "Company": "Beta",
                "Job URL": "https://example.com/beta",
                "Job Posting Date": (today - pd.Timedelta(days=2)).strftime("%d/%m/%Y"),
            },
            {
                "Job Title": "Legacy Role",
                "Company": "Gamma",
                "Job URL": "https://example.com/gamma",
                "Job Posting Date": (today - pd.Timedelta(days=45)).strftime("%Y-%m-%d"),
            },
        ]
    )

    result = get_industry_application_links(df, max_jobs=10, recency_days=30)

    assert len(result) == 2
    assert result[0]["company"] == "Alpha"
    assert result[0]["job_title"] == "Senior Data Analyst"
    assert result[0]["job_url"] == "https://example.com/alpha-new"
    assert result[1]["company"] == "Beta"
