import os
import psycopg2

import scripts_shared_functions

def mod_init_articles(pg_data, raw_articles_text_path, table_name):
    all_raw_articles = sorted(os.listdir(raw_articles_text_path))

    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    filled_ids = []

    for now_raw_article in all_raw_articles:
        print(f"Processing: {now_raw_article}")
        full_file_path = os.path.join(raw_articles_text_path, now_raw_article)
        article_name = str(".".join(now_raw_article.split(".")[:-1]))
        article_name = article_name.replace("_paragraphs", "")

        article_text = merge_paragraphs(full_file_path)
    
        cur.execute(f"SELECT 1 FROM {table_name} WHERE title = %s", (article_name,))
        if not cur.fetchone():
            exec_id = cur.execute(f"INSERT INTO {table_name} (title, language, content) VALUES (%s, %s, %s) RETURNING id", (article_name, 'rus', article_text))
            filled_ids.append(cur.fetchone()[0])
            print(f"Inserted: {article_name}")
        else:
            print(f"Skipped (already exists): {article_name}")
            
    conn.commit()
    cur.close()
    conn.close()

    return filled_ids

    print(filled_ids)

def merge_paragraphs(text_file_path):
    paragraphs = scripts_shared_functions.load_dict_from_json(text_file_path)["paragraphs"]
    merged_text = ""

    for i in paragraphs:
        _, now_par = scripts_shared_functions.split_page_and_metadata(i)
        merged_text += now_par
    return merged_text   

if __name__ == '__main__':
    pg_data = scripts_shared_functions.get_pg_data()
    mod_init_articles("./../txt_articles/Параграфы/", 'articles')
