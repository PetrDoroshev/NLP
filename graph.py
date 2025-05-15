import json
import stanza
from text_preprocessing import clean_text

pipe = stanza.Pipeline(lang='ru', processors='tokenize, pos, lemma, coref, depparse')


def resolve_coreference(doc, word):

    if len(word.coref_chains) <= 0:
        return None

    coref_chain = word.coref_chains[0]

    if not coref_chain.is_representative:

        chain = coref_chain.chain

        end_word = chain.mentions[chain.representative_index].end_word
        sentence_num = chain.mentions[chain.representative_index].sentence
        start_word = chain.mentions[chain.representative_index].start_word

        sentence = doc.sentences[sentence_num]

        for word_index in range(start_word, end_word):

            if sentence.words[word_index].pos == "NOUN":

                return doc.sentences[sentence_num].words[word_index].lemma

    return None


def extract_triplets(paragraph):

    if not paragraph:
        return []

    triplets = []

    doc = pipe(paragraph)
    for sent in doc.sentences:

        res_d = dict()

        for word in sent.words:

            coref = resolve_coreference(doc, word)
            if coref:
                word_lemma = coref
            else:
                word_lemma = word.lemma

            head = sent.words[word.head - 1].lemma

            object_ = None
            nmod_1 = None
            nmod_2 = None

            if word.deprel in ["nsubj", "nsubj:pass"]:

                res_d[word_lemma] = {"head": head }

                for k_0 in sent.words:

                    if (k_0.deprel in ["obj", "obl"]) & (k_0.head == word.head) & (k_0.id > word.head):
                        res_d[word_lemma]["obj"] = k_0.lemma
                        object_ = k_0

                for k_1 in sent.words:
                    if (k_1.head == word.head) & (k_1 == "не"):
                        res_d[word_lemma]["head"] = "не " + res_d[word_lemma]["head"]

                if "obj" in res_d[word_lemma].keys():

                    for k_4 in sent.words:
                        if (k_4.deprel == "nmod") & (k_4.head == object_.id):
                            nmod_1 = k_4
                            break

                    if nmod_1:
                        for k_5 in sent.words:
                            if (k_5.deprel == "nummod") & (k_5.head == nmod_1.id):
                                nmod_2 = k_5
                                break

                    if nmod_2:
                        res_d[word_lemma]["obj"] = res_d[word_lemma]["obj"] + " " + nmod_2.lemma
                    if nmod_1:
                        res_d[word_lemma]["obj"] = res_d[word_lemma]["obj"] + " " + nmod_1.lemma

        if len(res_d) > 0:
            triplets.append([sent.text, res_d])

    clear_triplets = dict()
    for tr in triplets:
        for word in tr[1].keys():
            if "obj" in tr[1][word].keys():
                if not (tr[0] in clear_triplets): clear_triplets[tr[0]] = []
                clear_triplets[tr[0]].append([word, tr[1][word]['head'], tr[1][word]['obj']])

    return clear_triplets

with open('./preprocessing_data/Параграфы_с_рисунками/Диссертация Липилин АС_figures_paragraphs.json', encoding="utf-8") as json_file:
    data = json.load(json_file)

    for p in data["paragraphs"]:

        triplets = extract_triplets(p)
        if triplets: print(f"{triplets},")
