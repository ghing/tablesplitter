from peewee import JOIN_LEFT_OUTER, fn
from restless.fl import FlaskResource
from restless.preparers import FieldsPreparer
from restless.serializers import JSONSerializer 

from tablesplitter.models import SplitFile, Text, Project


class FixedJSONSerializer(JSONSerializer):
    def deserialize(self, body):
        return super(FixedJSONSerializer, self).deserialize(body.decode("utf-8"))


class ModelResource(FlaskResource):
    def list(self):
        limit = self.request.args.get('limit', 20)
        return self.model.select().limit(limit)

    def detail(self, pk):
        return self.model.get(self.model.id == pk)


class CellResource(ModelResource):
    preparer = FieldsPreparer(fields = {
        'id': 'id',
        'source': 'source.id',
        'image_url': 'image_url',
        'box': 'box',
        'text_count': 'count',
    })

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
    preparer = FieldsPreparer(fields = {
        'source': 'source.id',
        'text': 'text',
        'accepted': 'accepted',
    })
    serializer = FixedJSONSerializer()

    model = Text

    def is_authenticated(self):
        return True

    def create(self):
        source = SplitFile.get(SplitFile.id == self.data['source'])
        return Text.create(source=source, method='manual',
            text=self.data['text'], user_id=self.data['user_id'])

    def update(self, pk):
        try:
            text = Text.objects.get(Text.id == pk)
        except Text.DoesNotExist:
            text = Text()

        source = SplitFile.get(SplitFile.id == self.data['source'])
        text.source = source
        text.text = self.data['text']
        text.accepted = self.data['accepted']
        text.save()
        return text


class ProjectResource(ModelResource):
    preparer = FieldsPreparer(fields = {
        'id': 'id',
        'name': 'name',
        'slug': 'slug',
        'instructions': 'instructions',
    })

    serializer = FixedJSONSerializer()

    model = Project 
