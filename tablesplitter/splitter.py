import math
import os
import os.path

from six.moves import range

from PIL import Image, ImageOps, ImageFilter

from tablesplitter.signal import split_image, detect_rows, detect_columns
from tablesplitter.util import (bufrange, threshold, getbbox_invert,
    merge_proximate, cell_basename, md5sum)


class SplitterRegistry(dict):
    def register(self, splitter_cls):
        self[splitter_cls.name] = splitter_cls


class TableSplitterBase(object):
    name = "__base__"
    transforms = {}
    span_map = {}

    def __init__(self, filename):
        self.md5 = md5sum(filename)
        self.filename = os.path.basename(filename)
        self._im = Image.open(filename)

    @property
    def im(self):
        return self._im

    def get_preprocessed_image(self, color_threshold):
        return self.im

    def get_hlines(self, **kwargs):
        raise NotImplementedError

    def get_vlines(self, **kwargs):
        raise NotImplementedError

    def transform(self, im, col, row):
        out = im
        try:
            cell_transforms = self.transforms[(col, row)]
            for transform in cell_transforms:
                name, args = transform[0], transform[1:]
                method = getattr(im, name)
                out = method(*args)
                return out
        except KeyError:
            return out 

    def get_boxes(self, **kwargs):
        hlines = self.get_hlines(**kwargs)
        num_rows = len(hlines) - 1
        detect_rows.send(self, filename=self.filename, md5=self.md5,
            rows=num_rows)
        vlines = self.get_vlines(**kwargs) 
        num_cols = len(vlines) - 1
        detect_columns.send(self, filename=self.filename, md5=self.md5,
            columns=num_cols)
        seen = [[False for y in range(num_rows)] for x in range(num_cols)]
        boxes = []

        for row in range(num_rows):
            for col in range(num_cols):
                if not seen[col][row]:
                    try:
                        # See if the area spans multiple cells
                        end_col, end_row = self.span_map[(col, row)]
                        if end_col < 0:
                            end_col = num_cols + end_col

                        if end_row < 0:
                            end_row = num_rows + end_row
                    except KeyError:
                        # By default, area is just a single cell
                        end_col = col
                        end_row = row

                    left, upper, right, lower = self._get_cell_box(col, row, end_col, end_row,
                        vlines, hlines)
                    boxes.append((col, row, left, upper, right, lower))
                    self._mark_seen(seen, col, row, end_col, end_row)

        return boxes

    def _get_cell_box(self, cellx_start, celly_start, cellx_end, celly_end,
        vlines, hlines):
        upper_left_x = vlines[cellx_start]
        upper_left_y = hlines[celly_start]
        lower_right_x = vlines[cellx_end + 1]
        lower_right_y = hlines[celly_end + 1]
                    
        return (upper_left_x, upper_left_y, lower_right_x, lower_right_y)

    def _mark_seen(self, seen, start_col, start_row, end_col, end_row):
        for col in range(start_col, end_col + 1):
            for row in range(start_row, end_row + 1):
                seen[col][row] = True

    def split(self, output_dir, **kwargs):
        """Split an image that contains a table into per-cell images"""
        for box in self.get_boxes(**kwargs):
            col, row, left, upper, right, lower = box
            region = self.im.crop((left, upper, right, lower))
            region = self.transform(region, col, row)
            # Increase contrast.  Whiteish regions become absolute white
            region = threshold(region, 200)
            output_filename = cell_basename(self.filename, col, row) + ".tiff"
            output_path = os.path.join(output_dir, output_filename)
            region.save(output_path)
            md5 = md5sum(output_path)
            split_image.send(self, input_filename=self.filename,
                input_md5=self.md5, filename=output_filename, md5=md5,
                column=col, row=row, left=left, upper=upper, right=right,
                lower=lower)


class MSTableSplitter(TableSplitterBase):
    name = "ms"

    # Define areas that span multiple cells.
    # Keys are start x, y.  Values are end x, y.
    # You can specify "-1" for the last cell to represent the last
    # cell.
    span_map = {
        (0, 0): (1, 0),
        (2, 0): (-1, 0),
        (0, 1): (1, 1),
        (2, 1): (-1, 1),
        (0, 2): (1, 2),
        (2, 3): (-1, 3),
        (0, 4): (1, 4),
        (2, 4): (-1, 4),
    }

    transforms = {
        (2, 2): [('transpose', Image.ROTATE_270)],
        (3, 2): [('transpose', Image.ROTATE_270)],
        (4, 2): [('transpose', Image.ROTATE_270)],
        (5, 2): [('transpose', Image.ROTATE_270)],
        (6, 2): [('transpose', Image.ROTATE_270)],
        (7, 2): [('transpose', Image.ROTATE_270)],
        (8, 2): [('transpose', Image.ROTATE_270)],
        (9, 2): [('transpose', Image.ROTATE_270)],
        (10, 2): [('transpose', Image.ROTATE_270)],
        (11, 2): [('transpose', Image.ROTATE_270)],
        (12, 2): [('transpose', Image.ROTATE_270)],
        (13, 2): [('transpose', Image.ROTATE_270)],
        (14, 2): [('transpose', Image.ROTATE_270)],
        (15, 2): [('transpose', Image.ROTATE_270)],
        (16, 2): [('transpose', Image.ROTATE_270)],
    }

    expected_cols = 17
    expected_rows = 29 

    def get_preprocessed_image(self, color_threshold=225):
        im = self.im

        if im.mode != 'L':
            im = im.convert('L')

        im = self.im.filter(ImageFilter.SHARPEN)
        im = threshold(im, color_threshold)
        im = im.filter(ImageFilter.FIND_EDGES)
        im = ImageOps.invert(im)
        return im

    def detect_hlines(self, im, color_threshold=225, min_length=None,
            max_gap=2, buf=2):
        startx, starty, endx, endy = getbbox_invert(im)
        lines = []

        if min_length is None:
            min_length = math.floor((endx - startx) * 0.5)

        for y in range(starty, endy):
            num_running = 0
            num_skipped = 0
            for x in range(startx, endx):
                c = im.getpixel((x, y))
                if c == 0:
                    num_running += 1
                    num_skipped = 0
                else:
                    if num_running > 200:
                        inbuf = False
                        for bufy in bufrange(y, 0, endy, buf):
                            if im.getpixel((x, bufy)) == 0:
                                inbuf = True
                                continue

                        if inbuf:
                            num_running += 1
                            num_skipped = 0
                            continue

                    num_skipped += 1

                    if num_skipped > max_gap:
                        if num_running >= min_length: 
                            lines.append(y)
                            break

                        num_running = 0
                        num_skipped = 0

        return merge_proximate(lines)

    def get_hlines(self, **kwargs):
        try:
            return self._hlines
        except AttributeError:
            im = self.get_preprocessed_image()
            self._hlines = self.detect_hlines(im, **kwargs)
            return self._hlines

    def get_vlines(self, **kwargs):
        try:
            return self._vlines
        except AttributeError:
            im = self.get_preprocessed_image()
            im = im.rotate(270)
            self._vlines = self.detect_hlines(im, **kwargs) 

            # If there's no left border, just start at the edge of the image
            if self._vlines[0] > 100:
                self._vlines.insert(0, 0)

            # Remove the right edge of the sheet
            if self._vlines[-1] > 2070:
                self._vlines.pop()

            return self._vlines

registry = SplitterRegistry()
registry.register(MSTableSplitter)
