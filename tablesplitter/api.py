from peewee import JOIN_LEFT_OUTER, fn
from restless.fl import FlaskResource
from restless.utils import json

from tablesplitter.models import SplitFile, Text


class ModelResource(FlaskResource):
    def list(self):
        limit = self.request.args.get('limit', 20)
        return self.model.select().limit(limit)

    def detail(self, pk):
        return self.model.get(self.model.id == pk)


class CellResource(ModelResource):
    fields = {
        'id': 'id',
        'source': 'source.id',
        'image_url': 'image_url',
        'box': 'box',
        'text_count': 'count',
    }

    model = SplitFile

    def list(self):
        limit = self.request.args.get('limit', 20)
        text_lt = self.request.args.get('text_lt')
        random = 'random' in self.request.args

        objects = SplitFile.select(SplitFile,
                fn.Count(Text.id).alias('count')).join(Text,
                        JOIN_LEFT_OUTER).group_by(SplitFile)

        if text_lt is not None:
            text_lt = int(text_lt)
            objects = objects.having(fn.Count(Text.id) < text_lt)
        if random:
            objects = objects.order_by(fn.Random())

        return objects.limit(limit)


class TextResource(ModelResource):
    fields = {
        'id': 'id',
        'source': 'source.id',
        'text': 'text',
    }

    model = Text

    def is_authenticated(self):
        return True

    def create(self):
        source = SplitFile.get(SplitFile.id == self.data['source'])
        return Text.create(source=source, method='manual',
            text=self.data['text'], user_id=self.data['user_id'])

    def raw_deserialize(self, body):
        return json.loads(body.decode("utf-8"))
