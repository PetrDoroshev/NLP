import os
import psycopg2

import scripts_shared_functions

def mod_d_init_preprocessing_results(pg_data, tokens_path, lemmas_path, table_name):
    all_tokens = sorted(os.listdir(tokens_path))
    all_lemmas = sorted(os.listdir(lemmas_path))

    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    for now_token in all_tokens:
        full_file_path = os.path.join(tokens_path, now_token)
        article_name = str(".".join(now_token.split(".")[:-1])).replace("_paragraphs_fragments_cleaned_tokenized", "")

        cur.execute(f"SELECT id FROM articles WHERE title = %s", (article_name,))
        art_id = cur.fetchone()[0]

        all_tok = scripts_shared_functions.load_dict_from_json(full_file_path)["tokens"]

        cur.execute(f"SELECT id FROM fragments WHERE article_id = %s", (art_id,))
        frag_ids = cur.fetchall()
        frag_ids = sorted(frag_ids)
        last_id = 0
        
        for now_tok in all_tok:
            try:
                content = " ".join(now_tok[0])
            except:
                content = ""
            cur.execute(f"INSERT INTO {table_name} (fragment_id, step, processed_text) VALUES (%s, %s, %s)", (frag_ids[last_id], "Token", content))
            last_id += 1

    for now_lemma in all_lemmas:
        full_file_path = os.path.join(lemmas_path, now_lemma)
        article_name = str(".".join(now_lemma.split(".")[:-1])).replace("_paragraphs_fragments_cleaned_lemmatized", "")

        cur.execute(f"SELECT id FROM articles WHERE title = %s", (article_name,))
        art_id = cur.fetchone()[0]

        all_lem = scripts_shared_functions.load_dict_from_json(full_file_path)["lemmas"]

        cur.execute(f"SELECT id FROM fragments WHERE article_id = %s", (art_id,))
        frag_ids = cur.fetchall()
        frag_ids = sorted(frag_ids)
        last_id = 0
        
        for now_lem in all_lem:
            try:
                content = " ".join(now_lem[0])
            except:
                content = ""
            cur.execute(f"INSERT INTO {table_name} (fragment_id, step, processed_text) VALUES (%s, %s, %s)", (frag_ids[last_id], "Lemma", content))
            last_id += 1
            
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    pg_data = scripts_shared_functions.get_pg_data()
    mod_init_fragments_and_elements(pg_data, "./../txt_articles/Очистка_текста/", 'fragments')
