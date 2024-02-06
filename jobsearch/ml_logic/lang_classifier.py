import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

from jobsearch.params import DB_PATH, LANG_CLASSIF_MODEL


def tokenize(text_corpus, model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer(text_corpus,
                     truncation=True,
                     padding=True,
                     max_length=512,
                     return_tensors="pt")
    
def tokenize_corpus_with_progress_bar(corpus, tokenizer, tokenizer_args):
  # apply the tokenizer to each element of the corpus with a progress bar
  inputs = [tokenizer(d, **tokenizer_args) for d in tqdm(corpus, total=len(corpus), unit=" elements", desc="Tokenizing")]
  return inputs

tokenizer_args = {"truncation": True, "padding": True, "max_length": 512, "return_tensors": "pt"}

class PyTorchEncodedDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items() if key in ['input_ids', 'attention_mask']}

    def __len__(self):
        return len(self.encodings.input_ids)

def create_pytorch_dataloader(inputs, batch_size=50):
    torch_descriptions = PyTorchEncodedDataset(inputs)
    return DataLoader(torch_descriptions, batch_size=batch_size)

def load_classifier(device, model_name):
    classifier = AutoModelForSequenceClassification.from_pretrained(model_name)
    classifier.to(device)
    return classifier

def infer_from_dataloader_batches(model, dataloader):
    logit_list = []
    with torch.no_grad():
        for batch in tqdm(dataloader):
            batch = {k: v.to(device) for k, v in batch.items()}
            logits = model(**batch).logits
            logit_list.append(logits)
    return logit_list

def post_process_logit_list(logit_list, model_name):
    id_list = [line.argmax().item() for batch in logit_list for line in batch]
    id_col = pd.Series(id_list)

    classifier = load_classifier(device, model_name)
    labels = id_col.map(classifier.config.id2label)
    labels.rename('lang_labels', inplace=True)
    return labels

if __name__ == "__main__":
    # df = load_and_clean_data(DB_PATH)
    # descriptions = sample_descriptions(df)
    # inputs = tokenize_descriptions(descriptions, LANG_CLASSIF_MODEL)
    # dataloader = create_data_loader(inputs)
    # device = torch.device('cpu')  # Change to 'cuda' if GPU is available
    # logit_list = perform_inference(dataloader, device, LANG_CLASSIF_MODEL)
    # lang_labels = post_processing(logit_list, LANG_CLASSIF_MODEL)
    # print(lang_labels.value_counts())
    # export_path = '/content/drive/MyDrive/github/gg_job_search/data/lang_labels.csv'
    # export_results(lang_labels, export_path)
