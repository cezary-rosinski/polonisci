import re
import spacy

def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    nlp = spacy.load("pl_core_news_sm")
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return ' '.join(tokens)

def split_text(text, max_length=100):
    words = text.split()
    return [' '.join(words[i:i + max_length]) for i in range(0, len(words), max_length)]
