#!/usr/bin/env python

import argparse
import os
import os.path
import shlex
import subprocess

from util import cell_basename
from core import NUM_COLS, NUM_ROWS, OCR_DIR, SPLIT_DIR

def ocr_image(input_filename, num_cols, num_rows, split_dir, ocr_dir):
    for col in range(num_cols):
        for row in range(num_rows):
            basename = cell_basename(input_filename, col, row)
            path = os.path.join(split_dir, basename + '.tiff')
            outbase = os.path.join(ocr_dir, basename)
            if os.path.exists(path):
                cmd = "tesseract {} {}".format(path, outbase)
                cmd_args = shlex.split(cmd)
                subprocess.check_call(cmd_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", action="store")
    parser.add_argument("--split-dir", dest="split_dir", action="store",
        default=SPLIT_DIR)
    parser.add_argument("--ocr-dir", dest="ocr_dir", action="store",
        default=OCR_DIR)
    args = parser.parse_args()
    ocr_image(args.input_filename, NUM_COLS, NUM_ROWS, args.split_dir, args.ocr_dir)

