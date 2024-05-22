import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from bertopic.backend import BaseEmbedder
from umap import UMAP
import spacy
import re
import nltk
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer


def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    nlp = spacy.load("pl_core_news_sm")
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return ' '.join(tokens)

def split_text(text, max_length=100):
    words = text.split()
    return [' '.join(words[i:i + max_length]) for i in range(0, len(words), max_length)]

# texts = texts[:100]

processed_texts = [preprocess_text(text) for text in tqdm(texts)]
split_texts = []
for text in processed_texts:
    split_texts.extend(split_text(text))
split_texts = [text for text in split_texts if text.strip() != '']

if len(split_texts) < 2:
    raise ValueError("Niewystarczająca liczba tekstów po przetwarzaniu wstępnym. Dodaj więcej danych wejściowych.")

polish_stopwords = [
    'i', 'oraz', 'a', 'ale', 'w', 'na', 'z', 'do', 'się', 'o', 'że', 'to', 'co', 'nie', 'jest', 'jak', 'tak', 'czy',
    'być', 'by', 'dla', 'czyli', 'ten', 'ona', 'on', 'my', 'oni', 'jeśli', 'gdy', 'za', 'tylko', 'po', 'przez', 'pod',
    'bez', 'nad', 'jeszcze', 'już', 'też', 'tam', 'tu', 'u', 'od', 'ze', 'jestem', 'są', 'jesteśmy', 'jesteś', 'was',
    'czyż', 'albo', 'mnie', 'tobie', 'tobą', 'wam', 'może', 'muszę', 'mogę', 'będzie', 'będą', 'był', 'była', 'było',
    'byli', 'były', 'mam', 'masz', 'mamy', 'macie', 'ich', 'je', 'jemu', 'jej', 'jego', 'ich', 'imię', 'im'
]

sentence_model = SentenceTransformer("allegro/herbert-base-cased")

class PolishEmbedder(BaseEmbedder):
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def embed(self, documents, verbose=False):
        return self.embedding_model.encode(documents, show_progress_bar=verbose)

polish_embedder = PolishEmbedder(sentence_model)
vectorizer_model = CountVectorizer(stop_words=polish_stopwords, ngram_range=(1, 3))
umap_model = UMAP(n_neighbors=10, n_components=5, min_dist=0.1, metric='cosine')

topic_model = BERTopic(
    embedding_model=polish_embedder,
    vectorizer_model=vectorizer_model,
    umap_model=umap_model,
    top_n_words=10,
    n_gram_range=(1, 3),
    min_topic_size=10,
    calculate_probabilities=True
)

try:
    topics, probabilities = topic_model.fit_transform(split_texts)
except ValueError as e:
    print(f"Error during model fitting: {e}")
    print("Texts:", split_texts)
    raise

print(topic_model.get_topic_info())
topic_info = topic_model.get_topic_info()
topic_info.to_csv("topics_info.csv", index=False)
