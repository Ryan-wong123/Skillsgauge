import os
import pandas as pd
import plotly.graph_objects as go
import ast
import plotly.express as px
import json


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


# ============================    Cross-Industry Job Matching      ==============================================================

# Import resume skills extractor for skill extraction from job descriptions
import resume_skills_extractor


def get_all_industry_csv_files():
    """Get list of all industry CSV files in bronze_datasets."""
    import glob
    # Look for JobStreet CSV files in bronze_datasets/JS/
    pattern = os.path.join('bronze_datasets', 'JS', 'js_*.csv')
    files = glob.glob(pattern)
    
    # Also check root directory for main CSV files
    root_pattern = os.path.join('.', '*.csv')
    root_files = glob.glob(root_pattern)
    
    # Combine both
    all_files = files + [f for f in root_files if 'job_street' in f.lower() or 'mcf' in f.lower()]
    return all_files


def _extract_skills_from_job_description(description, industry_files, general_skills_file):
    """Extract skills from job description text using the resume_skills_extractor logic.
    
    Args:
        description: Job description text
        industry_files: List of industry skill JSON files
        general_skills_file: Path to general skills JSON file
        
    Returns:
        List of extracted skills
    """
    if not description or pd.isna(description):
        return []
    
    text = resume_skills_extractor._normalize_text(description)
    
    # Load all industry skills and general skills
    all_skills = {}
    for industry_file in industry_files:
        industry_skills = resume_skills_extractor._load_skills(industry_file)
        all_skills.update(industry_skills)
    
    general_skills = resume_skills_extractor._load_skills(general_skills_file)
    all_skills.update(general_skills)
    
    # Extract matching skills
    extracted_skills = set()
    for skill, aliases in all_skills.items():
        variants = [skill] + resume_skills_extractor._alias_list(aliases)
        normalized_variants = {resume_skills_extractor._normalize_text(str(v)) for v in variants}
        
        if any(resume_skills_extractor._contains_skill(text, v) for v in normalized_variants):
            extracted_skills.add(skill.lower().strip())
    
    return sorted(extracted_skills)


def load_all_industry_data():
    """Load and combine data from all industry CSV files with extracted skills."""
    try:
        files = get_all_industry_csv_files()
        all_data = []
        
        for file_path in files:
            try:
                # Use on_bad_lines='skip' to handle malformed rows
                df = pd.read_csv(file_path, index_col=False, on_bad_lines='skip')
                
                # Only process files that don't have Skills column or have empty Skills
                if 'Skills' not in df.columns:
                    # No Skills column - need to extract from Job Description
                    if 'Job Description' in df.columns:
                        df['Skills'] = df['Job Description'].apply(
                            lambda desc: _extract_skills_from_job_description(
                                desc,
                                resume_skills_extractor.industry_files,
                                resume_skills_extractor.general_skills_file
                            ) if pd.notna(desc) else []
                        )
                
                all_data.append(df)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        return None
        
    except Exception as e:
        print(f"Error in load_all_industry_data: {e}")
        return None


def get_all_job_roles():
    """Get all unique job roles across all industries."""
    try:
        df = load_all_industry_data()
        if df is None or df.empty:
            return {}
        
        # Ensure skills column is properly converted
        # The column might be 'Skills' (string) or 'skills' (list)
        skill_col = 'Skills' if 'Skills' in df.columns else 'skills'
        
        def parse_skills(skill_val):
            """Parse skills from various formats."""
            if pd.isna(skill_val):
                return []
            if isinstance(skill_val, list):
                return skill_val
            try:
                # Try to parse as list
                return ast.literal_eval(skill_val)
            except:
                # If it's a string, return as single item list
                return [skill_val] if skill_val else []
        
        df['parsed_skills'] = df[skill_col].apply(parse_skills)
        
        # Group by Job Title and collect skills
        job_roles_dict = {}
        for job_title in df['Job Title'].unique():
            job_df = df[df['Job Title'] == job_title]
            # Get top skills for this job from parsed skills
            all_skills = job_df['parsed_skills'].explode()
            # Filter out empty strings
            all_skills = all_skills[all_skills != '']
            skill_counts = all_skills.value_counts()
            job_roles_dict[job_title] = skill_counts.head(15).index.tolist()
        
        return job_roles_dict
        
    except Exception as e:
        print(f"Error in get_all_job_roles: {e}")
        return {}


def match_user_skills_to_all_jobs(user_skills, job_roles_dict=None):
    """Match user skills to all job roles across industries.
    
    Args:
        user_skills: List of user skills
        job_roles_dict: Optional pre-loaded job roles dict
        
    Returns:
        List of tuples (job_title, match_percentage, industry) sorted by match
    """
    try:
        if job_roles_dict is None:
            job_roles_dict = get_all_job_roles()
        
        if not job_roles_dict:
            return []
        
        # Normalize user skills to uppercase for comparison
        user_skills_upper = [skill.upper() for skill in user_skills]
        
        matches = []
        
        for job_title, required_skills in job_roles_dict.items():
            # Normalize job skills to uppercase
            job_skills_upper = [skill.upper() for skill in required_skills]
            
            # Find matching skills
            matched = set(user_skills_upper) & set(job_skills_upper)
            
            if matched:
                # Calculate match percentage
                percentage = (len(matched) / len(set(job_skills_upper))) * 100
                matches.append((job_title, round(percentage), len(matched), list(matched)))
        
        # Sort by match percentage (highest first), then by number of matched skills
        matches.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        return matches[:20]  # Return top 20 matches
        
    except Exception as e:
        print(f"Error in match_user_skills_to_all_jobs: {e}")
        return []
