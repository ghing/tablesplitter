import hashlib
from functools import partial
import os.path

from PIL import ImageOps

def cell_basename(input_filename, col, row):
    base, oldext = os.path.splitext(os.path.basename(input_filename))
    return "{0}__{1:03d}__{2:03d}".format(base, col, row)

def threshold(im, threshold):
    return im.point(lambda p: p > threshold and 255)

def getbbox_invert(im):
    """Get bounding box, removing white borders"""
    invert_im = ImageOps.invert(im)
    return invert_im.getbbox()

def merge_proximate(vals, max_space=5):
    previous = None
    deduped = []

    if len(vals) == 0:
        return vals

    for val in vals:
        if previous is None:
            previous = val
        elif val - previous <= max_space:
            previous = val
        else:
            deduped.append(previous)
            previous = val

    if previous == val:
        deduped.append(val)

    return deduped

def bufrange(center, minval, maxval, size):
    start = center - size
    start = start if start >= minval else minval
    end = center + size
    end = end if end < maxval else maxval
    r = range(start, center)
    r.extend(range(center + 1, end + 1))
    return r


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()
