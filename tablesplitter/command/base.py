import sys

import six

from tablesplitter.conf import settings

class BaseCommand(object):
    help = ""

    @classmethod
    def add_arguments(cls, parser):
        pass

    def run(self, args):
        pass

    def output(self, msg, end='\n', file=sys.stdout):
        six.print_(msg + end, file=file)

    def output_error(self, msg, end='\n'):
        self.output(msg, end=end, file=sys.stderr)


class SplitterCommand(BaseCommand):
    @classmethod 
    def add_arguments(cls, parser):
        parser.add_argument("input_filename")
        parser.add_argument("--min-hline-length", dest="min_hline_length",
            type=int, default=settings.MIN_HLINE_LENGTH)
        parser.add_argument("--min-vline-length", dest="min_vline_length",
            type=int, default=settings.MIN_VLINE_LENGTH)
        parser.add_argument("--max-gap", dest="max_gap", type=int,
            default=settings.MAX_GAP)
        parser.add_argument("--buffer", type=int, default=settings.BUFFER)
