#!/usr/bin/env python

import argparse
import os
import os.path

import csv

from util import cell_basename
from core import NUM_COLS, NUM_ROWS, OUTPUT_CSV_DIR, OCR_DIR

def merge_ocr(input_filename, num_cols, num_rows, ocr_dir):
    data = []
    for row in range(num_rows):
        row_data = []
        for col in range(num_cols):
            row_data.append(get_cell_text(col, row, input_filename, ocr_dir))
        
        data.append(row_data)
    return data

def get_cell_text(col, row, input_filename, ocr_dir):
    basename = cell_basename(input_filename, col, row)
    path = os.path.join(ocr_dir, basename + ".txt")
    try:
        with open(path, "r") as f:
            text = get_cell_text_from_file(f)
    except IOError:
        text = ""
    return text

def get_cell_text_from_file(f):
    lines = []
    for line in f:
        cleanline = line.strip()
        if cleanline != "":
            lines.append(cleanline)
    return "\n".join(lines)

def get_output_filename(input_filename, csv_dir):
    base, oldext = os.path.splitext(os.path.basename(input_filename))
    return os.path.join(csv_dir, base + ".csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", action="store")
    parser.add_argument("--ocr-dir", dest="ocr_dir", action="store",
        default=OCR_DIR)
    parser.add_argument("--csv_dir", dest="csv_dir",
        default=OUTPUT_CSV_DIR)
    args = parser.parse_args()
    data = merge_ocr(args.input_filename, NUM_COLS, NUM_ROWS, args.ocr_dir)
    output_filename = get_output_filename(args.input_filename, args.csv_dir)

    with open(output_filename, 'wb') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)
