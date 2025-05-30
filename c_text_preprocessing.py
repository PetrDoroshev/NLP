import re
import os
import json

import shared_functions

def mod_text_preprocessing(raw_fragments_path, output_folder, regex_path, hunspell_check=None):
    all_raw_fragments = sorted(os.listdir(raw_fragments_path))

    regs = []
    with open(regex_path, "r", encoding="utf-8") as f:
        regx = f.read()
        for i in regx.split("<end_regex>"):
            if "<from>" in i:
                reg = i.split("<from>")[1];
                vals = reg.split("<to>")
                if len(vals) == 2:
                    regs.append([vals[0], vals[1].split("<end_regex>")[0]])
    
                print(f"'{regs[-1][0]}' to '{regs[-1][1]}'")

    hobj = None
    if hunspell_check is not None:
        import hunspell
        hobj = hunspell.HunSpell(hunspell_check[0], hunspell_check[1])

    for now_raw_fragment in all_raw_fragments:
        print(f"Processing: {now_raw_fragment}")
        # if 'Якименко' in now_raw_article: continue
        full_file_path = os.path.join(raw_fragments_path, now_raw_fragment)
        article_name = ".".join(now_raw_fragment.split(".")[:-1])

        paragraphs = shared_functions.load_dict_from_json(full_file_path)
        
        full_text = ""
        cleaned_fragments = []
        
        for p_raw in paragraphs['fragments']:
            metadata, p = shared_functions.split_page_and_metadata(p_raw)
            page_text = clean_text(p, regs, hobj, full_text)
            cleaned_fragments.append(f"{metadata} {page_text}")
            full_text += page_text
        
        clean_fragments = {"cleaned_text": cleaned_fragments}
        shared_functions.save_dict_as_json(f"{output_folder}/{article_name}_cleaned.json", clean_fragments)
    print("Completed!")


def clean_text(text, regs, hunspell, full_text):
    cleaned_text = text.lower()
    
    old_text = cleaned_text
    for i in regs:
        cleaned_text = re.sub(i[0], i[1], cleaned_text)
        
    while old_text != cleaned_text:
        old_text = cleaned_text
        for i in regs:
            cleaned_text = re.sub(i[0], i[1], cleaned_text)

    if 'тегкартинки' in cleaned_text and hunspell is not None:
        new_text = ''
        is_word_between_tags = False
        pr_word = None
        for now_word in cleaned_text.split(' '):
            if now_word == 'тегкартинки':
                is_word_between_tags = True
            elif now_word == 'тегкартинкиконец':
                is_word_between_tags = False
            elif is_word_between_tags:
                if pr_word is not None:
                    if hunspell.spell(pr_word + now_word):
                        new_text += (pr_word+now_word) + ' '
                        continue

                if len(now_word) <= 2:
                    if pr_word is not None:
                        pr_word += now_word
                    else:
                        pr_word = now_word
                    continue

                t_var = f" {now_word} "
                if len(t_var) < 4 or full_text.count(t_var) >= 2 or hunspell.spell(now_word):
                    new_text += now_word + ' '
                    continue
                    
                variants = hunspell.suggest(now_word)
                if len(variants):
                    max_var = 0;
                    hunspelled_variant = variants[0]
                    for now_var in variants:
                        t_var = f" {now_var} "
                        number_of_entr = new_text.count(t_var) + full_text.count(t_var)
                        if number_of_entr > max_var:
                            max_var = number_of_entr
                            var = hunspelled_variant
                        
                    print(f"\tChanging '{now_word}' to '{hunspelled_variant}' (found: {max_var} times), with list {variants}")
                else:
                    if pr_word is not None:
                        variants = hunspell.suggest(pr_word + now_word)
                        if len(variants):
                            max_var = 0;
                            hunspelled_variant = variants[0]
                            for now_var in variants:
                                t_var = f" {now_var} "
                                number_of_entr = new_text.count(t_var) + full_text.count(t_var)
                                if number_of_entr > max_var:
                                    max_var = number_of_entr
                                    var = hunspelled_variant
                            print(f"\tChanging '{now_word}' to '{hunspelled_variant}' (found: {max_var} times), with list {variants}")
                        else:
                            pr_word = pr_word + now_word
                            continue
                    else:
                        pr_word = now_word
                        continue
                    
                new_text += hunspelled_variant + ' '
                pr_word = None
            else:
                new_text += now_word + ' '

        cleaned_text = new_text.strip()
        cleaned_text = cleaned_text.lower()

        old_text = cleaned_text
        for i in regs:
            cleaned_text = re.sub(i[0], i[1], cleaned_text)
            
        while old_text != cleaned_text:
            old_text = cleaned_text
            for i in regs:
                cleaned_text = re.sub(i[0], i[1], cleaned_text)

    cleaned_text = re.sub(r'тегкартинки\s*|\s*тегкартинкиконец', '', cleaned_text)
    cleaned_text = cleaned_text.strip()

    return cleaned_text