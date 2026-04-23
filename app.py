
from flask import Flask, render_template, request, redirect, url_for, session, Response
from Analysis_Visualisation import load_data, analyse_industry_distribution, create_job_title_bubble_chart,create_salary_variation_chart, skills_comparison,generate_wordcloud,create_salary_growth_chart,create_salary_trend_chart,skill_in_demand
import resume_skills_extractor
import os
import pandas as pd
import Course_Url_Coursera 
from data_analysis import industry_job_trend , industry_general_skills, pull_industry_skills , industry_hiring_trend , skill_match_analysis , match_user_to_job_role, filter_df_by_job_role,industry_job,pull_in_job_trend,  pull_in_hiring_trend , get_job_detail_url, build_application_shortlist, create_application_shortlist_csv, process_bulk_applications
import threading
import copy
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Uploads folder name
UPLOAD_FOLDER = 'uploads'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
APPLICATION_SUBMISSIONS_FILE = os.path.join(UPLOAD_FOLDER, 'job_application_submissions.csv')

# Data set file path
file_path = r'bronze_datasets\\sg_job_data_cleaned.csv'

industry_list = []

# Class representing an industry
class Industry:
    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return f"Industry(title='{self.title}')"

    def __str__(self):
        return self.title

# Class representing a job role
class JobRole:
    def __init__(self, title, skill, match_percent = 0):

        self.title = title
        self.skill = skill
        self.match_percent = match_percent


def build_job_application_context(job_role=None, company=None):
    user_skills = session.get('userSkills', [])
    return {
        "name": session.get('applicant_name', ''),
        "email": session.get('applicant_email', ''),
        "job_role": job_role or session.get('last_applied_job_role', ''),
        "company": company or session.get('last_applied_company', ''),
        "supporting_info": '',
        "industry": session.get('industry', ''),
        "skills": user_skills,
        "resume_uploaded": session.get('resume_uploaded', False) or bool(user_skills),
    }


def validate_job_application_form(form_data):
    errors = []
    name = form_data.get('name', '').strip()
    email = form_data.get('email', '').strip()
    job_role = form_data.get('job_role', '').strip()
    company = form_data.get('company', '').strip()

    if not name:
        errors.append("Name is required.")

    if not email:
        errors.append("Email is required.")
    elif "@" not in email or "." not in email.split("@")[-1]:
        errors.append("Enter a valid email address.")

    if not job_role and not company:
        errors.append("Enter a job role or company before submitting.")

    return errors


