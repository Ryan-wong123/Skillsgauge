import pandas as pd
import spacy
import yake
import re
import numpy as np

#TODO: settle business #name issue

# setup
pd.set_option("display.max_columns", None)
np.set_printoptions(suppress=True)

# Load the CSV
file_path = "job_street_scrape.csv"
clean_path = "job_street_cleaned.csv"
df = pd.read_csv(file_path, encoding="utf-8")






# data understanding codes


# find unique values of columns


def find_unique_values(df , column):

    unique_values = df[column].unique()
    print(unique_values)




def clean_setup(df):
    # Assume df is your original DataFrame
    df_copy = df.copy()

    # create rows for analysis
    new_columns = {
        "Salary Low": None,
        "Salary High": None,
        "Salary Avg": None
    }

    for col, val in new_columns.items():
        df_copy[col] = val

    all_cols = list(df_copy.columns)
    insert_after = "Job Salary Range"
    insert_pos = all_cols.index(insert_after)

    # Remove new columns from current position
    for col in new_columns:
        all_cols.remove(col)

    for col in reversed(list(new_columns.keys())):
        all_cols.insert(insert_pos + 1, col)

    df_copy = df_copy[all_cols]
    #print(df_copy.head())

    return df_copy



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




def clean_df(df):

    df_copy = clean_setup(df)
    df_copy[["Salary Low", "Salary High", "Salary Avg"]] = df_copy["Job Salary Range"].apply(extract_salary_info)
    #clean_salary(df_copy)

    # for col in df.columns:
    #     unique_types = df[col].map(type).nunique()
    #     if unique_types > 1:
    #         print(f"Column '{col}' has mixed types")
    #
    # print("======================")
    # print(df["Job Salary Range"].map(type).value_counts())
    # print(df["Job Posting Date"].map(type).value_counts())

    #bad_rows = df[~df["Job Salary Range"].map(type).isin([str])]
    #print(bad_rows["Job Salary Range"])



    #df["Job Salary Range"] = df["Job Salary Range"].astype(str)

    find_unique_values(df_copy, "Job Salary Range")
    print("\n\n")
    #find_unique_values(df_copy, "Salary Low")

    #df_copy.to_csv(clean_path)

clean_df(df)











# Load spaCy NLP model
#nlp = spacy.load("en_core_web_sm")

# # Strip whitespace from all string columns
# df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
#
# # Initialize YAKE extractor
# kw_extractor = yake.KeywordExtractor(lan="en", n=5, top=1)





