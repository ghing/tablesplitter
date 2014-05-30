from tablesplitter.command.base import SplitterCommand

from tablesplitter.conf import settings
from tablesplitter.models import ImageFile, SplitFile
from tablesplitter.splitter import registry 
from tablesplitter.signal import split_image, detect_rows, detect_columns


@split_image.connect
def image_split(sender, **kwargs): 
    input_md5 = kwargs.get('input_md5')
    filename = kwargs.get('filename')
    md5 = kwargs.get('md5')
    column = kwargs.get('column')
    row = kwargs.get('row')
    left = kwargs.get('left')
    upper = kwargs.get('upper')
    right = kwargs.get('right')
    lower = kwargs.get('lower')

    source = ImageFile.get(ImageFile.md5 == input_md5)
    split = SplitFile.create(filename=filename, md5=md5, source=source,
        row=row, column=column, left=left, upper=upper, right=right, lower=lower)
    split.create_png()

@detect_rows.connect
def handle_rows(sender, **kwargs):
    md5 = kwargs.get('md5')
    rows = kwargs.get('rows')
    image = ImageFile.get(ImageFile.md5 == md5)
    image.num_rows = rows
    image.save()

@detect_columns.connect
def handle_columns(sender, **kwargs):
    md5 = kwargs.get('md5')
    columns = kwargs.get('columns')
    image = ImageFile.get(ImageFile.md5 == md5)
    image.num_columns = columns
    image.save()



class Command(SplitterCommand):
    name = 'split_img'

    help = "Split a table image into cells"

    @classmethod
    def add_arguments(cls, parser):
        super(Command, cls).add_arguments(parser)
        parser.add_argument("--output-dir", dest="output_dir", action="store",
            default=settings.SPLIT_DIR)
        parser.add_argument("--splitter", default=settings.DEFAULT_SPLITTER)

    def run(self, args):
        splitter_cls = registry[args.splitter]
        splitter = splitter_cls(args.input_filename)
        splitter.split(args.output_dir, min_length=args.min_hline_length,
            max_gap=args.max_gap, buf=args.buffer)
