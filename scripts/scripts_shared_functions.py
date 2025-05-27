import os
import psycopg2
import json
import re

def get_pg_data():
    try:
        with open('../.env') as f:
            for line in f:
                if not line.strip() or line.startswith('#'):
                    continue
                key, value = line.strip().split('=', 1)

                if key in os.environ:
                    print(f"Skipping {key} because already found")
                    continue
                else:
                    os.environ[key] = value
    except:
        pass
    
    db_params = {
        "host": '' or os.environ['NLP_PG_HOST'],
        "port": '' or os.environ['NLP_PG_PORT'],
        "db_name": '' or os.environ['NLP_PG_DB_NAME'],
        "user": '' or os.environ['NLP_PG_USER'],
        "password": '' or os.environ['NLP_PG_PASSWORD'],
    }
    
    return db_params


def get_db_connetion(pg_data):
    return psycopg2.connect(
        host=pg_data["host"],
        port=int(pg_data["port"]),
        dbname=pg_data["db_name"],
        user=pg_data["user"],
        password=pg_data["password"]
    )

def load_dict_from_json(path):
    with open(path, 'r', encoding='utf-8') as json_file:
        dictionary = json.load(json_file)
    return dictionary


def split_page_and_metadata(full_text):
    if not full_text.startswith("[(page"):
        return None, full_text

    pattern = r'\[\(page \d+\) \(latest_image_id \d+\)\]'
    match = re.search(pattern, full_text)
    if match:
        metadata = match.group(0)
        other_content = re.sub(pattern, '', full_text).strip()
        
        return metadata, other_content
    else:
        return None, full_text
