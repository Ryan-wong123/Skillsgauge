import pandas as pd
import plotly.graph_objects as go
import ast
import plotly.express as px
import json
import csv
from io import StringIO


#============================================       helper code     =============================================

# Filters the DataFrame to include only rows where the 'Job Title' matches the specified job role.
def filter_df_by_job_role(df, job_role):

        job_role_df = df[df["Job Title"] == job_role].copy()
        return job_role_df

# Filters a list of skills, removing any skill that is an empty string or contains only whitespace.
def filter_skills(skills_list):

    skills_list = list(skills_list)
    new_skill_list = []
    for skill in skills_list:
        if len(skill) > 1:
            new_skill_list.append(skill)

# Extracts the unique 'Broader Category' from the DataFrame, converts it to a string, and replaces spaces with underscores.
def get_industry_name(df):
    industry_name = df["Broader Category"].unique()
    industry_name = str(industry_name)
    industry_name = industry_name[2:-2]
    industry_name = industry_name.replace(" ", "_")
    return industry_name

# ========================================    Industry Section      ========================================================

def industry_job_trend(df):
    try:
        # group each industry data by industry and separate to individual industry df
        industry_df = df.groupby("Broader Category")
        df_list = [industry_df.get_group(x) for x in industry_df.groups]

        json_dict = {}
        for df in df_list:
            # get the current date year and quarter and exclude from analysis
            current_date = pd.Timestamp.now()
            current_year_quarter = f"{current_date.year}Q{current_date.quarter}"
            exclude_current_q = df[~(df["Year-Quarter"] == current_year_quarter)]
            df = exclude_current_q.copy(deep=True)

            # exclude job roles data with less than 10 rows
            job_count = exclude_current_q["Job Title"].value_counts()
            job_to_keep = job_count[job_count > 9].index
            df = df[df['Job Title'].isin(job_to_keep)]


            # change date to pd datetime format
            df['Job Posting Date'] = pd.to_datetime(df['Job Posting Date'], format="%Y-%m-%d")

            # set date to period and sort by quarter
            df["Quarter"] = df["Job Posting Date"].dt.to_period("Q")

            industry_name = get_industry_name(df)

            # count number of job per quarter
            job_per_quarter_count = df.groupby(["Job Title", "Quarter"]).size().to_frame("Count of job per quarter").reset_index()
            job_per_quarter_count = job_per_quarter_count.sort_values(by="Quarter")
            job_per_quarter_count = job_per_quarter_count.pivot_table(index="Quarter", columns="Job Title", values="Count of job per quarter", fill_value=0)
            job_per_quarter_count.reset_index(inplace=True)

            # calculate the last 6 quarter difference
            last_6_quarter = job_per_quarter_count.tail(6)
            diff_df = last_6_quarter.diff()
            sum_diff = diff_df.iloc[:,1:].sum()
            sort_df = sum_diff.sort_values()

            # get the top 5 trending job actual data point
            trending_up_job = sort_df.tail(5).index.tolist()
            trending_up_job = ["Quarter"] + trending_up_job
            result = job_per_quarter_count[trending_up_job]

            # add a line for every job role in graph
            fig = go.Figure()
            for job in result.columns[1:]:
                fig.add_trace(go.Scatter(
                    x=result['Quarter'].astype(str),
                    y=result[job],
                    mode='lines+markers',
                    name=job
                ))

            # update titles
            fig.update_layout(
                title = "Industry Job Trends",
                xaxis_title="Period",
                yaxis_title="No. of Job",
            )

            # get HTML code and save to JSON
            html_code = fig.to_html(full_html=False)
            json_dict[industry_name] = html_code

        with open("analysis/in_job_trend.json", "w") as file:
            json.dump(json_dict, file)

    except Exception as e:
        print("Something went wrong in industry job trend function")
        print(f"Details: {e}")

