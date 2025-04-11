import pandas as pd
import re
import spacy
import yake

# Load the CSV
file_path = "mcf_Scraped.csv"
df = pd.read_csv(file_path)

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Strip whitespace from all string columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Initialize YAKE extractor
kw_extractor = yake.KeywordExtractor(lan="en", n=2, top=1)

# Combined method: spaCy noun chunk first, YAKE fallback
def combined_spacy_yake_cleaner(text):
    if not isinstance(text, str) or not text.strip():
        return ""

    doc = nlp(text)

    # Step 1: Try spaCy noun chunks
    for chunk in doc.noun_chunks:
        if 2 <= len(chunk.text.strip().split()) <= 6:
            return chunk.text.strip()

    # Step 2: Fallback to YAKE
    keywords = kw_extractor.extract_keywords(text)
    if keywords:
        return keywords[0][0].strip()

    # Final fallback
    return text.strip()

# Apply to DataFrame
df['Cleaned Job Title (spaCy + YAKE)'] = df['Job Title'].astype(str).apply(combined_spacy_yake_cleaner)


# Convert 'Job Posting Date' to datetime format
df['Job Posting Date'] = pd.to_datetime(
    df['Job Posting Date'].str.replace('Posted ', '', regex=False),
    errors='coerce'
)

# Split and format 'Job Salary Range' into 'Min Salary' and 'Max Salary'
df[['Min Salary', 'Max Salary']] = (
    df['Job Salary Range']
    .str.replace(r'[\$,]', '', regex=True)
    .str.split('to', expand=True)
    .applymap(lambda x: f"${float(x):,.0f}" if pd.notna(x) and x.strip() else "")
)

# Drop the original unformatted salary column
df.drop(columns=['Job Salary Range'], inplace=True)

# Extract numeric years from 'Job Minimum Experience'
df['Job Minimum Experience'] = (
    df['Job Minimum Experience']
    .str.extract(r'(\d+)')
    .fillna(0)
    .astype(int)
)

# Convert 'skills' from newline-separated string to comma-separated string
df['skills'] = df['skills'].str.split('\n').apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

# Drop duplicates and ensure unique job entries
df = df.drop_duplicates()
df = df.drop_duplicates(subset=['Job Id'])

# Save the cleaned dataset
df.to_csv("mcf_Scraped_cleaned_final.csv", index=False)
