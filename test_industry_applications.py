"""Tests for industry application shortlist helpers."""

import builtins
from io import StringIO
import os

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
    assert result["summary_message"] == "Submitted 1 application(s) successfully. 1 application(s) failed."
    assert result["results"][0]["application_status"] == "Submitted"
    assert result["results"][1]["application_status"] == "Failed"


def test_process_bulk_applications_requires_selection_for_feedback():
    result = process_bulk_applications(
        shortlist=[{"job_title": "Data Analyst", "company": "Alpha", "job_url": "https://example.com"}],
        selected_indexes=[],
        user_profile={"industry": "Technology", "skills": ["SQL"]},
    )

    assert result["success_count"] == 0
    assert result["failure_count"] == 0
    assert result["alert_class"] == "alert-info"
    assert result["summary_message"] == "Select at least one job before submitting bulk applications."


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


def test_job_application_route_shows_validation_errors():
    client = skillsgauge_app.app.test_client()
    with client.session_transaction() as session:
        session["industry"] = "Technology"
        session["userSkills"] = ["SQL", "Python"]
        session["resume_uploaded"] = True

    response = client.post(
        "/job_application",
        data={
            "name": "",
            "email": "invalid-email",
            "job_role": "",
            "company": "",
            "supporting_info": "Available immediately.",
        },
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Name is required." in page
    assert "Enter a valid email address." in page
    assert "Enter a job role or company before submitting." in page


def test_job_application_route_prefills_context_from_session_and_query():
    client = skillsgauge_app.app.test_client()
    with client.session_transaction() as session:
        session["industry"] = "Technology"
        session["userSkills"] = ["SQL", "Python"]
        session["resume_uploaded"] = True
        session["applicant_name"] = "Alex Tan"
        session["applicant_email"] = "alex@example.com"

    response = client.get("/job_application?job_role=Data+Analyst&company=Alpha")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "value=\"Alex Tan\"" in page
    assert "value=\"alex@example.com\"" in page
    assert "value=\"Data Analyst\"" in page
    assert "value=\"Alpha\"" in page
    assert "Technology" in page
    assert "SQL" in page
    assert "Python" in page


def test_job_application_route_reuses_last_selected_context_from_session():
    client = skillsgauge_app.app.test_client()
    with client.session_transaction() as session:
        session["industry"] = "Technology"
        session["userSkills"] = ["SQL", "Python"]
        session["resume_uploaded"] = True
        session["applicant_name"] = "Alex Tan"
        session["applicant_email"] = "alex@example.com"
        session["last_applied_job_role"] = "Data Analyst"
        session["last_applied_company"] = "Alpha"

    response = client.get("/job_application")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "value=\"Alex Tan\"" in page
    assert "value=\"alex@example.com\"" in page
    assert "value=\"Data Analyst\"" in page
    assert "value=\"Alpha\"" in page


def test_job_application_route_submits_successfully(monkeypatch):
    captured_submission = {}

    def fake_save_job_application_submission(submission_data):
        captured_submission.update(submission_data)

    monkeypatch.setattr(
        skillsgauge_app,
        "save_job_application_submission",
        fake_save_job_application_submission,
    )

    client = skillsgauge_app.app.test_client()
    with client.session_transaction() as session:
        session["industry"] = "Technology"
        session["userSkills"] = ["SQL", "Python"]
        session["resume_uploaded"] = True

    response = client.post(
        "/job_application",
        data={
            "name": "Alex Tan",
            "email": "alex@example.com",
            "job_role": "Data Analyst",
            "company": "Alpha",
            "supporting_info": "Portfolio: https://example.com/portfolio",
        },
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Your job application for Data Analyst at Alpha was submitted successfully." in page
    assert captured_submission["name"] == "Alex Tan"
    assert captured_submission["email"] == "alex@example.com"
    assert captured_submission["job_role"] == "Data Analyst"
    assert captured_submission["company"] == "Alpha"
    assert captured_submission["industry"] == "Technology"
    assert captured_submission["skills"] == "SQL, Python"
    assert captured_submission["resume_uploaded"] is True
    with client.session_transaction() as session:
        assert session["applicant_name"] == "Alex Tan"
        assert session["applicant_email"] == "alex@example.com"
        assert session["last_applied_job_role"] == "Data Analyst"
        assert session["last_applied_company"] == "Alpha"


def test_load_saved_job_applications_filters_by_email(tmp_path, monkeypatch):
    submissions_file = tmp_path / "job_application_submissions.csv"
    submissions_file.write_text(
        "\n".join(
            [
                "submitted_at,name,email,job_role,company,supporting_info,industry,skills,resume_uploaded",
                "2026-04-09T12:00:00,Alex Tan,alex@example.com,Data Analyst,Alpha,,Technology,\"SQL, Python\",True",
                "2026-04-10T12:00:00,Sam Lee,sam@example.com,Engineer,Beta,,Engineering,Python,True",
                "2026-04-11T12:00:00,Alex Tan,ALEX@example.com,BI Analyst,Gamma,,Technology,SQL,False",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        skillsgauge_app,
        "APPLICATION_SUBMISSIONS_FILE",
        str(submissions_file),
    )

    saved_applications = skillsgauge_app.load_saved_job_applications("alex@example.com")

    assert len(saved_applications) == 2
    assert saved_applications[0]["job_role"] == "BI Analyst"
    assert saved_applications[1]["job_role"] == "Data Analyst"


def test_profile_route_shows_jobs_applied(tmp_path, monkeypatch):
    submissions_file = tmp_path / "job_application_submissions.csv"
    submissions_file.write_text(
        "\n".join(
            [
                "submitted_at,name,email,job_role,company,supporting_info,industry,skills,resume_uploaded",
                "2026-04-09T12:00:00,Alex Tan,alex@example.com,Data Analyst,Alpha,,Technology,\"SQL, Python\",True",
                "2026-04-10T12:00:00,Jordan,jordan@example.com,Engineer,Beta,,Engineering,Python,True",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        skillsgauge_app,
        "APPLICATION_SUBMISSIONS_FILE",
        str(submissions_file),
    )

    client = skillsgauge_app.app.test_client()
    with client.session_transaction() as session:
        session["applicant_name"] = "Alex Tan"
        session["applicant_email"] = "alex@example.com"

    response = client.get("/profile")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Profile" in page
    assert "Alex Tan" in page
    assert "alex@example.com" in page
    assert "Jobs Applied" in page
    assert "Data Analyst" in page
    assert "Alpha" in page
    assert "Engineer" not in page


def test_save_job_application_submission_writes_csv(tmp_path, monkeypatch):
    submissions_file = tmp_path / "job_application_submissions.csv"

    monkeypatch.setitem(skillsgauge_app.app.config, "UPLOAD_FOLDER", str(tmp_path))
    monkeypatch.setattr(
        skillsgauge_app,
        "APPLICATION_SUBMISSIONS_FILE",
        str(submissions_file),
    )

    skillsgauge_app.save_job_application_submission(
        {
            "submitted_at": "2026-04-09T12:00:00",
            "name": "Alex Tan",
            "email": "alex@example.com",
            "job_role": "Data Analyst",
            "company": "Alpha",
            "supporting_info": "Portfolio attached",
            "industry": "Technology",
            "skills": "SQL, Python",
            "resume_uploaded": True,
        }
    )

    saved_content = submissions_file.read_text(encoding="utf-8")
    assert "submitted_at,name,email,job_role,company,supporting_info,industry,skills,resume_uploaded" in saved_content
    assert "Alex Tan,alex@example.com,Data Analyst,Alpha,Portfolio attached,Technology,\"SQL, Python\",True" in saved_content


def test_job_application_route_shows_save_error(monkeypatch):
    def fake_save_job_application_submission(submission_data):
        raise OSError("disk full")

    monkeypatch.setattr(
        skillsgauge_app,
        "save_job_application_submission",
        fake_save_job_application_submission,
    )

    client = skillsgauge_app.app.test_client()
    with client.session_transaction() as session:
        session["industry"] = "Technology"
        session["userSkills"] = ["SQL", "Python"]
        session["resume_uploaded"] = True

    response = client.post(
        "/job_application",
        data={
            "name": "Alex Tan",
            "email": "alex@example.com",
            "job_role": "Data Analyst",
            "company": "Alpha",
            "supporting_info": "Available immediately.",
        },
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "We could not save your application right now. Please try again." in page


def test_update_skills_keeps_application_submission_csv(tmp_path):
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    resume_file = uploads_dir / "resume.pdf"
    resume_file.write_text("resume")
    submissions_file = uploads_dir / "job_application_submissions.csv"
    submissions_file.write_text("submitted_at,name\n")

    original_upload_folder = skillsgauge_app.UPLOAD_FOLDER
    original_config_upload_folder = skillsgauge_app.app.config["UPLOAD_FOLDER"]
    original_submissions_file = skillsgauge_app.APPLICATION_SUBMISSIONS_FILE

    skillsgauge_app.UPLOAD_FOLDER = str(uploads_dir)
    skillsgauge_app.app.config["UPLOAD_FOLDER"] = str(uploads_dir)
    skillsgauge_app.APPLICATION_SUBMISSIONS_FILE = str(submissions_file)

    try:
        client = skillsgauge_app.app.test_client()
        with client.session_transaction() as session:
            session["industry"] = "Technology"

        response = client.post(
            "/update_skills",
            data={"skills": ["SQL", "Python"]},
        )

        assert response.status_code == 302
        assert not resume_file.exists()
        assert submissions_file.exists()
        assert os.path.getsize(submissions_file) > 0
    finally:
        skillsgauge_app.UPLOAD_FOLDER = original_upload_folder
        skillsgauge_app.app.config["UPLOAD_FOLDER"] = original_config_upload_folder
        skillsgauge_app.APPLICATION_SUBMISSIONS_FILE = original_submissions_file