def pull_in_job_trend(industry):
    with open("analysis/in_job_trend.json") as file:
        job_trend = json.load(file)

    html_code = job_trend[industry]

    return html_code

# Analyzes the general skills required for each industry by counting the frequency of skills from the provided DataFrame.
def industry_general_skills(df):
    try:
        # change str type list to actual list
        df["skills"] = df["skills"].apply(ast.literal_eval)

        # group each industry data by industry and separate to individual industry df
        df = df.groupby("Broader Category")
        df_list = [df.get_group(x) for x in df.groups]
        json_dict = {}

        for df in df_list:

            industry_name = get_industry_name(df)

            # get frequency count of skills
            all_skills = df['skills'].explode()
            total_skill_count = all_skills.value_counts()

            # extract the top 20 skills and save to JSON
            top20_skill_json = total_skill_count.head(20)
            json_dict[industry_name] = top20_skill_json.to_dict()

        pd.Series(json_dict).to_json("analysis/industry_skills.json", indent=4)

    except Exception as e:
        print("something went wrong with industry general skills ")
        print(f"Details: {e}")

# Analyzes the job titles within each industry by counting how frequently each job title appears
def industry_job(data):
    try:
        # Create a dictionary to hold the final result
        result = {}

        # Group the data by industry and count job titles
        grouped_data = data.groupby('Broader Category')['Job Title'].value_counts()

        # Loop through each industry and its job titles
        for (industry, job_title), count in grouped_data.items():
            if industry not in result:
                result[industry] = {}
            result[industry][job_title] = count

        # Save the result as a JSON file
        path = "analysis/industry_Jobs.json"
        pd.Series(result).to_json(path, indent=4)

    except Exception as e:
        print("something went wrong in industry job function")
        print(f"Details: {e}")

# Retrieves the top skills for a given industry from a pre-generated JSON file.
def pull_industry_skills(industry_name):
    with open("analysis/industry_skills.json") as file:
        industry_skills = json.load(file)

    skill_list = []
    data = industry_skills[industry_name]
    # fill up skills into a list format
    for k, v in data.items():

        skill_list.append(k)

    return skill_list

# Analyzes hiring trends by industry based on job posting dates, generating a median job count for each month and saving the results as HTML for visualization.
def industry_hiring_trend(df):
    try:

        # setting type to date time format
        df['Job Posting Date'] = pd.to_datetime(df['Job Posting Date'], format="%Y-%m-%d")

        # extract month from data
        df["Month"] = df["Job Posting Date"].dt.month
        df["Year"] = df["Job Posting Date"].dt.year

        # separate different industry to its own df
        df = df.groupby("Broader Category")
        df_list = [df.get_group(x) for x in df.groups]
        json_dict ={}
        for df in df_list:
            industry_name = get_industry_name(df)

            # group by month and year and get count of job
            monthly_counts = df.groupby(['Year', 'Month']).size().reset_index(name='Count of job')

            # further group all years by month before getting median
            median_counts = monthly_counts.groupby('Month')['Count of job'].median().reset_index()

            month_names = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]

            # enter data into plotly
            fig = px.area(median_counts, x=month_names, y="Count of job")
            fig.update_yaxes(range=[median_counts["Count of job"].min() * 0.75, median_counts["Count of job"].max() + 25])

            fig.update_layout(
                title = "Industry Hiring Trends",
                xaxis_title="Period",
                yaxis_title="Median No. of Job per Month",
            )

            html_code = fig.to_html(full_html=False)

            json_dict[industry_name] = html_code

        with open("analysis/in_hiring_trend.json" , "w") as file:
            json.dump(json_dict, file, indent=4)

    except Exception as e:
        print("something went wrong in industry hiring trend")
        print(f"Details: {e}")

def pull_in_hiring_trend(industry):
    with open("analysis/in_hiring_trend.json" , "r") as file:
        json_dict = json.load(file)

    html_code = json_dict[industry]

    return html_code

# ============================    Job Role Section      ===============================================================

