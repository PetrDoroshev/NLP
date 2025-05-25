import os
import re
import json

import shared_functions

def mod_filter_fragments(raw_parag_path, output_folder, regex_path):
    all_raw_articles = sorted(os.listdir(raw_parag_path))
    
    regs = []
    with open(regex_path, "r", encoding="utf-8") as f:
        regx = f.read()
        for i in regx.split("<end_regex>"):
            if "<start_regex>" in i:
                vals = i.split("<start_regex>")
                if len(vals) == 2:
                    regs.append(vals[1])
    
                print(f"Searching: '{regs[-1]}'")

    regs_patterns = [re.compile(i, re.IGNORECASE) for i in regs]

    for now_raw_article in all_raw_articles:
        print(f"Processing: {now_raw_article}")
        full_file_path = os.path.join(raw_parag_path, now_raw_article)
        article_name = ".".join(now_raw_article.split(".")[:-1])

        paragraphs = shared_functions.load_dict_from_json(full_file_path)
        
        fragments = get_fragments(paragraphs["paragraphs"], regs_patterns)
        
        out_frag = {"fragments": fragments}
        shared_functions.save_dict_as_json(f"{output_folder}/{article_name}_fragments.json", out_frag)
    print("Completed!")

def get_fragments(paragraphs, regs, min_len=5):
    fragments = []
    now_fragment = None
    last_page = None

    temp_metadata = None
    
    for raw_p in paragraphs:
        metadata, p = shared_functions.split_page_and_metadata(raw_p)

        if now_fragment is None:
            temp_metadata = metadata
                
        for now_reg in regs:
            if now_reg.search(p):
                if now_fragment is not None:
                    now_fragment += f" {p}"
                else:
                    now_fragment = p
                break
        else:
            if now_fragment is not None:
                fragments.append(f"{temp_metadata} {now_fragment}")
                temp_metadata = None
                now_fragment = None
                
    if now_fragment is not None:
        fragments.append(f"{temp_metadata} {now_fragment}")

    return fragments