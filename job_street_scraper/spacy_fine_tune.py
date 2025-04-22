import pandas as pd
import spacy
from spacy.tokens import DocBin
from spacy.training.example import Example
import json

# Load your CSV
df = pd.read_csv("../train_data/job_title_data.csv")

#df = pd.read_csv("job_street_cleaned.csv")

midpoint = len(df) // 2

df_train = df.iloc[:midpoint]
df_dev = df.iloc[midpoint:]

# Save them as separate CSV files
df_train.to_csv("job_title_train.csv", index=False)
df_dev.to_csv("job_title_dev.csv", index=False)

#
# nlp = spacy.load("en_core_web_sm")  # load base model
# ner = nlp.get_pipe("ner")
#
# # Add new labels
# ner.add_label("ROLE")
#
# train_data = []
#
# for _, row in df.iterrows():
#     raw = str(row["Raw Job Title"])
#     role = str(row["Cleaned Role"])
#
#     if role in raw:
#         start = raw.index(role)
#         end = start + len(role)
#         train_data.append((raw, {"entities": [(start, end, "ROLE")]}))
#
# with open("train_data.json", "w") as f:
#     json.dump(train_data, f)
#