# Get top 10 job roles skills and save to an analysis file
def skill_match_analysis(df, industry_name):
    try:

        # remove all the job less than 10 rows
        df["Job Title"] = df["Job Title"].str.upper()
        job_count = df["Job Title"].value_counts()
        roles_to_keep = job_count[job_count.values >= 10].index
        df = df[df["Job Title"].isin(roles_to_keep)].copy()
        df["Job Title"] = df["Job Title"].str.title()

        # get list of unique job title
        unique_job_list = df["Job Title"].unique()

        # set skill list value to list type
        try:
            df["skills"] = df["skills"].apply(ast.literal_eval)
        except:
            print("alr converted")

        json_data = {}
        for job in unique_job_list:
            # filter df to only include job with more than 10 rows
            filtered_df = df[df["Job Title"] == job]

            # get top 10 skill per job role and save to JSON
            job_skill_series = filtered_df["skills"].explode().value_counts()
            json_dict = { job : job_skill_series.head(10).to_dict()}
            json_data.update(json_dict)

        file_path = "analysis/job_role_skill_" + industry_name + ".json"
        pd.Series(json_data).to_json(file_path, indent=4)

    except Exception as e:
        print("something went wrong in skill match analysis")
        print(f"Details: {e}")

# Matches user skills to job skills and calculates the matching percentage.
def match_user_to_job_role(job_role_skills_series, user_skill_list):
    try:

        grouped = job_role_skills_series.groupby(level=0)
        # convert series to dict key value and skills to list
        job_role_skill_dict = {key: group.index.get_level_values(1).tolist() for key, group in grouped}

        match_dict = {}
        # set list to upper to be able to compare
        user_skill_list = list(map(str.upper, user_skill_list))

        for key , value in job_role_skill_dict.items():
            # convert job role skills to upper and compare to find matching percent
            value = list(map(str.upper, value))
            matched_skill = set(value) & set(user_skill_list)

            if matched_skill:
                # percentage calculated by length of match skills over len of job role skills * 100
                percentage = (len(matched_skill) / len(set(value))) * 100
                match_dict[key] = round(percentage)

        return match_dict, job_role_skill_dict

    except Exception as e:
        print("something went wrong in match user to job role")
        print(f"Details: {e}")

# Get job urls of the specific job
def get_job_detail_url(job_df):
    try:
        # find recent job in the past 14 days
        curr_date = pd.to_datetime('today').date()
        job_df['Job Posting Date'] = pd.to_datetime(job_df['Job Posting Date'], format='%Y-%m-%d')
        last_14_days = curr_date - pd.offsets.Day(14)
        filtered_df = job_df.query("`Job Posting Date` >= @last_14_days")

        # if more than 5 only return 5 job post
        if len(filtered_df.index) == 0:
            return None
        elif len(filtered_df.index) > 5:
            job_detail_data = filtered_df.head(5).to_dict(orient="records")
            return job_detail_data

        else:
            job_detail_data = filtered_df.to_dict(orient= "records")
            return job_detail_data

    except Exception as e:
        print("something went wrong in get job detail url")
        print(f"Details: {e}")


def _first_available_value(row, columns, default=""):
    for column in columns:
        if column in row.index:
            value = row[column]
            if pd.notna(value):
                return str(value)
    return default


