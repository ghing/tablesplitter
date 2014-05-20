from datetime import datetime
import os.path

from peewee import (Model, SqliteDatabase, CharField, DateTimeField,
                    IntegerField, ForeignKeyField, TextField)
from PIL import Image

from tablesplitter.conf import settings
from tablesplitter.util import slugify

db = SqliteDatabase('tablesplitter.db')


class BaseModel(Model):
    created = DateTimeField(default=datetime.now)

    class Meta:
        database = db

class Project(BaseModel):
    name = CharField()
    slug = CharField(null=True)

    def save(self, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name)

        super(Project, self).save(**kwargs)

    def __str__(self):
        return self.name


class File(BaseModel):
    filename = CharField()
    md5 = CharField()
    project = ForeignKeyField(Project, null=True)

    def __str__(self):
        return "{} ({})".format(self.filename, self.md5)

class SourceFile(File):
    pass

class ImageFile(File):
    source = ForeignKeyField(SourceFile, related_name='derivatives', null=True)
    page = IntegerField(null=True)

class SplitFile(File):
    source = ForeignKeyField(ImageFile, related_name='cells')
    row = IntegerField()
    column = IntegerField()
    left = IntegerField()
    upper = IntegerField()
    right = IntegerField()
    lower = IntegerField()

    def create_png(self):
        inpath = os.path.join(settings.SPLIT_DIR, self.filename)
        base, ext = os.path.splitext(self.filename)
        outpath = os.path.join(settings.SPLIT_DIR, base + ".png")
        Image.open(inpath).save(outpath)

    @property
    def image_url(self):
        base, ext = os.path.splitext(self.filename)
        return settings.IMG_URL_PREFIX + '/' + base + '.png' 

    @property
    def box(self):
        return (self.left, self.upper, self.right, self.lower)

class Text(BaseModel):
    METHODS = [
        ('ocr', "OCR"),
        ('manual', "Manual"),
    ]

    method = CharField(choices=METHODS) 
    source = ForeignKeyField(SplitFile, related_name='conversions')
    user_id = CharField()
    text = TextField()
