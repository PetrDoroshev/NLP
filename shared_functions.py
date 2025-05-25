import re
import json

def save_dict_as_json(path, dictionary):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=4)

def load_dict_from_json(path):
    with open(path, 'r', encoding='utf-8') as json_file:
        dictionary = json.load(json_file)
    return dictionary

def get_page_metadata(full_text):
    if not full_text.startswith("[(page"):
        return None, full_text

    pattern = r'\[\(page \d+\) \(latest_image_id \d+\)\]'
    match = re.search(pattern, full_text)
    if match:
        metadata = match.group(1)
        other_content = re.sub(pattern, '', full_text).strip()

        digit_pattern = r'\d+'
        metadata_digits = re.findall(digit_pattern, metadata)
        
        return metadata_digits, other_content
    else:
        return None, full_text

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

def create_metadata(page_num, image_in_page_num):
    return f"[(page {page_num}) (latest_image_id {image_in_page_num})]"