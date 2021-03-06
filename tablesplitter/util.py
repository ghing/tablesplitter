import hashlib
from functools import partial
import os.path
import re
from unicodedata import normalize

import six

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
    r = [i for i in range(start, center)]
    r.extend([i for i in range(center + 1, end + 1)])
    return r


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

# Slugify snipped by Armin Ronacher
# Source: http://flask.pocoo.org/snippets/5/
def slugify(text, delim=six.u('-')):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', six.text_type(word))
        if word:
            result.append(word)
    return six.text_type(delim.join(result))
