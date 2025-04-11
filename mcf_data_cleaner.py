import pandas as pd
import re
import spacy

# Load the CSV
file_path = "mcf_Scraped.csv"
df = pd.read_csv(file_path)

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Strip whitespace from all string columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Pure NLP cleaner using noun chunks (no hardcoded filters)
def extract_noun_chunk_job_title(text):
    doc = nlp(text)
    noun_chunks = [chunk.text.strip() for chunk in doc.noun_chunks if 2 <= len(chunk.text.split()) <= 6]
    
    # Return longest meaningful chunk
    if noun_chunks:
        return max(noun_chunks, key=len)
    
    # Fallback to top 5 words with NOUN/PROPN/ADJ tags
    tokens = [token.text for token in doc if token.pos_ in {"NOUN", "PROPN", "ADJ"}]
    return ' '.join(tokens[:5]) if tokens else text.strip()

# Apply to job titles
df['Cleaned Job Title (SpaCy SM)'] = df['Job Title'].astype(str).apply(extract_noun_chunk_job_title)


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
