import nltk
import os
import json
import natasha

from navec import Navec
from slovnet import Morph
from natasha import MorphVocab
from razdel import sentenize, tokenize
from nltk.corpus import stopwords

import shared_functions

nltk.download("stopwords")

def mod_model_creation(clean_fragments_path, tokens_folder, lemmas_folder, morph_navec):
    all_clean_fragments = sorted(os.listdir(clean_fragments_path))

    morph_vocab = MorphVocab()
    navec = Navec.load(morph_navec['navec'])
    morph = Morph.load(morph_navec['morph'], batch_size=4)
    morph.navec(navec)

    for now_clean_fragments in all_clean_fragments:
        print(f"Processing: {now_clean_fragments}")
        # if 'Якименко' in now_raw_article: continue
        full_file_path = os.path.join(clean_fragments_path, now_clean_fragments)
        article_name = ".".join(now_clean_fragments.split(".")[:-1])

        clean_paragraphs = shared_functions.load_dict_from_json(full_file_path)

        tokens_dict = {"tokens": []}
        lemmas_dict = {"lemmas": []}
    
        for p_raw in clean_paragraphs['cleaned_text']:
            _, p = shared_functions.split_page_and_metadata(p_raw)
            
            paragraph_tokens = []
            paragraph_lemmas = []
    
            for sent in split_paragraph_on_sent(p):
                sentence_tokens = get_tokens(sent)
                sentence_lemmas = get_lemmas(sentence_tokens, morph, morph_vocab)
    
                paragraph_tokens.append(sentence_tokens)
                paragraph_lemmas.append(sentence_lemmas)
    
            tokens_dict["tokens"].append(paragraph_tokens)
            lemmas_dict["lemmas"].append(paragraph_lemmas)

        shared_functions.save_dict_as_json(f"{tokens_folder}/{article_name}_tokenized.json", tokens_dict)
        shared_functions.save_dict_as_json(f"{lemmas_folder}/{article_name}_lemmatized.json", lemmas_dict)
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