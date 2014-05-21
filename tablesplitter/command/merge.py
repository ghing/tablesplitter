#!/usr/bin/env python

import csv
import os
import os.path

from tablesplitter.command.base import BaseCommand
from tablesplitter.conf import settings
from tablesplitter.models import ImageFile
from tablesplitter.util import cell_basename

def merge_ocr(input_filename, num_cols, num_rows, ocr_dir):
    data = []
    image_obj = ImageFile.get(ImageFile.filename == os.path.basename(input_filename))
           
    for row in range(num_rows):
        row_data = []
        for col in range(num_cols):
            row_data.append(get_cell_text(col, row, image_obj))
        
        data.append(row_data)
    return data

def get_cell_text(col, row, image_obj):
    return image_obj.get_cell_text(col, row)

def get_cell_text_from_file(col, row, input_filename, ocr_dir):
    basename = cell_basename(input_filename, col, row)
    path = os.path.join(ocr_dir, basename + ".txt")
    try:
        with open(path, "r") as f:
            text = read_cell_text_from_file(f)
    except IOError:
        text = ""
    return text

def read_cell_text_from_file(f):
    lines = []
    for line in f:
        cleanline = line.strip()
        if cleanline != "":
            lines.append(cleanline)
    return "\n".join(lines)

def get_output_filename(input_filename, csv_dir):
    base, oldext = os.path.splitext(os.path.basename(input_filename))
    return os.path.join(csv_dir, base + ".csv")


class Command(BaseCommand):
    name = 'merge'

    help = "Merge OCRed or transcriped text into a single CSV file"

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("input_filename", action="store")
        parser.add_argument("--cols", type=int)
        parser.add_argument("--rows", type=int)
        parser.add_argument("--ocr-dir", dest="ocr_dir", action="store",
            default=settings.OCR_DIR)
        parser.add_argument("--csv_dir", dest="csv_dir",
            default=settings.OUTPUT_CSV_DIR)

    def run(self, args):
        data = merge_ocr(args.input_filename, args.cols, args.rows, args.ocr_dir)
        output_filename = get_output_filename(args.input_filename, args.csv_dir)

        with open(output_filename, 'w') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
