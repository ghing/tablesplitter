from datetime import datetime
import os.path

from peewee import (Model, SqliteDatabase, CharField, DateTimeField,
                    IntegerField, ForeignKeyField, TextField, fn)
from PIL import Image

from tablesplitter.conf import settings
from tablesplitter.util import slugify

db = SqliteDatabase(settings.DATABASE)


class BaseModel(Model):
    created = DateTimeField(default=datetime.now)

    class Meta:
        database = db


class Project(BaseModel):
    name = CharField()
    slug = CharField()
    instructions = TextField(default="")

    def save(self, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name)

        super(Project, self).save(**kwargs)

    def __str__(self):
        return self.name


class File(BaseModel):
    filename = CharField()
    md5 = CharField()

    def __str__(self):
        return "{} ({})".format(self.filename, self.md5)


class SourceFile(File):
    project = ForeignKeyField(Project, related_name='source_files', null=True)
    instructions = TextField(default="")


class WebImageMixin(object):
    def create_png(self, size=None):
        inpath = os.path.join(self.IMAGE_DIR, self.filename)

        im = Image.open(inpath)
        if size is not None:
            im.thumbnail(size)

        outfile = self.png_filename(size=size)
        outpath = os.path.join(self.IMAGE_DIR, outfile)

        im.save(outpath)

    def png_filename(self, filename=None, size=None):
        if filename is None:
            filename = self.filename
        base, ext = os.path.splitext(filename)
        outfile_bits = [base]

        if size is not None:
            outfile_bits.append("{}x{}".format(size[0], size[1]))

        return "-".join(outfile_bits) + ".png"

    def create_thumbnail_png(self):
        size = None
        if self.THUMBNAIL_SIZE != "original":
            size = self.THUMBNAIL_SIZE
        self.create_png(size)

    @property
    def image_url(self):
        base, ext = os.path.splitext(self.filename)
        return self.IMAGE_URL_PREFIX + base + '.png' 

    @property
    def thumbnail_url(self):
        filename = self.png_filename(size=self.THUMBNAIL_SIZE)
        return self.IMAGE_URL_PREFIX + filename


class ImageFile(WebImageMixin, File):
    IMAGE_DIR = settings.IMG_DIR
    IMAGE_URL_PREFIX = settings.IMG_URL_PREFIX + '/extracted/'
    THUMBNAIL_SIZE = 600, 600

    source = ForeignKeyField(SourceFile, related_name='derivatives', null=True)
    page = IntegerField(null=True)
    num_rows = IntegerField(null=True)
    num_columns = IntegerField(null=True)

    def get_cell_text(self, column, row):
        try:
            cell_obj = self.cells.where(SplitFile.row == row).where(SplitFile.column == column)[0]
            text, count = cell_obj.most_common_text
            return text
        except IndexError:
            return ""


class SplitFile(WebImageMixin, File):
    IMAGE_DIR = settings.SPLIT_DIR
    IMAGE_URL_PREFIX = settings.IMG_URL_PREFIX + '/cell/'
    THUMBNAIL_SIZE = "original"

    source = ForeignKeyField(ImageFile, related_name='cells')
    row = IntegerField()
    column = IntegerField()
    left = IntegerField()
    upper = IntegerField()
    right = IntegerField()
    lower = IntegerField()

    @property
    def box(self):
        return (self.left, self.upper, self.right, self.lower)

    @property
    def needs_texts(self):
        text_count = self.text.count()
        return text_count < settings.MIN_TEXTS

    @property
    def distinct_texts(self):
        return self.texts.select(Text.text, fn.Count(Text.text).alias('count'))\
                         .group_by(Text.text).dicts()

    @property
    def most_common_text(self):
        try:
            text_dict = self.distinct_texts.order_by(fn.Count(Text.text).desc())[0]
            return text_dict['text'], text_dict['count'] 
        except IndexError:
            return None

    @property
    def needs_review(self):
        return self.distinct_texts.count() != 1

class Text(BaseModel):
    METHODS = [
        ('ocr', "OCR"),
        ('manual', "Manual"),
    ]

    method = CharField(choices=METHODS) 
    source = ForeignKeyField(SplitFile, related_name='texts')
    user_id = CharField()
    text = TextField()
