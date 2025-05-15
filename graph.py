import json
import stanza
from text_preprocessing import clean_text

syntax_pipe = stanza.Pipeline(lang='ru', processors='tokenize, pos, lemma, coref, depparse')


def resolve_coreference(doc, word):

    if len(word.coref_chains) <= 0:
        return None

    coref_chain = word.coref_chains[0]

    if not coref_chain.is_representative:

        chain = coref_chain.chain

        end_word = chain.mentions[chain.representative_index].end_word
        sentence_num = chain.mentions[chain.representative_index].sentence
        start_word = chain.mentions[chain.representative_index].start_word

        return doc.sentences[sentence_num].words[start_word].lemma

    return None


def extract_triplets(sentence):

    if not sentence:
        return []

    triplets = []

    doc = syntax_pipe(sentence)
    for sent in doc.sentences:


        res_d = dict()
        temp_d = dict()

        for word in sent.words:
            temp_d[word.lemma] = {"head": sent.words[word.head - 1].lemma, "dep": word.deprel, "id": word.id}
            c = word.coref_chains
            if len(c) > 0:
                s = resolve_coreference(doc, word)

        for word in temp_d.keys():
            nmod_1 = ""
            nmod_2 = ""
            if temp_d[word]["dep"] in ["nsubj", "nsubj:pass"]:
                res_d[word] = {"head": temp_d[word]["head"]}
                r = resolve_coreference(doc, sent.words[temp_d[word]["id"] - 1])
                if r:
                    print()

                for k_0 in temp_d.keys():
                    if (temp_d[k_0]["dep"] in ["obj", "obl"]) & \
                            (temp_d[k_0]["head"] == res_d[word]["head"]) & \
                            (temp_d[k_0]["id"] > temp_d[res_d[word]["head"]]["id"]):
                        res_d[word]["obj"] = k_0
                        r = resolve_coreference(doc, sent.words[temp_d[k_0]["id"] - 1])
                        if r:
                            print()
                        break

                for k_1 in temp_d.keys():
                    if (temp_d[k_1]["head"] == res_d[word]["head"]) & (k_1 == "не"):
                        res_d[word]["head"] = "не " + res_d[word]["head"]

                if "obj" in res_d[word].keys():
                    for k_4 in temp_d.keys():
                        if (temp_d[k_4]["dep"] == "nmod") & \
                                (temp_d[k_4]["head"] == res_d[word]["obj"]):
                            nmod_1 = k_4
                            break

                    for k_5 in temp_d.keys():
                        if (temp_d[k_5]["dep"] == "nummod") & \
                                (temp_d[k_5]["head"] == nmod_1):
                            nmod_2 = k_5
                            break

                    if nmod_2:
                        res_d[word]["obj"] = res_d[word]["obj"] + " " + nmod_2
                    if nmod_1:
                        res_d[word]["obj"] = res_d[word]["obj"] + " " + nmod_1

        if len(res_d) > 0:
            triplets.append([sent.text, res_d])

    clear_triplets = dict()
    for tr in triplets:
        for word in tr[1].keys():
            if "obj" in tr[1][word].keys():
                clear_triplets[tr[0]] = [word, tr[1][word]['head'], tr[1][word]['obj']]

    return clear_triplets

with open('./preprocessing_data/Параграфы_с_рисунками/Диссертация Липилин АС_figures_paragraphs.json', encoding="utf-8") as json_file:
    data = json.load(json_file)

    for p in ["При этом электролит имеет структуру плотной керамики, а электроды имеют требуемую пористую структуру с открытой пористостью 46-49% (рис. 128г)."]:

        triplets = extract_triplets(p)
        if triplets: print(f"{triplets},")
