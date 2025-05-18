import difflib
import re
import os
from jiwer import wer, cer

def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)  # заменяем все пробельные символы на пробел
    return text.strip()

for filename in sorted(os.listdir("./txt_articles")):


    with open(f"./txt_ethalon/{filename}", "r", encoding="utf-8") as f1, open(f"./txt_articles/{filename}", "r", encoding="utf-8") as f2:
        ref_text = f1.read()
        hyp_text = f2.read()


        print(f"{filename} - {difflib.SequenceMatcher(None, ref_text, hyp_text).ratio()}")


