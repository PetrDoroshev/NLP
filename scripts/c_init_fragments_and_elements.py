import os
import psycopg2
import boto3
from urllib.parse import urlparse
from botocore import UNSIGNED
from botocore.config import Config

import scripts_shared_functions


def list_public_s3_files(path_to_sss):
    proto, end_content = path_to_sss.split("://")[0], path_to_sss.split("://")[1]
    host, end_content = end_content.split("/")[0], "/".join(end_content.split("/")[1:])

    endpoint = f"{proto}://{host}/"
    bucket, prefix = end_content.split("/")[0], "/".join(end_content.split("/")[1:])

    s3 = boto3.client(
        's3',
        endpoint_url=endpoint,
        config=Config(signature_version=UNSIGNED),
    )

    paginator = s3.get_paginator('list_objects_v2')
    file_keys = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            file_keys.append(obj['Key'])

    return file_keys


def init_elements(pg_data, articles_ids, path_to_sss):
    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    art = [None for _ in articles_ids]

    for (index_id, now_id) in enumerate(articles_ids):
        cur.execute(f"SELECT title FROM articles where id = %s ", (now_id, ))
        art_name = cur.fetchone()[0]

        temp_path = path_to_sss.replace('__DONT_REMOVE_THIS_PAGE_NUM__/', '')
        temp_path = temp_path.replace('__DONT_REMOVE_THIS_ARTICLE_NAME__', art_name)
        
        files = list_public_s3_files(temp_path)
        image_dir_list = ["/".join(i.split("/")[:-1]) for i in files]
        image_dir_list = list(set(image_dir_list))

        image_dict = {}
        for f in image_dir_list:
            page_num = f.split("/page_")[1]
            full_link = path_to_sss.replace('__DONT_REMOVE_THIS_ARTICLE_NAME__', art_name)
            full_link = full_link.replace('__DONT_REMOVE_THIS_PAGE_NUM__', f'page_{page_num}')
            cur.execute(f"INSERT INTO elements (article_id, type, path) VALUES (%s, %s, %s) RETURNING id", (now_id, "image", full_link))

            elem_id = cur.fetchone()[0]

            image_dict[int(page_num)] = elem_id

        if image_dict:
            art[index_id] = image_dict
        
    conn.commit()
    cur.close()
    conn.close()
    
    return art

def mod_init_fragments_and_elements(pg_data, fragments_path, table_name, article_ids, path_to_sss):
    all_fragments = sorted(os.listdir(fragments_path))

    arts = init_elements(pg_data, article_ids, path_to_sss)

    conn = scripts_shared_functions.get_db_connetion(pg_data)
    cur = conn.cursor()

    for (index_id, now_art_id) in enumerate(article_ids):
        cur.execute(f"SELECT title FROM articles WHERE id = %s", (now_art_id,))
        article_name = cur.fetchone()[0]

        full_file_path = f"{fragments_path}/{article_name}_paragraphs_fragments_cleaned.json"

        all_frag = scripts_shared_functions.load_dict_from_json(full_file_path)["cleaned_text"]

        print(f"Processing: {article_name}; id {now_art_id}")
        
        for now_fraw in all_frag:
            digs, content = scripts_shared_functions.get_page_metadata(now_fraw)
            elem_id = arts[index_id][int(digs[1])]
            
            cur.execute(f"INSERT INTO {table_name} (article_id, element_id, content) VALUES (%s, %s, %s)", (now_art_id, elem_id, content))
            
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    pg_data = scripts_shared_functions.get_pg_data()
    mod_init_fragments_and_elements(pg_data, "./../txt_articles/Очистка_текста/", 'fragments')
