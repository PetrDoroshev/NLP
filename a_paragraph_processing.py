import re
import os
import io
import json
import pymupdf

from pymupdf import TEXT_DEHYPHENATE, TEXTFLAGS_WORDS
from statistics import mean, median

import shared_functions

# Главная функция для обработки параграфов и текста
def mod_paragraph_processing(articles_docs, output_folder, teseract_mode, images_store_dir):
    all_raw_articles = sorted(os.listdir(articles_docs))

    for now_raw_article in all_raw_articles:
        print(f"Processing: {now_raw_article}")
        # if 'Твёрдые электролиты' not in now_raw_article: continue
        full_file_path = os.path.join(articles_docs, now_raw_article)
        article_name = ".".join(now_raw_article.split(".")[:-1])

        imgs_dir = images_store_dir
        if images_store_dir is not None:
            imgs_dir = os.path.join(images_store_dir, article_name)
            try:
                os.mkdir(imgs_dir)
                print(f"\tFolder created {imgs_dir}")
            except OSError as error:
                pass

        paragraphs = get_paragraphs(full_file_path, teseract_mode, imgs_dir)

        report_dict = {"paragraphs": paragraphs}
        shared_functions.save_dict_as_json(f"{output_folder}/{article_name}_paragraphs.json", report_dict)

    print("Completed!")

# Основная функция, которая парсит файл и возвращает параграфы
def get_paragraphs(filename, teseract_path=None, imgs_dir=None):
    min_px_size = 25
    min_px_size_vect = 60
    doc = pymupdf.open(filename)
    article_name = ".".join(filename.split("/")[-1].split(".")[:-1])
    paragraphs = []

    do_image_in_doc_exists = False
    latest_image_page = None

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
            image_id = (page_id + 1) * 1000
            
            if imgs_dir is not None:                
                for img_index, img in enumerate(images_data):
                    
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    
                    if not base_image["image"]:
                        continue

                    img_pil = Image.open(io.BytesIO(base_image["image"]))
                    width, height = img_pil.size

                    if min(width, height) <= min_px_size:
                        continue

                    page_path = os.path.join(imgs_dir, f'page_{page_id+1}')
                    os.makedirs(page_path, exist_ok=True)
                    
                    ext = base_image["ext"]
                    filename = f"image_{image_id}.{ext}"
                    output_path = os.path.join(page_path, filename)
                    
                    with open(output_path, "wb") as f:
                        f.write(base_image["image"])
                        latest_image_page = image_id // 1000
                    
                    image_id += 1
                    
                for draw_index, path in enumerate(page.get_drawings()):
                    try:
                        rect = path["rect"]
                        dpi = 72
                        width_px = rect.width * dpi / 72
                        height_px = rect.height * dpi / 72
                        if min(width_px, height_px) >= min_px_size_vect:
                            pix = page.get_pixmap(clip=rect)
                            page_path = os.path.join(imgs_dir, f'page_{page_id+1}')
                            os.makedirs(page_path, exist_ok=True)
                            filename = f"image_{image_id}.png"
                            output_path = os.path.join(page_path, filename)
                            pix.save(f"{output_path}")
                            image_id += 1
                            latest_image_page = image_id // 1000
                    except Exception as e:
                        pass
                        # print(f"Error with drawing {draw_index} on page {page_id}: {e}")
        
        # paragraphs.append(f"ъъъууу{"ш" * (page_id + 1)}уууъъъ")
        if latest_image_page is None:
            continue
        paragraphs.append(shared_functions.create_metadata(page_id + 1, latest_image_page))
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
    temp_metadata = None

    for now_parag_raw in pars:
        metadata, now_parag = shared_functions.split_page_and_metadata(now_parag_raw)
        if metadata is not None:
            temp_metadata = metadata
            continue
            
        if len(now_parag) < 5:
            last_parag += now_parag
        elif len(last_parag) > 500 and re.search(r'(?<!\d)\s*\.\s*(?!\d)', now_parag):
            splits = re.split(r'(?<!\d)\s*\.\s*(?!\d)', now_parag, 1)
            last_parag += splits[0]
            last_parag += '.'

            if temp_metadata is not None:
                last_parag = f"{temp_metadata} {last_parag}"
            new_paragraphs.append(last_parag)
            
            last_parag = splits[1].lstrip()
            last_parag = last_parag.lstrip('.')
        elif now_parag.strip().endswith('.'):
            last_parag += now_parag
            if temp_metadata is not None:
                last_parag = f"{temp_metadata} {last_parag}"
            new_paragraphs.append(last_parag)
            last_parag = ""
        else:
            last_parag += now_parag

    if temp_metadata is not None:
        last_parag = f"{temp_metadata} {last_parag}"
        temp_metadata = None
    new_paragraphs.append(last_parag)
    return new_paragraphs

def merge_paragraphs(paragraphs):
    merged_paragraphs = []
    i = 0
    n = len(paragraphs)

    temp_metadata = None

    while i < n:
        temp_metadata, current = shared_functions.split_page_and_metadata(paragraphs[i])

        if temp_metadata is None:
            # current = paragraphs[i]
                
            # Пока текущая строка заканчивается на '-' и есть следующая строка
            while (current.endswith('-')) and i + 1 < n:
                i += 1
                # next_paragraph = paragraphs[i]
                metadata, next_paragraph = shared_functions.split_page_and_metadata(paragraphs[i])
                if metadata is not None and temp_metadata is None:
                    temp_metadata = metadata
                    continue
                    
                current = current[:-1] + next_paragraph

        merged_paragraphs.append(current)
        if temp_metadata is not None:
            merged_paragraphs.append(temp_metadata)
            temp_metadata = None
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

if __name__ == "__main__":
    filename = os.path.join("./Articles", sorted(os.listdir("./Articles"))[7])
    for p in get_paragraphs(filename, False):
        print(p)
        print("-------------r---------------")