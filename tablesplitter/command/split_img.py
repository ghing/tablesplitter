from tablesplitter.command.base import SplitterCommand

from tablesplitter.conf import settings
from tablesplitter.models import ImageFile, SplitFile
from tablesplitter.splitter import MSTableSplitter
from tablesplitter.signal import split_image


@split_image.connect
def image_split(sender, **kwargs): 
    input_md5 = kwargs.get('input_md5')
    filename = kwargs.get('filename')
    md5 = kwargs.get('md5')
    column = kwargs.get('column')
    row = kwargs.get('row')

    source = ImageFile.get(ImageFile.md5 == input_md5)
    SplitFile.create(filename=filename, md5=md5, source=source,
        row=row, column=column)


class Command(SplitterCommand):
    name = 'split_img'

    help = "Split a table image into cells"

    @classmethod
    def add_arguments(cls, parser):
        super(Command, cls).add_arguments(parser)
        parser.add_argument("--output-dir", dest="output_dir", action="store",
            default=settings.SPLIT_DIR)

    def run(self, args):
        splitter = MSTableSplitter(args.input_filename)
        splitter.split(args.output_dir, min_length=args.min_hline_length,
            max_gap=args.max_gap, buf=args.buffer)
