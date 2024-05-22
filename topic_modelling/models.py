from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from bertopic.backend import BaseEmbedder
from umap import UMAP
from sentence_transformers import SentenceTransformer
import config

class PolishEmbedder(BaseEmbedder):
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def embed(self, documents, verbose=False):
        return self.embedding_model.encode(documents, show_progress_bar=verbose)

def create_topic_model():
    sentence_model = SentenceTransformer("allegro/herbert-base-cased")
    polish_embedder = PolishEmbedder(sentence_model)
    vectorizer_model = CountVectorizer(stop_words=config.POLISH_STOPWORDS, ngram_range=(1, 3))
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
    return topic_model
