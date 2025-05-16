import nltk
import os
import json
import natasha

from navec import Navec
from slovnet import Morph
from natasha import MorphVocab
from razdel import sentenize, tokenize
from nltk.corpus import stopwords

nltk.download("stopwords")

def mod_model_creation(norm_parag_path, tokens_folder, lemmas_folder, morph_navec):
    all_raw_articles = sorted(os.listdir(norm_parag_path))

    morph_vocab = MorphVocab()
    navec = Navec.load(morph_navec['navec'])
    morph = Morph.load(morph_navec['morph'], batch_size=4)
    morph.navec(navec)

    for now_raw_article in all_raw_articles:
        print(f"Processing: {now_raw_article}")
        # if 'Якименко' in now_raw_article: continue
        full_file_path = os.path.join(norm_parag_path, now_raw_article)
        article_name = ".".join(now_raw_article.split(".")[:-1])

        clean_paragraphs = load_dict_from_json(full_file_path)

        tokens_dict = {"tokens": []}
        lemmas_dict = {"lemmas": []}
    
        for p in clean_paragraphs['cleaned_text']:
            paragraph_tokens = []
            paragraph_lemmas = []
    
            for sent in split_paragraph_on_sent(p):
                sentence_tokens = get_tokens(sent)
                sentence_lemmas = get_lemmas(sentence_tokens, morph, morph_vocab)
    
                paragraph_tokens.append(sentence_tokens)
                paragraph_lemmas.append(sentence_lemmas)
    
            tokens_dict["tokens"].append(paragraph_tokens)
            lemmas_dict["lemmas"].append(paragraph_lemmas)

        save_dict_as_json(f"{tokens_folder}/{article_name}_tokenized.json", tokens_dict)
        save_dict_as_json(f"{lemmas_folder}/{article_name}_lemmatized.json", lemmas_dict)
    print("Completed!")

def get_tokens(text, check_stopwords=True):
    tokens = []
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

def split_paragraph_on_sent(paragraph):
    sentences = []
    for sent in sentenize(paragraph):
        sentences.append(sent.text)
    return sentences

def save_dict_as_json(path, dictionary):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=4)

def load_dict_from_json(path):
    with open(path, 'r', encoding='utf-8') as json_file:
        dictionary = json.load(json_file)
    return dictionary