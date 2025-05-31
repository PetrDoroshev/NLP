import os
import psycopg2

import scripts_shared_functions

def init_elements(pg_data):
    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    cur.execute(f"SELECT id FROM articles", ())
    art_id = cur.fetchone()[0]

    cur.execute(f"INSERT INTO elements (article_id, type, path) VALUES (%s, %s, %s)", (art_id, "err", "err"))
            
    conn.commit()

    cur.execute(f"SELECT id FROM elements", ())
    frag = cur.fetchone()[0]
    cur.close()
    conn.close()
    return frag

def mod_init_fragments_and_elements(pg_data, fragments_path, table_name):
    all_fragments = sorted(os.listdir(fragments_path))

    fr = init_elements(pg_data)

    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    for now_fragment in all_fragments:
        full_file_path = os.path.join(fragments_path, now_fragment)
        article_name = str(".".join(now_fragment.split(".")[:-1])).replace("_paragraphs_fragments_cleaned", "")

        all_frag = scripts_shared_functions.load_dict_from_json(full_file_path)["cleaned_text"]
        cur.execute(f"SELECT id FROM articles WHERE title = %s", (article_name,))
        art_id = cur.fetchone()[0]

        print(f"Processing: {article_name}; id {art_id}")
        
        for now_fraw in all_frag:
            _, content = scripts_shared_functions.split_page_and_metadata(now_fraw)
            cur.execute(f"INSERT INTO {table_name} (article_id, element_id, content) VALUES (%s, %s, %s)", (art_id, fr, content))
            
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    pg_data = scripts_shared_functions.get_pg_data()
    mod_init_fragments_and_elements(pg_data, "./../txt_articles/Очистка_текста/", 'fragments')