def save_job_application_submission(submission_data):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file_exists = os.path.exists(APPLICATION_SUBMISSIONS_FILE)
    fieldnames = [
        'submitted_at',
        'name',
        'email',
        'job_role',
        'company',
        'supporting_info',
        'industry',
        'skills',
        'resume_uploaded',
    ]

    with open(APPLICATION_SUBMISSIONS_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(submission_data)


def load_job_application_submissions(email=None):
    if not os.path.exists(APPLICATION_SUBMISSIONS_FILE):
        return []

    with open(APPLICATION_SUBMISSIONS_FILE, newline='', encoding='utf-8') as csvfile:
        applications = list(csv.DictReader(csvfile))

    if email:
        email = email.strip().lower()
        applications = [
            application for application in applications
            if application.get('email', '').strip().lower() == email
        ]

    applications.sort(key=lambda application: application.get('submitted_at', ''), reverse=True)
    return applications


def clear_uploaded_resume_files():
    if not os.path.isdir(UPLOAD_FOLDER):
        return

    submissions_filename = os.path.basename(APPLICATION_SUBMISSIONS_FILE)
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename == submissions_filename:
            continue

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

@app.route('/')
def Home():
    # Load the data and make copy of data
    data = load_data(file_path)
    data1 = copy.deepcopy(data)
    data2 = copy.deepcopy(data)
    data3 = copy.deepcopy(data)
    
    # Start the jobs in separate threads
    thread1 = threading.Thread(target=industry_job, args=(data3,))
    thread2 = threading.Thread(target=industry_job_trend, args=(data1,))
    thread3 = threading.Thread(target=industry_hiring_trend, args=(data2,))
    thread4 = threading.Thread(target=industry_general_skills, args=(data,))
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    
    return render_template('home.html')

@app.route('/industries')
def Industries():
    # Load CSV file
    data = load_data(file_path)
    industry_list.clear()

    # Count occurrences of each industry (Broader Category)
    industry_counts = data['Broader Category'].value_counts().reset_index()
    industry_counts.columns = ['Broader Category', 'count']  # Rename columns to 'Broader Category' and 'count'

    # Get all industries (sorted alphabetically)
    all_industries = industry_counts.sort_values(by='Broader Category').reset_index(drop=True)

    # Analyze the industry distribution
    industry_distribution, total_jobs = analyse_industry_distribution(data)

    # Create industry list to pass to the template
    industry_list.clear()
    for idx, row in all_industries.iterrows():
        industry = Industry(title=row['Broader Category'])
        industry_list.append(industry)

    return render_template('industries.html', all_industries=industry_list, total_jobs=total_jobs, 
                           industry_distribution=industry_distribution)

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def analyse_industry_distribution(data):
    # Group data by 'Broader Category'
    industry_distribution = data['Broader Category'].value_counts()
    total_jobs = len(data)
    return industry_distribution, total_jobs

# Handle individual industry charts and web page
@app.route('/industry_details', methods=['POST'])
def industry_details():

    # Get the industry name from the form submission and store it in the session
    industry_name_orig = request.form.get('industry_name')
    session["industry"] = industry_name_orig

    # Find the industry object from industry_list that matches the given title, or return None if not found
    industry = next((ind for ind in industry_list if ind.title == industry_name_orig), None)

    # Load the industry-related data from the specified file path
    data = load_data(file_path)

    #  --- Calling of Analysis and Visualisation Functions ---
    job_title_chart = create_job_title_bubble_chart(data, industry_name_orig) # Call the Bubble chart function
    salary_chart = create_salary_variation_chart(data, industry_name_orig)  # Call the Salary Box chart function
    salary_trend_chart = create_salary_trend_chart(data, industry_name_orig)  # Call the Salary trend Line chart function
    salary_growth_chart = create_salary_growth_chart(data, industry_name_orig) # Call the the salary growth chart
    # --------------------------------------------------------

    # find industry general skills
    industry_name = industry_name_orig.replace(" ", "_")

    # Path to the dataset for the specific industry 
    industry_path = "bronze_datasets/(Final)_past_" + industry_name + ".csv"

    with open(industry_path , encoding='utf-8') as csvfile:
        df = pd.read_csv(csvfile, index_col=False)

    # analysis for job role skills
    skill_match_analysis(df,industry_name)

    # pulling of all json data
    skill_list = pull_industry_skills( industry_name)
    job_trend_code = pull_in_job_trend(industry_name)
    hiring_trend_code = pull_in_hiring_trend(industry_name)
    application_shortlist = build_application_shortlist(df)

    # Generate a list of other industries for the sidebar, limited to 4 items
    other_industries = [ind.title for ind in industry_list if ind.title != industry_name_orig][:4]
    other_industries = other_industries[:4] 
    
    # Generate a word cloud visualization based on the industry's job titles
    wordCloud = generate_wordcloud(industry_name)

    return render_template('industry_details.html',  
                           industry=industry, 
                           other_industries=other_industries, 
                           job_trend_fig=job_trend_code,
                           skill_list = skill_list,
                           application_shortlist=application_shortlist,
                           wordCloud = wordCloud,
                           hiring_trend_fig = hiring_trend_code,
                           salary_growth_chart = salary_growth_chart,
                           job_title_chart=job_title_chart,
                           salary_chart=salary_chart,
                           salary_trend_chart = salary_trend_chart)    


@app.route('/industry_applications/export')
def export_industry_applications():
    if 'industry' not in session:
        return redirect(url_for("Industries"))

    industry_name = session["industry"].replace(" ", "_")
    industry_path = "bronze_datasets/(Final)_past_" + industry_name + ".csv"

    with open(industry_path, encoding='utf-8') as csvfile:
        df = pd.read_csv(csvfile, index_col=False)

    shortlist = build_application_shortlist(df)
    csv_content = create_application_shortlist_csv(shortlist)
    download_name = f"{industry_name.lower()}_application_shortlist.csv"

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment; filename={download_name}"}
    )


@app.route('/industry_applications/bulk', methods=['GET', 'POST'])
def bulk_industry_applications():
    if 'industry' not in session:
        return redirect(url_for("Industries"))

    industry_name = session["industry"]
    industry_key = industry_name.replace(" ", "_")
    industry_path = "bronze_datasets/(Final)_past_" + industry_key + ".csv"

    with open(industry_path, encoding='utf-8') as csvfile:
        df = pd.read_csv(csvfile, index_col=False)

    shortlist = build_application_shortlist(df)
    user_skills = session.get('userSkills', [])
    user_profile = {
        "industry": industry_name,
        "skills": user_skills,
        "resume_ready": session.get('resume_uploaded', False) or bool(user_skills),
    }

    submission_summary = None
    selected_indexes = []

    if request.method == 'POST':
        selected_indexes = request.form.getlist('selected_jobs')
        submission_summary = process_bulk_applications(shortlist, selected_indexes, user_profile)

    return render_template(
        'bulk_industry_applications.html',
        industry=industry_name,
        shortlist=shortlist,
        user_profile=user_profile,
        submission_summary=submission_summary,
        selected_indexes=selected_indexes,
    )


