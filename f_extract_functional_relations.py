import json
import stanza
import os

import shared_functions

class Entity:
    def __init__ (self, subject, nmod=None, coref_str=""):

        self.subject = subject
        self.nmod = nmod
        self.coref_str = coref_str

    def __str__(self):

        if self.coref_str:
            return self.coref_str

        if self.nmod:
            return f"{self.subject.lemma} {self.nmod.lemma}"
        else:
            return f"{self.subject.lemma}"

def mod_extract_functional_relations(raw_fragments_path, function_triplets_path, save_old_triplets=True):
    pipe = stanza.Pipeline(lang='ru', processors='tokenize, pos, lemma, coref, depparse')
    all_raw_fragments = sorted(os.listdir(raw_fragments_path))

    if save_old_triplets:
        all_triplets = read_old_triplets(function_triplets_path)
    else:
        all_triplets = []
    
    for now_raw_fragments in all_raw_fragments:
        print(f"\tProcessing: {now_raw_fragments}")
        article_triplest = []
        full_file_path = os.path.join(raw_fragments_path, now_raw_fragments)
        article_name = ".".join(now_raw_fragments.split(".")[:-1])

        fragments = shared_functions.load_dict_from_json(full_file_path)

        for p_id, p_raw in enumerate(fragments['fragments']):
            _, p = shared_functions.split_page_and_metadata(p_raw)
            now_triplets = extract_triplets(pipe, p)
            article_triplest.append( { str(p_id): now_triplets })

        all_triplets.append({ str(article_name): article_triplest })

    triplets = { "triplets": all_triplets }

    shared_functions.save_dict_as_json(function_triplets_path, triplets)

    print(f"Completed!")

def read_old_triplets(triplets_path):
    all_triplets = []

    old_triplets = shared_functions.load_dict_from_json(triplets_path)

    for now_trip in old_triplets["triplets"]:
        for now_art_name in now_trip:
            all_triplets.append( {str(now_art_name): now_trip[now_art_name] })
            
    return all_triplets

def resolve_coreference(doc, word):
    if len(word.coref_chains) <= 0:
        return None

    coref_chain = word.coref_chains[0]

    if not coref_chain.is_representative:

        chain = coref_chain.chain

        end_word = chain.mentions[chain.representative_index].end_word
        sentence_num = chain.mentions[chain.representative_index].sentence
        start_word = chain.mentions[chain.representative_index].start_word

        for i in range(start_word, end_word):

            sent = doc.sentences[sentence_num]
            word = sent.words[i]

            if word.pos == "NOUN":

                word_children_nmod = [w for w in sent.words if w.head == word.id and w.deprel == "nmod"
                                      and w.pos == "NOUN"]

                if word_children_nmod:
                    return f"{word.lemma} {word_children_nmod[0].lemma}"

                return word.lemma

    return None


def get_entities(doc):
    entities = []

    if not doc:
        return []

    for sent in doc.sentences:
        for word in sent.words:
            if word.deprel in ["nsubj", "nsubj:pass"]:
                coref = resolve_coreference(doc, word)

                if coref:
                    entities.append(Entity(word, None, coref))
                else:
                    if word.pos == "NOUN":
                        word_children_nmod = [w for w in sent.words if w.head == word.id and w.deprel == "nmod"
                                              and w.pos == "NOUN"]
                        if word_children_nmod:
                            nmod = word_children_nmod[0]
                            entities.append(Entity(word, nmod))
                        else:
                            entities.append(Entity(word))
    return entities


def extract_triplets(pipeline, paragraph):
    if not paragraph:
        return []

    triplets = []

    doc = pipeline(paragraph)
    entities = get_entities(doc)

    for ent in entities:

        object_ = None
        nmod_1 = None
        nmod_2 = None

        res_d = dict()

        word_lemma = str(ent)
        word = ent.subject
        sent = word.sent

        head = sent.words[ent.subject.head - 1].lemma
        res_d[word_lemma] = {"head": head}

        for k_0 in sent.words:

            if (k_0.deprel in ["obj", "obl"]) & (k_0.head == word.head) & (k_0.pos == "NOUN"):
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
            triplets.append(res_d)

    clear_triplets = []
    for tr in triplets:
        for word in tr.keys():
            if "obj" in tr[word].keys():
                clear_triplets.append([word, tr[word]['head'], tr[word]['obj']])

    return clear_triplets