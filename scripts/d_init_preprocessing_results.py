import os
import psycopg2

import scripts_shared_functions

def mod_d_init_preprocessing_results(pg_data, tokens_path, lemmas_path, table_name, article_ids, fragments_ids):
    all_tokens = sorted(os.listdir(tokens_path))
    all_lemmas = sorted(os.listdir(lemmas_path))

    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    for now_index_id_art, now_article_id in enumerate(article_ids):
        cur.execute(f"SELECT title FROM articles WHERE id = %s", (now_article_id,))
        article_name = cur.fetchone()[0]

        # cur.execute(f"SELECT id FROM fragments WHERE article_id = %s order by id", (now_article_id,))
        # all_fragments = cur.fetchall()
        
        all_fragments = fragments_ids[now_index_id_art]

        print(f"Processing: {article_name}; id {now_article_id}")

        full_file_path = f"{tokens_path}/{article_name}_paragraphs_fragments_cleaned_tokenized.json"
        all_tok = scripts_shared_functions.load_dict_from_json(full_file_path)["tokens"]
        last_id = 0
        
        for now_tok in all_tok:
            try:
                content = " ".join(now_tok[0])
            except:
                content = ""
            cur.execute(f"INSERT INTO {table_name} (fragment_id, step, processed_text) VALUES (%s, %s, %s)", (all_fragments[last_id], "Token", content))
            last_id += 1

        full_file_path = f"{lemmas_path}/{article_name}_paragraphs_fragments_cleaned_lemmatized.json"
        all_lem = scripts_shared_functions.load_dict_from_json(full_file_path)["lemmas"]
        last_id = 0
        
        for now_lem in all_lem:
            try:
                content = " ".join(now_lem[0])
            except:
                content = ""
            cur.execute(f"INSERT INTO {table_name} (fragment_id, step, processed_text) VALUES (%s, %s, %s)", (all_fragments[last_id], "Lemma", content))
            last_id += 1
            
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    pg_data = scripts_shared_functions.get_pg_data()
    mod_init_fragments_and_elements(pg_data, "./../txt_articles/Очистка_текста/", 'fragments')
