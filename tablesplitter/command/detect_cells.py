
from PIL import ImageDraw

from tablesplitter.command.base import SplitterCommand
from tablesplitter.splitter import MSTableSplitter

import sys

class Command(SplitterCommand):
    name = 'detect_cells'

    help = "Display detected cells"

    def run(self, args):
        with open(args.input_filename, 'r') as f:
            splitter = MSTableSplitter(f, args.input_filename)
            hlines = splitter.get_hlines(min_length=args.min_hline_length,
                max_gap=args.max_gap, buf=args.buffer)
            num_rows = len(hlines) - 1
            self.output("Horizontal lines: {}".format(hlines))
            vlines = splitter.get_vlines(min_length=args.min_vline_length,
                max_gap=args.max_gap, buf=args.buffer)
            num_cols = len(vlines) - 1 
            self.output("Vertical lines: {}".format(vlines))

            success = num_cols == splitter.expected_cols and num_rows == splitter.expected_rows 
            
            code = 0 if success else 1
            msg = "Detected {} columns and {} rows.".format(num_cols, num_rows)
            if not success:
                msg += " Expected {} columns and {} rows.".format(splitter.expected_cols, splitter.expected_rows)
               

            self.output(msg)

            overlayed = self.overlay_lines(splitter.im, hlines, vlines)
            overlayed.show()

            sys.exit(code)

    def overlay_lines(self, im, hlines, vlines, color=(255, 0, 0)):
        xsize, ysize = im.size
        colored = im.convert("RGB")
        draw = ImageDraw.Draw(colored)
        for y in hlines:
            draw.line((0, y, xsize, y), fill=color)

        for x in vlines:
            draw.line((x, 0, x, ysize), color)

        return colored 
