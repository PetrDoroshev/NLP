import os

import gensim
from gensim.models import Word2Vec
from natasha import MorphVocab
from navec import Navec
from slovnet import Morph

import shared_functions
import d_models_creation

def mod_build_word2vec(raw_fragments_path, result_model_path, all_combined_text_path, morph_navec):
    all_raw_fragments = sorted(os.listdir(raw_fragments_path))

    morph_vocab = MorphVocab()
    navec = Navec.load(morph_navec['navec'])
    morph = Morph.load(morph_navec['morph'], batch_size=4)
    morph.navec(navec)

    sentences = []
    
    for now_raw_fragment in all_raw_fragments:
        print(f"\tProcessing: {now_raw_fragment}")
        full_file_path = os.path.join(raw_fragments_path, now_raw_fragment)
        article_name = ".".join(now_raw_fragment.split(".")[:-1])

        fragments = shared_functions.load_dict_from_json(full_file_path)
        
        for p_raw in fragments['cleaned_text']:
            _, p = shared_functions.split_page_and_metadata(p_raw)
            for sent in d_models_creation.split_paragraph_on_sent(p):
                tokens = d_models_creation.get_tokens(sent)
                lemmas = d_models_creation.get_lemmas(tokens, morph, morph_vocab, save_tags=False)

                if len(lemmas) > 5:
                    lemmas_sent = ' '.join(lemmas)
                    if lemmas_sent:
                        sentences.append(lemmas_sent)

    with open(all_combined_text_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(sentences))
        
    data = gensim.models.word2vec.LineSentence(all_combined_text_path)
    
    model = Word2Vec(data, vector_size=300, window=10, min_count=2, sg=1)
    model.save(result_model_path)
    print(f"Completed! Len of model: {len(model.wv)}")    