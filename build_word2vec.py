import os

import gensim
from gensim.models import Word2Vec
from natasha import MorphVocab
from navec import Navec
from slovnet import Morph

from paragraph_processing import get_paragraphs
from paragraph_processing import split_paragraph_on_sent
from text_preprocessing import get_lemmas, get_tokens

def prepare_data():

    sentences = []
    morph_vocab = MorphVocab()
    navec = Navec.load('./models/navec_news_v1_1B_250K_300d_100q.tar')
    morph = Morph.load('./models/slovnet_morph_news_v1.tar', batch_size=4)
    morph.navec(navec)

    for i in range(len(os.listdir("./Articles")) - 1):
        filename = os.path.join("./Articles", sorted(os.listdir("./Articles"))[i])
        article_name = filename.split("/")[-1].split(".")[0]
        print(article_name)
        paragraphs = get_paragraphs(filename)
        for p in paragraphs:

            for sent in split_paragraph_on_sent(p):

                tokens = get_tokens(sent)
                lemmas = get_lemmas(tokens, morph, morph_vocab, save_tags=False)

                if len(lemmas) > 5:

                    lemmas_sent = ' '.join(lemmas)
                    if lemmas_sent:
                        sentences.append(lemmas_sent)

    with open("train_text.txt", "w", encoding="utf-8") as f:
        f.write('\n'.join(sentences))


if not os.path.exists("./train_text.txt"):
    prepare_data()

f = './train_text.txt'
data = gensim.models.word2vec.LineSentence(f)

model = Word2Vec(data, vector_size=300, window=10, min_count=2, sg=1)
print(len(model.wv))
model.save("./models/word2vec.model")

