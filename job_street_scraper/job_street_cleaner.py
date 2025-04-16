import pandas as pd
import spacy
import yake


pd.set_option("display.max_columns", 5)


def df_replace(old , new):
    df["Job Sub Industry"] = df["Job Sub Industry"].replace(old,new)

    df.to_csv(file_path, index=False)



# Load the CSV
file_path = "job_street_scrape.csv"
#df = pd.read_csv(file_path, encoding="utf-8", low_memory=False)
df = pd.read_csv(file_path, encoding="utf-8")



for col in df.columns:
    unique_types = df[col].map(type).nunique()
    if unique_types > 1:
        print(f"Column '{col}' has mixed types")

print("======================")
print(df["Job Salary Range"].map(type).value_counts())
print(df["Job Posting Date"].map(type).value_counts())


# bad_rows = df[~df["Job Posting Date"].map(type).isin([str])]
# print(bad_rows[["Job Id", "Job Posting Date"]])


"""

#NAME?


"""

# print("=============================")
# print(df.loc[df["Job Sub Industry"] == "Specialists", ["Job Id", "Job Title", "Job Sub Industry"]])
#
#
#
# df_replace("Specialists", "Medical Specialists")
#





filtered = df[df["Job Industry"] == "(Healthcare & Medical)"]
unique_sub_industries = filtered["Job Sub Industry"].dropna().unique()

print("Unique Sub Industries:")
for sub in unique_sub_industries:
    print("-", sub)



# id_counts = df["Job Id"].value_counts()
# duplicates_only = id_counts[id_counts > 1]
# print(duplicates_only)

#
# df_cleaned = df.drop_duplicates(subset="Job Id", keep="first")
#
# df_cleaned.to_csv(file_path, index=False)
#






# Load spaCy NLP model
#nlp = spacy.load("en_core_web_sm")

# # Strip whitespace from all string columns
# df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
#
# # Initialize YAKE extractor
# kw_extractor = yake.KeywordExtractor(lan="en", n=5, top=1)





