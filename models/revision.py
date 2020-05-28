# revision.py
from mongoengine import Document, StringField, BooleanField, DateTimeField
from bson.objectid import ObjectId
from utils import T
from models import User

class Revision(Document):
    name = StringField(required=True)
    number = StringField(required=True)
    text = StringField(required=True)
    archived = BooleanField(default=False)
    created_by = StringField()
    created = DateTimeField(required=True)
    updated_by = StringField()
    updated = DateTimeField(required=True)

    @staticmethod
    def filter(**params):
        return Revision.objects.filter(**params)

    def find(self, name, archived=False):
        filter = Revision.objects(name__icontains=name, archived=archived)
        revision = filter.first()
        return revision

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

    def create_new(self, name, number, text):
        self.name = name
        self.number = number
        self.text = text
        self.created = T.now()
        self.updated = T.now()
        self.save()
        return self

    def get_or_create(self, name, number, text, archived=False):
        revision = self.find(name, archived)
        if revision is None:
            revision = self.create_new(name, number, text)
        return revision

    def get_string(self, user):
        return ''.join([
            f'_Name:_ ***{self.name}***\n',
            f'_Number:_ ***{self.number}***\n',
            f'_Date:_ ***{T.to(self.updated, user)}***\n',
            f'_Notes:_ {self.text}'
        ])

    def get_short_string(self, user):
        return ''.join([
            f'_Name:_ ***{self.name}***\n',
            f'_Number:_ ***{self.number}***\n',
            f'_Date:_ ***{T.to(self.updated, user)}***\n',
            f'_Notes:_ {self.text}'
        ])
        