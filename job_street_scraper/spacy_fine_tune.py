import pandas as pd
import spacy
from spacy.tokens import DocBin
from spacy.training.example import Example
from spacy.cli.train import train
import json

# Load your CSV
#df = pd.read_csv("job_title_dev.csv")

df = pd.read_csv("job_title_trainv3.csv")

#df = pd.read_csv("job_street_cleaned.csv")

#df.iloc[::10].to_csv("job_title_train2.csv", index=False)



#
# nlp = spacy.load("en_core_web_sm")  # load base model
#nlp = spacy.load("output/model-best")  # load trained model


def clr_special_name(df):
    df["Job Title"] = df["Job Title"].astype(str).str.strip().str.lower()
    df["Job Title"] = df["Job Title"].replace({"#name?": pd.NA})
    df = df.dropna(subset=["Job Title"])

    print(df)
    df.to_csv("job_title_trainv3.csv", index=False)

clr_special_name(df)

def extract_entities(text):
    doc = nlp(text)

    return ", ".join(ent.text for ent in doc.ents)

#df["Job Title Clean 2"] = df["Job Title"].apply(extract_entities)


#df.to_csv("clean_check.csv", index=False)




# ner = nlp.get_pipe("ner")
#
# # Add new labels
# ner.add_label("ROLE")
def gen_train_data_spacy(csv_path, output_path):
    nlp = spacy.load("en_core_web_sm")  # use pretrained model
    doc_bin = DocBin()

    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        raw_text = str(row["Job Title"])
        clean_role = str(row["Job Title Clean"]).strip()

        start = raw_text.lower().find(clean_role.lower())
        if start == -1:
            continue  # skip if clean title is not found in raw

        end = start + len(clean_role)

        doc = nlp.make_doc(raw_text)
        span = doc.char_span(start, end, label="ROLE")
        if span is None:
            continue  # skip malformed spans

        doc.ents = [span]
        doc_bin.add(doc)

    doc_bin.to_disk(output_path)


#gen_train_data_spacy("job_title_train2.csv", "job_title.spacy")


def train_spacy_model():
    train(
        config_path="config.cfg",
        output_path="output",


    )

#train_spacy_model()






