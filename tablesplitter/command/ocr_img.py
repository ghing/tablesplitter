#!/usr/bin/env python

import os
import os.path
import shlex
import subprocess

from tablesplitter.command.base import BaseCommand
from tablesplitter.conf import settings
from tablesplitter.models import SplitFile, Text
from tablesplitter.util import cell_basename, md5sum
from tablesplitter.signal import image_text


@image_text.connect
def handle_text(sender, **kwargs): 
    filename = kwargs.get('source_filename')
    md5 = kwargs.get('source_md5')
    method = kwargs.get('method')
    user = kwargs.get('user')
    text = kwargs.get('text')

    source = SplitFile.get(SplitFile.filename == filename, SplitFile.md5 == md5)
    Text.create(source=source, user_id=user, text=text, method=method)

class Command(BaseCommand):
    name = 'ocr_img'

    help = "OCR cell images"

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("input_filename", action="store")
        parser.add_argument("--cols", type=int, required=True)
        parser.add_argument("--rows", type=int, required=True)
        parser.add_argument("--split-dir", dest="split_dir", action="store",
            default=settings.SPLIT_DIR)
        parser.add_argument("--ocr-dir", dest="ocr_dir", action="store",
            default=settings.OCR_DIR)
        parser.add_argument("--user", default="tesseract")

    def run(self, args):
        self.ocr_image(args.input_filename, args.cols, args.rows,
                       args.split_dir, args.ocr_dir, args.user)

    def ocr_image(self, input_filename, num_cols, num_rows, split_dir, ocr_dir,
            user):
        for col in range(num_cols):
            for row in range(num_rows):
                basename = cell_basename(input_filename, col, row)
                img_filename = basename + '.tiff'
                path = os.path.join(split_dir, img_filename)
                outbase = os.path.join(ocr_dir, basename)
                if os.path.exists(path):
                    img_md5 = md5sum(path)
                    cmd = "tesseract {} {}".format(path, outbase)
                    cmd_args = shlex.split(cmd)
                    subprocess.check_call(cmd_args)
                    output_filename = outbase + '.txt'
                    with open(output_filename, 'r') as f:
                        text = f.read()
                        image_text.send(self, source_filename=img_filename, 
                            source_md5=img_md5, method='ocr',
                            text=text, user=user)
