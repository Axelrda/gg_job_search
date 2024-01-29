import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

from jobsearch.cleaning import drop_columns, perform_data_casting
from jobsearch.utils import fetch_table_data
from jobsearch.params import DB_PATH, LANG_CLASSIF_MODEL

def load_and_clean_data(db_path):
    data = fetch_table_data(db_path)
    df = data.copy()
    df = drop_columns(df)
    df = perform_data_casting(df)
    return df

def sample_descriptions(df, sample_size=250):
    return df.description.to_list()

def tokenize_descriptions(descriptions, model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer(descriptions,
                     truncation=True,
                     padding=True,
                     max_length=512,
                     return_tensors="pt")

class PyTorchEncodedDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items() if key in ['input_ids', 'attention_mask']}

    def __len__(self):
        return len(self.encodings.input_ids)

def create_data_loader(inputs, batch_size=50):
    torch_descriptions = PyTorchEncodedDataset(inputs)
    return DataLoader(torch_descriptions, batch_size=batch_size)

def perform_inference(dataloader, device, model_name):
    lg_classifier = AutoModelForSequenceClassification.from_pretrained(model_name)
    lg_classifier.to(device)

    logit_list = []
    with torch.no_grad():
        for batch in tqdm(dataloader):
            batch = {k: v.to(device) for k, v in batch.items()}
            logits = lg_classifier(**batch).logits
            logit_list.append(logits)
    return logit_list

def post_processing(logit_list, model_name):
    id_list = [line.argmax().item() for batch in logit_list for line in batch]
    id_col = pd.Series(id_list)
    lg_classifier = AutoModelForSequenceClassification.from_pretrained(model_name)
    lang_labels = id_col.map(lg_classifier.config.id2label)
    lang_labels.rename('lang_labels', inplace=True)
    return lang_labels

def export_results(lang_labels, output_path):
    lang_labels.to_csv(output_path, mode='a', index=False, header=False)

if __name__ == "__main__":
    df = load_and_clean_data(DB_PATH)
    descriptions = sample_descriptions(df)
    inputs = tokenize_descriptions(descriptions, LANG_CLASSIF_MODEL)
    dataloader = create_data_loader(inputs)
    device = torch.device('cpu')  # Change to 'cuda' if GPU is available
    logit_list = perform_inference(dataloader, device, LANG_CLASSIF_MODEL)
    lang_labels = post_processing(logit_list, LANG_CLASSIF_MODEL)
    print(lang_labels.value_counts())
    export_path = '/content/drive/MyDrive/github/gg_job_search/data/lang_labels.csv'
    export_results(lang_labels, export_path)
