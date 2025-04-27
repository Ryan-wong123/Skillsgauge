import pandas as pd
import spacy
import yake
import re
import datetime

#TODO: settle business #name issue

# setup
#pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
#np.set_printoptions(suppress=True)

# Load the CSV
file_path = "job_street_scrape.csv"
clean_path = "job_street_cleaned.csv"
df = pd.read_csv(file_path, encoding="utf-8")

nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("output/model-best")
# Initialize YAKE extractor
kw_extractor = yake.KeywordExtractor(lan="en", n=5, top=1)


# data understanding codes


# find unique values of columns


def find_unique_values(df , column):

    unique_values = df[column].value_counts()
    print(unique_values.tail(100))




def clean_setup(df):
    # Assume df is your original DataFrame
    df_copy = df.copy()

    # create new columns for analysis
    new_columns = {
        "Job Title Clean": None,
        "Salary Low": None,
        "Salary High": None,
        "Salary Avg": None
    }

    for col, val in new_columns.items():
        df_copy[col] = val
    #define new column order
    new_order = [
        "Job Id", "Job URL", "Job Title", "Job Title Clean", "Company", "Job Industry",
        "Job Sub Industry", "Job Description", "Job Employment Type", "Job Minimum Experience",
        "Job Salary Range", "Salary Low", "Salary High", "Salary Avg",
        "Skills", "Job Posting Date", "Location"
    ]
    #set order
    df_copy = df_copy[new_order]

    return df_copy


# clean salary portion
def normalize_salary_text(s):
    if pd.isna(s):
        return ""
    s = str(s).lower().strip()
    s = s.replace("â€“", "-").replace("–", "-").replace(",", "").replace("$", "").replace(".", "")
    return s

def extract_number(value):
    # Handle cases like "3k", "4.5k", "3500"
    match = re.match(r"(\d+\.?\d*)\s*(k)?", value.strip())
    if not match:
        return None
    number = float(match.group(1))
    if match.group(2):  # if 'k' is present
        number *= 1000
    return number

def extract_salary_info(salary_str):
    s = normalize_salary_text(salary_str)

    # Determine the salary unit
    if any(k in s for k in ["per month", "p.m", "p.m.", "/month"]):
        unit = "month"
        multiplier = 1
    elif any(k in s for k in ["per hour", "p.h", "/hour"]):
        unit = "hour"
        multiplier = 160  # Approximate 160 hours per month
    elif any(k in s for k in ["per annum", "per year", "p.a", "/year", "annum"]):
        unit = "year"
        multiplier = 1/12
    else:
        unit = "unknown"
        multiplier = 1

    # Extract raw number strings
    raw_numbers = re.findall(r"[\d.]+k?", s)

    # Convert each to actual value
    numbers = [extract_number(n) for n in raw_numbers if extract_number(n) is not None]

    if len(numbers) == 2:
        low = numbers[0] * multiplier
        high = numbers[1] * multiplier
        avg = (low + high) / 2
    elif len(numbers) == 1:
        low = high = avg = numbers[0] * multiplier
    else:
        low = high = avg = None

    return pd.Series([ low, high, avg])




# clean job title portion potentially using trained spacy model
def extract_job_title(text):
    if pd.isna(text):
        return ""
    text = str(text)

    # Remove content after |, $, or digits at the end (salary info, contract, etc.)
    text = re.split(r"\s*\|\s*|\$|\d{3,4}", text)[0]

    # Remove common trailing patterns
    text = re.sub(r'\(.*?\)', '', text)   # remove parentheses
    text = re.sub(r'\s+-.*', '', text)    # remove after " - ..."

    return text.strip()


def jobTitleCleaner(text):
    print("start cleaning job title:" + text)

    if not isinstance(text, str) or not text.strip():
        print("end value: ")
        return ""

    doc = nlp(text)

    # Step 1: Extract noun chunks likely to be job roles
    noun_chunks = [
        chunk.text.strip()
        for chunk in doc.noun_chunks
        if 1 <= len(chunk.text.strip().split()) <= 6  # Avoid long or too short chunks
    ]

    # Step 2: Prefer noun chunks that contain proper nouns or job-like compound nouns
    prioritized = []
    for chunk in noun_chunks:
        tokens = nlp(chunk)
        if any(tok.pos_ in {"PROPN", "NOUN"} for tok in tokens) and not any(tok.pos_ == "VERB" for tok in tokens):
            prioritized.append(chunk)

    if prioritized:
        print("end value: " + prioritized[0].title())
        return prioritized[0].title()

    # Step 3: Fallback to YAKE if no good noun chunks
    keywords = kw_extractor.extract_keywords(text)
    if keywords:
        print("end value2: " + keywords[0][0].title().strip())
        return keywords[0][0].title().strip()

    # Step 4: Final fallback – return cleaned title-cased version
    print("end value3: " + text.title())
    return text.title()


def clean_posting_date(df):
    # convert str to data time format
    df["Job Posting Date"] = pd.to_datetime(df["Job Posting Date"], format="%d/%m/%Y" ,errors='coerce')

    # if NA set today date
    today = pd.Timestamp.today().normalize()
    df["Job Posting Date"] = df["Job Posting Date"].fillna(today)

    return df

def clean_df(df):


    df_copy = clean_setup(df)
    # extract salary values to int values
    df_copy[["Salary Low", "Salary High", "Salary Avg"]] = df_copy["Job Salary Range"].apply(extract_salary_info)
    df_copy["Clean Job Title"] = df_copy["Job Title"].apply(extract_job_title)

    # clean job title
    #df_copy["Job Title Clean"] = df_copy["Job Title"].astype(str).apply(jobTitleCleaner)


    #print("job title clean complete")


    # clean job posting date
    df_copy = clean_posting_date(df_copy)




    #print(df_copy["Job Posting Date"])


    #find_unique_values(df_copy, "Job Title")
    print("\n\n")
    #find_unique_values(df_copy, "Job Title Clean")

    #df_copy.to_csv(clean_path, index=False)

clean_df(df)









