from tablesplitter.command.base import SplitterCommand

from tablesplitter.conf import settings

from tablesplitter.splitter import MSTableSplitter

class Command(SplitterCommand):
    name = 'split_img'

    help = "Split a table image into cells"

    @classmethod
    def add_arguments(cls, parser):
        super(Command, cls).add_arguments(parser)
        parser.add_argument("--output-dir", dest="output_dir", action="store",
            default=settings.SPLIT_DIR)

    def run(self, args):
        with open(args.input_filename, 'r') as f:
            splitter = MSTableSplitter(f, args.input_filename)
            splitter.split(args.output_dir)
