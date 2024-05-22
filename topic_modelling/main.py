import pandas as pd
from tqdm import tqdm
import preprocess
import models
import pickle
from datasets import Dataset

def load_data(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    data_list = [{"id": key, "full_text": value["full text"]} for key, value in data.items()]
    dataset = Dataset.from_dict({"id": [item["id"] for item in data_list], "full_text": [item["full_text"] for item in data_list]})
    texts = dataset["full_text"]
    ids = dataset["id"]
    return texts, ids

def main():
    file_path = '/content/drive/MyDrive/Granty, współpraca naukowa/polonisci/full/polonisci_text_abstract.pickle'
    texts, ids = load_data(file_path)

    processed_texts = [preprocess.preprocess_text(text) for text in tqdm(texts)]
    split_texts = []
    for text in processed_texts:
        split_texts.extend(preprocess.split_text(text))
    split_texts = [text for text in split_texts if text.strip() != '']

    if len(split_texts) < 2:
        raise ValueError("Niewystarczająca liczba tekstów po przetwarzaniu wstępnym. Dodaj więcej danych wejściowych.")

    topic_model = models.create_topic_model()

    try:
        topics, probabilities = topic_model.fit_transform(split_texts)
    except ValueError as e:
        print(f"Error during model fitting: {e}")
        print("Texts:", split_texts)
        raise

    print(topic_model.get_topic_info())
    topic_info = topic_model.get_topic_info()
    topic_info.to_csv("topics_info.csv", index=False)

if __name__ == "__main__":
    main()
