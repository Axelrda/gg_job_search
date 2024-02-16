import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

import os


def tokenize_descriptions(descriptions, model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    inputs = tokenizer(descriptions,
                       truncation=True,
                       padding=True,
                       max_length=512,
                       return_tensors="pt")
    return inputs

class PyTorchEncodedDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: val[idx] for key, val in self.encodings.items() if key in ['input_ids', 'attention_mask']}

    def __len__(self):
        return self.encodings.input_ids.shape[0]  # Adjusted for tensor shape

def create_data_loader(inputs, batch_size=16):
    dataset = PyTorchEncodedDataset(inputs)
    return DataLoader(dataset, batch_size=batch_size)

def setup_model_and_device(model_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.to(device)
    return model, device

def run_inference(model, dataloader, device):
    model.eval()  # Set model to evaluation mode
    logit_list = []
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Processing batches"):
            batch = {k: v.to(device) for k, v in batch.items()}
            logits = model(**batch).logits
            logit_list.append(logits.cpu())
    return logit_list

def post_process_logits(logit_list, model):
    id_list = [logit.argmax().item() for logits in logit_list for logit in logits]
    id_col = pd.Series(id_list)
    lang_labels = id_col.map(model.config.id2label)
    lang_labels.rename('lang_labels', inplace=True)
    return lang_labels

def detect_language(model_path:str, df:pd.DataFrame, column: str = "description"):   
    descriptions = df[column].to_list()
    inputs = tokenize_descriptions(descriptions, model_path)
    dataloader = create_data_loader(inputs, 16)
    model, device = setup_model_and_device(model_path)
    logit_list = run_inference(model, dataloader, device)
    lang_labels = post_process_logits(logit_list, model)
    return lang_labels
