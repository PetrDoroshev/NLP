"""
PyMuPDF Demo Script

The script addresses the frequent problem that a page's words are not present
in reading order, as it may happen when text has been added to a non-empty
page.
We read the words of a page and use their coordinates for recovering line
content.
"""

import sys
import pymupdf
from pymupdf import TEXT_DEHYPHENATE
import os
from statistics import median


def recover_lines(page):
    """Reconstitute text lines on the page by using the coordinates of the
    single words.
    """
    # extract words, sorted by bottom, then left coordinate
    words = [
        (pymupdf.Rect(w[:4]), w[4]) for w in page.get_text("words", sort=False)
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

    # sort all lines vertically
    #lines.sort(key=lambda l: (l[0].y1))

    # compute the middle value of line heights
    median_lheight = median([l[0].height for l in lines])

    text = lines[0][1]  # text of first line
    y1 = lines[0][0].y1  # its bottom coordinate
    for lrect, ltext in lines[1:]:
        distance = int(round((lrect.y0 - y1) / median_lheight))
        breaks = "\n" * (distance + 1)
        text += breaks + ltext
        y1 = lrect.y1

    # return page text
    return text


if __name__ == "__main__":
    for filename in sorted(os.listdir("./Articles")):
        doc = pymupdf.open("./Articles/" + filename)
        text = chr(12).join([recover_lines(page) for page in doc])
        with open(f"./txt_articles_rl/{filename.split('.')[0]}.txt", "w", encoding="utf-8") as f:

            f.write(text)



