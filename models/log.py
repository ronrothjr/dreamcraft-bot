# log.py
import datetime
from mongoengine import *

class Log(Document):
    parent_id = StringField(required=True)
    user_id = StringField()
    guild = StringField()
    name = StringField()
    category = StringField()
    data = DynamicField()
    created_by = StringField()
    created = DateTimeField(required=True)
    updated_by = StringField()
    updated = DateTimeField(required=True)

    @staticmethod
    def query():
        return Log.objects

    @staticmethod
    def filter(**params):
        return Log.objects.filter(**params)

    @classmethod
    def get_by_id(cls, id):
        log = cls.filter(id=ObjectId(id)).first()
        return log

    @classmethod
    def get_by_page(cls, params, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * 5
            logs = cls.filter(**params).order_by('-created').skip(offset).limit(page_size).all()
        else:
            logs = cls.filter(**params).order_by('-created').all()
        return logs

    @classmethod
    def get_by_parent(cls, parent, category=''):
        logs = []
        params = {}
        if parent:
            params.update(parent_id=str(parent.id))
        if category:
            params.update(category=category)
        return logs

    def create_new(self, parent_id, name, user_id, guild, category, data):
        self.parent_id = parent_id
        self.user_id = user_id
        self.guild = guild
        self.name = name
        self.category = category
        self.data = data
        self.created_by = str(user_id)
        self.created = datetime.datetime.utcnow()
        self.updated_by = str(user_id)
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self
        