import pandas as pd
import re
import spacy

# Load models
nlp = spacy.load("en_core_web_sm")

# Load the CSV
file_path = "mcf_Scraped.csv"
df = pd.read_csv(file_path)

#Strip whitespace from all string columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

#Convert 'Job Posting Date' to datetime format
df['Job Posting Date'] = pd.to_datetime(
    df['Job Posting Date'].str.replace('Posted ', '', regex=False),
    errors='coerce'
)

# Split and format 'Job Salary Range' into 'Min Salary' and 'Max Salary' with $ and comma
df[['Min Salary', 'Max Salary']] = (
    df['Job Salary Range']
    .str.replace(r'[\$,]', '', regex=True)
    .str.split('to', expand=True)
    .applymap(lambda x: f"${float(x):,.0f}" if pd.notna(x) and x.strip() else "")
)

# Drop the original unformatted salary column
df.drop(columns=['Job Salary Range'], inplace=True)

# Extract numeric years from 'Job Minimum Experience', default to 0 if missing
df['Job Minimum Experience'] = (
    df['Job Minimum Experience']
    .str.extract(r'(\d+)')        # Extract digits
    .fillna(0)                    # Replace NaN with 0
    .astype(int)                 # Convert to integer (no decimals)
)

#Convert 'skills' from newline-separated string to string list
df['skills'] = df['skills'].str.split('\n')
df['skills'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

#Drop duplicates
df = df.drop_duplicates()
df = df.drop_duplicates(subset=['Job Id'])

#Save cleaned DataFrame
df.to_csv("mcf_Scraped_cleaned.csv", index=False)
