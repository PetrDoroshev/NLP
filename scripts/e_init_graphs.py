import os
import psycopg2
import psycopg2.extras

psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

import scripts_shared_functions

def mod_e_init_graphs(pg_data, func_triplets_path, hier_triplets_path, table_name):
    json_triplets = scripts_shared_functions.load_dict_from_json(func_triplets_path)
    json_triplets = json_triplets["triplets"]

    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    for now_article in json_triplets:
        for now_article_name in now_article:
            
            article_name = now_article_name.replace("_paragraphs_cleaned", "")
            
            cur.execute(f"SELECT id FROM articles WHERE title = %s", (article_name,))
            art_id = cur.fetchone()[0]
    
            cur.execute(f"SELECT id FROM fragments WHERE article_id = %s", (art_id,))
            frag_ids = cur.fetchall()

            cur.execute(f"SELECT id FROM fragments WHERE article_id = %s", (art_id,))
            frag_ids = cur.fetchall()
            frag_ids = sorted(frag_ids)
            last_id = 0
            
            for now_triplet_js in now_article[now_article_name]:
                for now_triplet_id in now_triplet_js:
                    tr = {"graph": now_triplet_js[now_triplet_id]}

                    cur.execute(f"INSERT INTO {table_name} (fragment_id, name, type, graph_data) VALUES (%s, %s, %s, %s)", (frag_ids[last_id], "name", "func", tr))
                    last_id += 1

    hier_triplets = scripts_shared_functions.load_dict_from_json(hier_triplets_path)

    cur.execute(f"SELECT id, content FROM fragments", ())
    frag_ids = cur.fetchall()

    for now_frag_id, now_frag_cont in frag_ids:
        for now_trip in hier_triplets["triplets"]:
            if now_trip[0] in now_frag_cont and now_trip[2] in now_frag_cont:
                tr = {"graph": now_trip}
                cur.execute(f"INSERT INTO {table_name} (fragment_id, name, type, graph_data) VALUES (%s, %s, %s, %s)", (now_frag_id, "name", "hier", tr))
            
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    pg_data = scripts_shared_functions.get_pg_data()
    mod_init_fragments_and_elements(pg_data, "./../txt_articles/Очистка_текста/", 'fragments')
