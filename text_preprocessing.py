import re
import os
import json

def mod_text_preprocessing(raw_parag_path, output_folder, regex_path, hunspell_check=None):
    all_raw_articles = sorted(os.listdir(raw_parag_path))

    regs = []
    with open(regex_path, "r") as f:
        regx = f.read()
        for i in regx.split("\n"):
            vals = i.split("<to>")
            if len(vals) == 2:
                regs.append([vals[0], vals[1].split("<end_regex>")[0]])

    hobj = None
    if hunspell_check is not None:
        import hunspell
        hobj = hunspell.HunSpell(hunspell_check[0], hunspell_check[1])

    for now_raw_article in all_raw_articles:
        print(f"Processing: {now_raw_article}")
        # if 'Якименко' in now_raw_article: continue
        full_file_path = os.path.join(raw_parag_path, now_raw_article)
        article_name = ".".join(now_raw_article.split(".")[:-1])

        paragraphs = load_dict_from_json(full_file_path)
        
        cleaned_paragraphs =  [clean_text(p, regs, hobj) for p in paragraphs['paragraphs']]
        
        paragraphs = {"cleaned_text": cleaned_paragraphs}
        save_dict_as_json(f"{output_folder}/{article_name}_cleaned.json", paragraphs)
    print("Completed!")


def clean_text(text, regs, hunspell):
    cleaned_text = text.lower()

    for i in regs:
        cleaned_text = re.sub(i[0], i[1], cleaned_text)
    # cleaned_text = re.sub(r'\([^)]*\)', '', text)
    # cleaned_text = re.sub('[^а-яА-Я0-9ё\s]', '', text)
    # cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
    # cleaned_text = re.sub(r"\d+", "", cleaned_text)
    # cleaned_text = re.sub(r'[a-zA-Z0-9\'_-]+', '', cleaned_text)
    # cleaned_text = re.sub('\s+', ' ', cleaned_text)

    if 'тегкартинки' in cleaned_text and hunspell is not None:
        new_text = ''
        is_word_between_tags = False
        for now_word in cleaned_text.split(' '):
            if now_word == 'тегкартинки':
                is_word_between_tags = True
            elif now_word == 'тегкартинкиконец':
                is_word_between_tags = False
            elif is_word_between_tags:
                if len(now_word) < 4 or cleaned_text.count(now_word) >= 2 or hunspell.spell(now_word):
                    new_text += now_word + ' '
                    continue
                
                variants = hunspell.suggest(now_word)
                if len(variants):
                    max_var = 0;
                    hunspelled_variant = variants[0]
                    for now_var in variants:
                        number_of_entr = new_text.count(now_var) + cleaned_text.count(now_var)
                        if number_of_entr > max_var:
                            max_var = number_of_entr
                            var = hunspelled_variant
                        
                    print(f"\tChanging '{now_word}' to '{hunspelled_variant}' (found: {max_var} times), with list {variants}")
                else:
                    hunspelled_variant = now_word
                    
                new_text += hunspelled_variant + ' '
            else:
                new_text += now_word + ' '

        cleaned_text = new_text.strip()

    cleaned_text = re.sub(r'тегкартинки\s*|\s*тегкартинкиконец', '', cleaned_text)

    return cleaned_text

def save_dict_as_json(path, dictionary):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=4)

def load_dict_from_json(path):
    with open(path, 'r', encoding='utf-8') as json_file:
        dictionary = json.load(json_file)
    return dictionary
