import os
import psycopg2
import psycopg2.extras

psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

import scripts_shared_functions

def mod_e_init_graphs(pg_data, func_triplets_path, hier_triplets_path, table_name, articles_ids, fragments_ids):
    json_triplets = scripts_shared_functions.load_dict_from_json(func_triplets_path)
    json_triplets = json_triplets["triplets"]
    hier_triplets = scripts_shared_functions.load_dict_from_json(hier_triplets_path)

    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    for now_index_id_art, now_article_id in enumerate(articles_ids):
        cur.execute(f"SELECT title FROM articles WHERE id = %s", (now_article_id,))
        article_name = cur.fetchone()[0]

        # cur.execute(f"SELECT id FROM fragments WHERE article_id = %s order by id", (now_article_id,))
        # all_fragments = cur.fetchall()

        all_fragments = fragments_ids[now_index_id_art]

        print(f"Processing: {article_name}; id {now_article_id}")
        last_id = 0
        
        for now_triplet_js in json_triplets:
            try:
                temp_triplet_js = now_triplet_js[f"{article_name}_paragraphs_fragments"]
            except:
                continue
                
            for now_triplet_id in temp_triplet_js:
                for now_tr in now_triplet_id:
                    tr = {"graph": now_triplet_id[now_tr]}
    
                    cur.execute(f"INSERT INTO {table_name} (fragment_id, name, type, graph_data) VALUES (%s, %s, %s, %s)", (all_fragments[last_id], "name", "func", tr))
                    last_id += 1
    
        for now_frag_id in all_fragments:
            cur.execute(f"SELECT content FROM fragments WHERE id = %s", (now_frag_id,))
            now_frag_cont = cur.fetchone()[0]
            
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
