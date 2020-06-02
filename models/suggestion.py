# suggestion.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from mongoengine import Document, StringField, BooleanField, DateTimeField
from bson.objectid import ObjectId
from utils import T

class Suggestion(Document):
    name = StringField(required=True)
    text = StringField(required=True)
    archived = BooleanField(default=False)
    created_by = StringField()
    created = DateTimeField(required=True)
    updated_by = StringField()
    updated = DateTimeField(required=True)

    @staticmethod
    def filter(**params):
        return Suggestion.objects.filter(**params)

    def find(self, text, archived=False):
        filter = Suggestion.objects(text__icontains=text, archived=archived)
        suggestion = filter.first()
        return suggestion

    @classmethod
    def get_by_id(cls, id):
        item = cls.filter(id=ObjectId(id)).first()
        return item

    @classmethod
    def get_by_page(cls, params, page_num=1, page_size=5, sort='-created'):
        if page_num:
            offset = (page_num - 1) * page_size
            logs = cls.filter(**params).order_by(sort).skip(offset).limit(page_size).all()
        else:
            logs = cls.filter(**params).order_by(sort).all()
        return logs

    def create_new(self, name, text):
        self.name = name
        self.text = text
        self.created = T.now()
        self.updated = T.now()
        self.save()
        return self

    def get_or_create(self, name, text, archived=False):
        suggestion = self.find(name, archived)
        if suggestion is None:
            suggestion = self.create_new(name, text)
        return suggestion

    def get_string(self, user):
        return ''.join([
            f'_Name:_ ***{self.name}***\n',
            f'_Date:_ ***{T.to(self.updated, user)}***\n',
            f'_Notes:_ {self.text}'
        ])

    def get_short_string(self, user):
        return ''.join([
            f'_Name:_ ***{self.name}***\n',
            f'_Date:_ ***{T.to(self.updated, user)}***\n',
            f'_Notes:_ {self.text}'
        ])
        