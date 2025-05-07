from typing import SupportsIndex

import pymupdf
from pymupdf import TEXT_DEHYPHENATE
import os
from statistics import mean, median
from sklearn.cluster import DBSCAN


def extract_lines(page):

    words = [
            (pymupdf.Rect(w[:4]), w[4]) for w in page.get_text("words", sort=False, flags=TEXT_DEHYPHENATE)
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
    print(avg_line_spacing)

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

        #print(f"{spacing} - {lines[i][1]}")

    if len(paragraph) != 0:
        paragraphs.append(paragraph)

    return paragraphs

filename = os.path.join("./Articles", sorted(os.listdir("./Articles"))[7])
print(filename)

doc = pymupdf.open(filename)
for page in doc.pages():
    lines = extract_lines(page)
    if len(lines) > 1:
        paragraphs = extract_paragraphs(lines)
        for p in paragraphs:
            for line in p:
                print(line)
            print("-----------p end-----------")
