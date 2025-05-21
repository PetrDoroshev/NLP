import os
import re
import json

def mod_filter_fragments(norm_parag_path, output_folder, regex_path):
    all_norm_articles = sorted(os.listdir(norm_parag_path))
    
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

    for now_norm_article in all_norm_articles:
        print(f"Processing: {now_norm_article}")
        full_file_path = os.path.join(norm_parag_path, now_norm_article)
        article_name = ".".join(now_norm_article.split(".")[:-1])

        paragraphs = load_dict_from_json(full_file_path)
        
        fragments = get_fragments(paragraphs["cleaned_text"], regs_patterns)
        
        out_frag = {"fragments": fragments}
        save_dict_as_json(f"{output_folder}/{article_name}_cleaned.json", out_frag)
    print("Completed!")

def get_fragments(paragraphs, regs, min_len=5):
    '''
    for i in range(len(paragraphs)):
        if figure_pattern.search(paragraphs[i]):

            paragraph = paragraphs[i].split("\n")
            if len(paragraph) < min_len:
                for k in range(i + 1, len(paragraphs)):
                    paragraph += paragraphs[k].split("\n")
                    if len(paragraph) > min_len:
                        break

          figure_paragraphs.append("\n".join(paragraph))
    '''
    fragments = []
    now_fragment = None
    last_page = None
    
    for p in paragraphs:
        if p.startswith("ъъъууу") and p.endswith("уууъъъ"):
            if now_fragment is None:
                fragments.append(p)
            else:
                last_page = p
            continue
                
        for now_reg in regs:
            if now_reg.search(p):
                if now_fragment is not None:
                    now_fragment += f" {p}"
                else:
                    now_fragment = p
                break
        else:
            if now_fragment is not None:
                fragments.append(now_fragment)
                if last_page is not None:
                    fragments.append(last_page)
                now_fragment = None
                
    if now_fragment is not None:
        fragments.append(now_fragment)

    return fragments

def save_dict_as_json(path, dictionary):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=4)

def load_dict_from_json(path):
    with open(path, 'r', encoding='utf-8') as json_file:
        dictionary = json.load(json_file)
    return dictionary