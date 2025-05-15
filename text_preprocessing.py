import re
from natasha import MorphVocab
from razdel import sentenize, tokenize
import nltk
from nltk.corpus import stopwords


def clean_text(text):

    #cleaned_text = re.sub(r'\([^)]*\)', '', text)
    cleaned_text = re.sub('[^а-яА-Я0-9ё\s]', '', text)
    cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
    cleaned_text = re.sub(r"\d+", "", cleaned_text)
    cleaned_text = re.sub(r'[a-zA-Z0-9\'_-]+', '', cleaned_text)
    cleaned_text = re.sub('\s+', ' ', cleaned_text)

    return cleaned_text.lower()

def get_tokens(text, check_stopwords=True):

    tokens = []
    text = clean_text(text)
    stop_words = stopwords.words("russian") # стоп-слова

    for token in tokenize(text):
        if check_stopwords:
            if token not in stop_words:
                tokens.append(token.text)
        else:
            tokens.append(token.text)

    return tokens


def get_lemmas(tokens, morph, morph_vocab, save_tags=False):
    lemmas = []
    markup = next(morph.map([tokens]))

    for token in markup.tokens:
        if save_tags:
            lemmas.append(morph_vocab.lemmatize(token.text, token.pos, token.feats) + f"_{token.pos}")
        else:
             lemmas.append(morph_vocab.lemmatize(token.text, token.pos, token.feats))
    return lemmas

