import re
import os
import io
import json
import pymupdf

from pymupdf import TEXT_DEHYPHENATE, TEXTFLAGS_WORDS
from statistics import mean, median

# Главная функция для обработки параграфов и текста
def mod_paragraph_processing(articles_docs, output_folder, teseract_mode):
    all_raw_articles = sorted(os.listdir(articles_docs))

    for now_raw_article in all_raw_articles:
        print(f"Processing: {now_raw_article}")
        # if 'Якименко' not in now_raw_article: continue
        full_file_path = os.path.join(articles_docs, now_raw_article)
        article_name = ".".join(now_raw_article.split(".")[:-1])

        paragraphs = get_paragraphs(full_file_path, teseract_mode)

        report_dict = {"paragraphs": paragraphs}
        save_dict_as_json(f"{output_folder}/{article_name}_paragraphs.json", report_dict)

    print("Completed!")

# Основная функция, которая парсит файл и возвращает параграфы
def get_paragraphs(filename, teseract_path=None):
    doc = pymupdf.open(filename)
    paragraphs = []

    do_image_in_doc_exists = False

    if teseract_path is not None:
        import pytesseract
        from PIL import Image
        if teseract_path != "<linux>":
            pytesseract.pytesseract.tesseract_cmd = teseract_path

    last_processed_image_page_id = -1

    for page_id, page in enumerate(doc):
        images_data = page.get_images(full=True)
        if do_image_in_doc_exists or images_data:
            do_image_in_doc_exists = True
        else:
            continue
        
        lines = extract_lines(page)
        if len(lines) > 1:
            last_processed_image_page_id = -1
            paragraphs_lines = extract_paragraphs(lines)
            
            for p in paragraphs_lines:
            
                paragraph_line = ""
                lines = [line[1] for line in p]
            
                for i in range(len(lines)):
            
                    line = lines[i]
                    if line.endswith("-"):
                        if i != len(lines) - 1: line = line[:-1]
                        paragraph_line += f'{line}'
                    else:
                        paragraph_line += f'{line}\n'
            
                paragraphs.append(paragraph_line)
        elif teseract_path is not None and images_data:
            if last_processed_image_page_id == -1:
                print(f"\tScan processing for page №{page_id}")
            else:
                if page_id % 10 == 0:
                    print(f"\tScan processing for page №{page_id} and at least one page before")
            text = ""
            last_processed_image_page_id = page_id

            for img_idx, img in enumerate(images_data, start=1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"] 
                
                img = Image.open(io.BytesIO(image_bytes))
                img_text = pytesseract.image_to_string(img, lang="rus")
                
                text += f" тег_картинки {img_text.strip()} тег_картинки_конец "

            all_paragraphs = [i + '\n' for i in text.split('\n')]
            paragraphs.extend(all_paragraphs)
        else:
            print(f"\tPage {page_id} skipped due no text or no image or disabled teseract")
            
    return  group_paragraphs(merge_paragraphs(paragraphs))

# Дополнительное объеденение параграфов на основании числа знаков и наличия/позиции точки
def group_paragraphs(pars):
    new_paragraphs = []

    last_parag = ""

    for now_parag in pars:
        if len(now_parag) < 5:
            last_parag += now_parag
        elif len(last_parag) > 500 and re.search(r'(?<!\d)\s*\.\s*(?!\d)', now_parag):
            splits = re.split(r'(?<!\d)\s*\.\s*(?!\d)', now_parag, 1)
            last_parag += splits[0]
            last_parag += '.'
            new_paragraphs.append(last_parag)
            last_parag = splits[1].lstrip()
            last_parag = last_parag.lstrip('.')
        elif now_parag.strip().endswith('.'):
            last_parag += now_parag
            new_paragraphs.append(last_parag)
            last_parag = ""
        else:
            last_parag += now_parag
    new_paragraphs.append(last_parag)
    return new_paragraphs

def merge_paragraphs(paragraphs):
    merged_paragraphs = []
    i = 0
    n = len(paragraphs)

    while i < n:
        current = paragraphs[i]
        # Пока текущая строка заканчивается на '-' и есть следующая строка
        while (current.endswith('-')) and i + 1 < n:
            i += 1
            next_paragraph = paragraphs[i]
            current = current[:-1] + next_paragraph
        merged_paragraphs.append(current)
        i += 1

    return merged_paragraphs


def extract_lines(page):
    words = [
            (pymupdf.Rect(w[:4]), w[4]) for w in page.get_text("words", sort=False, flags=TEXTFLAGS_WORDS)
        ]

    if len(words) == 0:
        return ""

    lines = []  # list of reconstituted lines
    line = [words[0]]  # current line
    lrect = words[0][0]  # the line's rectangle

    # walk through the words
    for wr, text in words:
        w0r, _ = line[-1]  # read previous word in current line

        # if this word matches top or bottom of the line, append it
        if abs(lrect.y0 - wr.y0) <= 3 or abs(lrect.y1 - wr.y1) <= 3:
            line.append((wr, text))
            lrect |= wr
        else:
            # output current line and re-initialize
            # note that we sort the words in current line first
            ltext = " ".join([w[1] for w in sorted(line, key=lambda w: w[0].x0)])
            lines.append((lrect, ltext))
            line = [(wr, text)]
            lrect = wr

    # also append last unfinished line
    ltext = " ".join([w[1] for w in sorted(line, key=lambda w: w[0].x0)])
    lines.append((lrect, ltext))

    return lines

def extract_paragraphs(lines: list):
    if len(lines) < 1:
        return

    paragraphs = []
    paragraph = [lines[0]]


    avg_line_spacing = median([abs(lines[i][0].y1 - lines[i + 1][0].y0) for i in range(len(lines) - 1)])
    avg_line_width = median([lines[i][0].x1 - lines[i][0].x0 for i in range(len(lines))])

    for i in range(1, len(lines)):

        prev_rect = lines[i - 1][0]
        current_rect = lines[i][0]
        spacing = current_rect.y0 - prev_rect.y1


        if (((spacing - avg_line_spacing) > 2 and spacing > 0) or prev_rect.x0 < current_rect.x0
                or current_rect.x1 - prev_rect.x1 > avg_line_width / 2):

            paragraphs.append(paragraph.copy())
            paragraph.clear()
            paragraph.append(lines[i])
        else:
            paragraph.append(lines[i])

    if len(paragraph) != 0:
        paragraphs.append(paragraph)

    return paragraphs

def get_figures_paragraphs(paragraphs, min_len=5):
    figure_pattern = re.compile(r'(рис\.|рисун[a-я]{2})', re.IGNORECASE)
    figure_paragraphs = []

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
    for p in paragraphs:
        if figure_pattern.search(p):
            figure_paragraphs.append(p)

    return figure_paragraphs

def save_dict_as_json(path, dictionary):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    filename = os.path.join("./Articles", sorted(os.listdir("./Articles"))[7])
    for p in get_paragraphs(filename, False):
        print(p)
        print("-------------r---------------")