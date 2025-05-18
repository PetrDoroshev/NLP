import nltk
from navec import Navec
from slovnet import Morph
from paragraph_processing import get_paragraphs, get_figures_paragraphs, split_paragraph_on_sent
from text_preprocessing import *
import text_preprocessing
import natasha
import os
import json
nltk.download("stopwords")

report_path = "preprocessing_data"

def save_dict_as_json(path, dictionary):

    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=4)

morph_vocab = MorphVocab()
navec = Navec.load('models/navec_news_v1_1B_250K_300d_100q.tar')
morph = Morph.load('models/slovnet_morph_news_v1.tar', batch_size=4)
morph.navec(navec)

for i in range(len(os.listdir("./Articles")) - 1):
    filename = os.path.join("./Articles", sorted(os.listdir("./Articles"))[i])
    article_name = filename.split("\\")[-1].split(".")[0]
    print(article_name)

    paragraphs = get_paragraphs(filename)

    report_dict = {"paragraphs": paragraphs}
    save_dict_as_json(f"{report_path}/Параграфы/{article_name}_paragraphs.json", report_dict)

    paragraphs = get_figures_paragraphs(get_paragraphs(filename))
    report_dict = {"paragraphs": paragraphs}
    save_dict_as_json(f"{report_path}/Параграфы_с_рисунками/{article_name}_figures_paragraphs.json", report_dict)


    cleaned_paragraphs =  [clean_text(p) for p in paragraphs]
    report_dict = {"cleaned_text": cleaned_paragraphs}
    save_dict_as_json(f"{report_path}/Очистка_текста/{article_name}_cleaned.json", report_dict)


    report_dict = {"tokens": []}
    report_dict_2 = {"lemmas": []}


    for p in paragraphs:

        paragraph_tokens = []
        paragraph_lemmas = []

        for sent in split_paragraph_on_sent(p):

            sentence_tokens = get_tokens(sent)
            sentence_lemmas = get_lemmas(sentence_tokens, morph, morph_vocab)

            paragraph_tokens.append(sentence_tokens)
            paragraph_lemmas.append(sentence_lemmas)


        report_dict["tokens"].append(paragraph_tokens)
        report_dict_2["lemmas"].append(paragraph_lemmas)

    save_dict_as_json(f"{report_path}/Токенизация/{article_name}_tokenized.json", report_dict)
    save_dict_as_json(f"{report_path}/Лемматизация/{article_name}_lemmatized.json", report_dict_2)

