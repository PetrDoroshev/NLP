import pymupdf
from pymupdf import TEXT_DEHYPHENATE
import os
from statistics import mean, median
from razdel import sentenize
import re

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




def get_paragraphs(filename):

    doc = pymupdf.open(filename)
    paragraphs = []

    for page in doc:
         lines = extract_lines(page)
         if len(lines) > 1:
            paragraphs_lines =  extract_paragraphs(lines)
            for p in paragraphs_lines:
                paragraphs.append("\n".join([line[1] for line in p]))

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

def split_paragraphs_on_sent(paragraphs):

    splited_paragraphs = []

    for p in paragraphs:

        sentences = []

        for sent in sentenize(p):
            sentences.append(sent)

        splited_paragraphs.append(sentences)

    return splited_paragraphs

if __name__ == "__main__":

    filename = os.path.join("./Articles", sorted(os.listdir("./Articles"))[5])
    for p in get_paragraphs(filename):
        print(p)
        print("-------------r---------------")

