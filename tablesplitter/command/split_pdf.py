import glob
import os.path
import re
import subprocess

from blinker import signal

from tablesplitter.conf import settings
from tablesplitter.command.base import BaseCommand
from tablesplitter.models import Project, File, ImageFile
from tablesplitter.util import md5sum

def output_prefix(input_filename, output_dir):
    name, ext = os.path.splitext(os.path.basename(input_filename))
    return os.path.join(output_dir, name)

def pdf_to_images(input_filename, output_dir, first=None, last=None):
    cmd_args = [
        "pdftoppm",
        "-gray",
    ]

    if first is not None:
        cmd_args.append("-f")
        cmd_args.append(first)

    if last is not None:
        cmd_args.append("-l")
        cmd_args.append(last)

    cmd_args.append(input_filename)

    cmd_args.append(output_prefix(input_filename, output_dir))

    subprocess.check_call(cmd_args)

extract_image = signal('extract_image')

@extract_image.connect
def image_extracted(sender, input_filename, input_md5, output_filename,
        output_md5, page, project=None):
    try:
        project_obj = Project.get(Project.slug == project)
    except Project.DoesNotExist:
        project_obj = None

    try:
        input_file = File.get(File.md5 == input_md5, File.project == project_obj) 
    except File.DoesNotExist:
        input_file = File.create(md5=input_md5, filename=input_filename,
            project=project_obj)

    ImageFile.create(md5=output_md5, filename=output_filename,
        source=input_file, page=page)


class Command(BaseCommand):
    name = 'split_pdf'

    help = "Split an image PDF document into individual images"

    _page_num_re = re.compile(r'^[^\s]+-(\d+).pgm$')

    @classmethod        
    def add_arguments(cls, parser):
        parser.add_argument('input_filename')
        parser.add_argument("--output_dir", dest="output_dir", 
            default=settings.IMG_DIR)
        parser.add_argument("--first", default=None)
        parser.add_argument("--last", default=None)
        parser.add_argument("--project", default=None)

    def run(self, args):
        pdf_to_images(args.input_filename, output_dir=args.output_dir,
                first=args.first, last=args.last)
        self.report_extracted(args.input_filename, args.output_dir,
            project=args.project)

    def page_num(self, filename):
        m = self._page_num_re.match(filename)
        return int(m.groups()[0])

    def report_extracted(self, input_filename, output_dir, project):
        input_filename_base = os.path.basename(input_filename)
        input_md5 = md5sum(input_filename)
        pathname = output_prefix(input_filename, output_dir) + "*.pgm"
        for fname in glob.glob(pathname):
            output_filename = os.path.basename(fname)
            output_md5 = md5sum(fname)
            page_num = self.page_num(output_filename)
            extract_image.send(self, input_filename=input_filename_base,
                input_md5=input_md5, output_filename=output_filename,
                output_md5=output_md5, page=page_num, project=project)