@app.route('/job_application', methods=['GET', 'POST'])
def job_application():
    job_role = request.args.get('job_role', '').strip()
    company = request.args.get('company', '').strip()
    form_data = build_job_application_context(job_role=job_role, company=company)
    success_message = None
    error_messages = []

    if request.method == 'POST':
        form_data = {
            "name": request.form.get('name', '').strip(),
            "email": request.form.get('email', '').strip(),
            "job_role": request.form.get('job_role', '').strip(),
            "company": request.form.get('company', '').strip(),
            "supporting_info": request.form.get('supporting_info', '').strip(),
            "industry": session.get('industry', ''),
            "skills": session.get('userSkills', []),
            "resume_uploaded": session.get('resume_uploaded', False) or bool(session.get('userSkills', [])),
        }

        error_messages = validate_job_application_form(form_data)

        if not error_messages:
            submission_record = {
                "submitted_at": datetime.utcnow().isoformat(timespec='seconds'),
                "name": form_data["name"],
                "email": form_data["email"],
                "job_role": form_data["job_role"],
                "company": form_data["company"],
                "supporting_info": form_data["supporting_info"],
                "industry": form_data["industry"],
                "skills": ", ".join(form_data["skills"]),
                "resume_uploaded": form_data["resume_uploaded"],
            }

            try:
                save_job_application_submission(submission_record)
                session['applicant_name'] = form_data["name"]
                session['applicant_email'] = form_data["email"]
                session['last_applied_job_role'] = form_data["job_role"]
                session['last_applied_company'] = form_data["company"]
                applied_target = form_data["job_role"] or form_data["company"]
                if form_data["job_role"] and form_data["company"]:
                    applied_target = f'{form_data["job_role"]} at {form_data["company"]}'
                success_message = f"Your job application for {applied_target} was submitted successfully."
                form_data = build_job_application_context(
                    job_role=form_data["job_role"],
                    company=form_data["company"],
                )
            except OSError:
                error_messages.append("We could not save your application right now. Please try again.")

    return render_template(
        'job_application.html',
        form_data=form_data,
        success_message=success_message,
        error_messages=error_messages,
    )


@app.route('/profile')
def Profile():
    applicant_email = session.get('applicant_email', '')
    applied_jobs = load_job_application_submissions(applicant_email) if applicant_email else []
    profile_context = {
        "name": session.get('applicant_name', ''),
        "email": applicant_email,
        "industry": session.get('industry', ''),
        "skills": session.get('userSkills', []),
        "resume_uploaded": session.get('resume_uploaded', False) or bool(session.get('userSkills', [])),
        "applied_jobs": applied_jobs,
        "amos_role": "Amos is responsible for the user profile job-tracking view and the job-adding workflow for saved applications.",
    }

    return render_template('profile.html', profile=profile_context)

#show the job roles page with suitable jobs
@app.route('/job_roles')
def Job_roles():

    # Retrieve the user's skills from the session if available, else use an empty list
    if 'userSkills' in session:
        userSkills = session['userSkills']
    else:
        userSkills = []

    # Check if the industry is available in the session
    if 'industry' in session:
        industry_name = session["industry"]
        # Replace spaces with underscores in the industry name to match the JSON file path format
        industry_name = industry_name.replace(" ", "_")
        # Construct the path to the job role skill analysis JSON file for the selected industry
        path = "analysis/job_role_skill_"+industry_name+".json"

    else:
        # If no industry is found in session, redirect the user to the Industries page
        print("no industry")
        return redirect(url_for("Industries"))

    # Open the JSON file that contains job role skill data
    with open(path) as file:
        # Load the JSON data into a DataFrame and stack it to get job roles and their associated skills
        job_role_skill_df = pd.read_json(file, orient="index")
        job_role_skills_series = job_role_skill_df.stack()

    # Match the user's skills to job roles based on the loaded data
    match_dict , job_role_skill_dict = match_user_to_job_role(job_role_skills_series, userSkills)

    job_role_list = []
    print(job_role_skill_dict)
    # if no match job take the first 6 job roles
    if len(match_dict) == 0:
        no_match_list  = list(job_role_skill_dict.items())[:6]
        
        # Loop through each job role and add it to the job_role_list with 0% match
        for job in no_match_list:
            print(job)

            job_object = JobRole(job[0], job[1],0)
            job_role_list.append(job_object)

    else:   
        # If matches are found, add them to the list with the corresponding match percentage
        for job, percent in match_dict.items():
            skill_list = job_role_skill_dict[job]
            job_object = JobRole(job, skill_list,int(percent))
            job_role_list.append(job_object)

    # Sort by best matching percentage
    job_role_list.sort(key=lambda x: x.match_percent, reverse=True)

    if len(job_role_list) > 15:
        job_role_list = job_role_list[:15]

    return render_template('job_roles.html', job_role=job_role_list)

