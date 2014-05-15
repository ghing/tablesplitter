#!/usr/bin/env python

import argparse
import sys

from PIL import ImageDraw

from tablesplitter.conf import settings

from tablesplitter.splitter import MSTableSplitter

MIN_HLINE_LENGTH = MIN_VLINE_LENGTH = 150 
MAX_GAP = 2
BUF = 4

def report_detected_cells(input_filename):
    with open(input_filename, 'r') as f:
        splitter = MSTableSplitter(f, input_filename)
        hlines = splitter.get_hlines(min_length=MIN_HLINE_LENGTH,
            max_gap=MAX_GAP, buf=BUF)
        num_rows = len(hlines) - 1
        print "Horizontal lines: {}".format(hlines)
        vlines = splitter.get_vlines(min_length=MIN_VLINE_LENGTH,
            max_gap=MAX_GAP, buf=BUF)
        num_cols = len(vlines) - 1 
        print "Vertical lines: {}".format(vlines)

        success = num_cols == splitter.expected_cols and num_rows == splitter.expected_rows 
        
        code = 0 if success else 1
        msg = "Detected {} columns and {} rows.".format(num_cols, num_rows)
        if not success:
            msg += " Expected {} columns and {} rows.".format(splitter.expected_cols, splitter.expected_rows)
           

        print(msg)

        overlayed = overlay_lines(splitter.im, hlines, vlines)
        overlayed.show()

        sys.exit(code)

def overlay_lines(im, hlines, vlines, color=(255, 0, 0)):
    xsize, ysize = im.size
    colored = im.convert("RGB")
    draw = ImageDraw.Draw(colored)
    for y in hlines:
        draw.line((0, y, xsize, y), fill=color)

    for x in vlines:
        draw.line((x, 0, x, ysize), color)

    return colored 

def split_img(filename, output_dir):
    with open(filename, 'r') as f:
        splitter = MSTableSplitter(f, filename)
        splitter.split(output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", action="store")
    parser.add_argument("--output-dir", dest="output_dir", action="store",
        default=settings.SPLIT_DIR)
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    if args.report:
        report_detected_cells(args.input_filename)
    else:
        split_img(args.input_filename, output_dir=args.output_dir)
