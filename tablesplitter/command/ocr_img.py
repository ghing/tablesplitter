#!/usr/bin/env python

import os
import os.path
import shlex
import subprocess

from tablesplitter.command.base import BaseCommand
from tablesplitter.conf import settings
from tablesplitter.util import cell_basename

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


class Command(BaseCommand):
    name = 'ocr_img'

    help = "OCR cell images"

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("input_filename", action="store")
        parser.add_argument("--cols", type=int)
        parser.add_argument("--rows", type=int)
        parser.add_argument("--split-dir", dest="split_dir", action="store",
            default=settings.SPLIT_DIR)
        parser.add_argument("--ocr-dir", dest="ocr_dir", action="store",
            default=settings.OCR_DIR)

    def run(self, args):
        ocr_image(args.input_filename, args.cols, args.rows, args.split_dir, args.ocr_dir)