# Show the individual job page
@app.route("/job_roles/<job_title>")
def expanded_job_roles(job_title):
    # Retrieve the user's skills from the session if available, else use an empty list
    if 'userSkills' in session:
        userSkills = session['userSkills'] 
    else:
        userSkills = []
    
    # Check if the industry is available in the session
    if 'industry' in session:
        industry_name = session["industry"]
        # Replace spaces with underscores in the industry name to match the JSON file path format
        industry_name = industry_name.replace(" ", "_")

    else:
        # If the industry is not found in the session, redirect the user to the "Industries" page to select an industry
        return redirect(url_for("Industries"))

    with open("bronze_datasets/(Final)_past_"+ industry_name +".csv" , encoding="utf-8") as file:
        df = pd.read_csv(file, index_col=False)
        job_df = filter_df_by_job_role(df, job_title)

    # Compare the user's skills with the skills required for a specific job title in the selected industry
    skillComparisonChart,skillsLacking , match_skills = skills_comparison(userSkills,job_title, industry_name)
    # Combine the skills lacking and the matching skills into a total skill set
    total_skill = skillsLacking + match_skills
    # Create a JobRole object with the job title and the combined list of skills
    job = JobRole(job_title, total_skill)

    # Generate a chart that shows the demand for skills in the industry using the job data (job_df)
    skillsDemandChart = skill_in_demand(job_df)
    # Show the courses link from coursera API
    urlCourses = Course_Url_Coursera.search_courses(skillsLacking)
    # Retrieve detailed job data (e.g., job descriptions, requirements, etc.) from the job data (job_df)
    job_detail_data = get_job_detail_url(job_df)

    return render_template("expanded_job_roles.html" ,
                           job_title = job_title,
                           job_role = job,
                           courses = urlCourses,
                           chart=skillComparisonChart,
                            skillsDemand_Chart = skillsDemandChart,
                           job_detail_data = job_detail_data)

# Resume upload page
@app.route('/resume')
def Resume():
    return render_template('resume.html')


@app.route('/skills')
def skill_database():
    search_query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', 'All').strip() or 'All'
    available_categories = resume_skills_extractor.get_skill_database_categories()

    if selected_category not in available_categories:
        selected_category = 'All'

    skill_catalog = resume_skills_extractor.load_skill_database(
        search_query=search_query,
        selected_category=selected_category,
    )

    return render_template('skill_database.html', skill_catalog=skill_catalog)

'''
Author: Ryan Wong
Handles the file input and editing of skills of the resume extractor
'''

# Upload resume
@app.route('/upload', methods=['POST'])
def upload_resume():
    # Check if the 'resume' key is in the request files
    if 'resume' not in request.files:
        # If no file is selected, redirect to the same page 
        return redirect(request.url)
    
    # Retrieve the uploaded file from the form
    file = request.files['resume']
    
    # If the user hasn't selected a file (filename is empty), redirect back to the form
    if file.filename == '':
        return redirect(request.url)
    
    # Save the file
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(pdf_path)
    
    #get skills 
    resume_skills_extractor.extract_text_from_pdf(pdf_path)
    skills_found = resume_skills_extractor.outputSkillsExtracted(5)
    session['resume_uploaded'] = True

    return render_template('edit_resume.html', skills=skills_found)

# Edit resume skills page
@app.route('/add_skills', methods=['POST'])
def add_skills():
    # Get the list of skills from the form
    skills = request.form.getlist('skills')
    return render_template('edit_resume.html', skills=skills)

# Update and submit skills 
@app.route('/update_skills', methods=['POST'])
def update_skills():
    # Update the session with the list of skills submitted by the user from the form
    session['userSkills'] = request.form.getlist('skills')
    session['resume_uploaded'] = True
    
    # Remove uploaded resume artifacts without deleting stored application submissions
    clear_uploaded_resume_files()
    return redirect(url_for('Job_roles'))

if __name__ == '__main__':
    app.run(debug=True)