def build_application_shortlist(job_df, max_jobs=20):
    try:
        if job_df is None or job_df.empty:
            return []

        working_df = job_df.copy()

        if 'Job Posting Date' in working_df.columns:
            working_df['Job Posting Date'] = pd.to_datetime(
                working_df['Job Posting Date'],
                format='%Y-%m-%d',
                errors='coerce'
            )
            working_df = working_df.sort_values(
                by='Job Posting Date',
                ascending=False,
                na_position='last'
            )

        shortlist = []
        seen_jobs = set()

        for _, row in working_df.iterrows():
            job_title = _first_available_value(row, ['Job Title'], 'Unknown Role')
            company = _first_available_value(row, ['Company', 'Company Name'], 'Unknown Company')
            location = _first_available_value(
                row,
                ['Location', 'Area', 'Region', 'Job Location'],
                'Location not provided'
            )
            posted_date = _first_available_value(row, ['Job Posting Date'], '')
            job_url = _first_available_value(row, ['Job URL', 'URL'], '')

            dedupe_key = (job_title, company, job_url)
            if dedupe_key in seen_jobs:
                continue

            seen_jobs.add(dedupe_key)
            shortlist.append({
                'job_title': job_title,
                'company': company,
                'location': location,
                'posted_date': posted_date,
                'job_url': job_url,
                'status': 'To Apply',
                'notes': ''
            })

            if len(shortlist) >= max_jobs:
                break

        return shortlist

    except Exception as e:
        print("something went wrong in build application shortlist")
        print(f"Details: {e}")
        return []


def create_application_shortlist_csv(shortlist):
    fieldnames = [
        'job_title',
        'company',
        'location',
        'posted_date',
        'job_url',
        'status',
        'notes'
    ]

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for job in shortlist:
        writer.writerow({field: job.get(field, '') for field in fieldnames})

    return output.getvalue()


def process_bulk_applications(shortlist, selected_indexes, user_profile=None):
    selected_indexes = selected_indexes or []
    results = []

    if not shortlist:
        return {
            "results": results,
            "success_count": 0,
            "failure_count": 0,
            "selected_count": 0,
            "processed_count": 0,
            "alert_class": "alert-info",
            "summary_message": "No suitable jobs are available for bulk application yet.",
        }

    if not selected_indexes:
        return {
            "results": results,
            "success_count": 0,
            "failure_count": 0,
            "selected_count": 0,
            "processed_count": 0,
            "alert_class": "alert-info",
            "summary_message": "Select at least one job before submitting bulk applications.",
        }

    if len(selected_indexes) > 1:
        return {
            "results": results,
            "success_count": 0,
            "failure_count": 0,
            "selected_count": len(selected_indexes),
            "processed_count": 0,
            "alert_class": "alert-danger",
            "summary_message": "Only one job application can be submitted per draft.",
        }

    for raw_index in selected_indexes:
        try:
            index = int(raw_index)
        except (TypeError, ValueError):
            continue

        if index < 0 or index >= len(shortlist):
            continue

        job = shortlist[index]
        application_status = "Submitted"
        status_message = "Application submitted successfully."

        if not job.get("job_url"):
            application_status = "Failed"
            status_message = "Application could not be submitted because the job link is unavailable."
        elif user_profile and not user_profile.get("industry"):
            application_status = "Failed"
            status_message = "Application could not be submitted because the industry profile is missing."
        elif user_profile and not user_profile.get("skills"):
            application_status = "Submitted"
            status_message = "Application submitted with a limited profile because no saved skills were found."

        results.append(
            {
                **job,
                "application_status": application_status,
                "status_message": status_message,
            }
        )

    success_count = sum(1 for job in results if job["application_status"] == "Submitted")
    failure_count = len(results) - success_count

    if not results:
        alert_class = "alert-warning"
        summary_message = "No valid jobs were processed from the selected application batch."
    elif failure_count == 0:
        alert_class = "alert-success"
        summary_message = f"Submitted {success_count} application(s) successfully."
    elif success_count == 0:
        alert_class = "alert-danger"
        summary_message = f"All {failure_count} selected application(s) failed."
    else:
        alert_class = "alert-warning"
        summary_message = (
            f"Submitted {success_count} application(s) successfully. "
            f"{failure_count} application(s) failed."
        )

    return {
        "results": results,
        "success_count": success_count,
        "failure_count": failure_count,
        "selected_count": len(selected_indexes),
        "processed_count": len(results),
        "alert_class": alert_class,
        "summary_message": summary_message,
    }
