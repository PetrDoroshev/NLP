import os
import io

import pymupdf
import pytesseract
from PIL import Image


def get_images(filename):
    doc = pymupdf.open(filename)
    images = []

    for page in doc.pages():
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)

    return images


def ocr_images_to_text(images):
    extracted_text = ""

    for img in images:
        print(img)
        text = pytesseract.image_to_string(img, lang="rus+eng")
        extracted_text += text + "\n\n"

    return extracted_text

pytesseract.pytesseract.tesseract_cmd = r'D:/Software/Tesseract-OCR/tesseract.exe'

for i in range(len(os.listdir("./images_articles"))):
    filename = "./images_articles/" + sorted(os.listdir("./images_articles"))[i]
    with open(f"./txt_ethalon/{filename.split('/')[-1].split('.')[0]}.txt", "w", encoding="utf-8") as f:
        print(filename)
        images = get_images(filename)
        print(len(images))
        text_from_scans = ocr_images_to_text(images)
        f.write(text_from_scans)