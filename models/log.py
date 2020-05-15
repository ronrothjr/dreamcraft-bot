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
    def get_by_user_id(cls, user_id, page=1, items_per_page=5):
        if page:
            offset = (page - 1) * 5
            logs = cls.filter(created_by=user_id).order_by('-created').skip( offset ).limit( items_per_page ).all()
        else:
            logs = cls.filter(created_by=user_id).order_by('-created').all()
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

    def create_new(self, parent_id, user_id, guild, category, data):
        self.parent_id = parent_id
        self.user_id = user_id
        self.guild = guild
        self.category = category
        self.data = data
        self.created_by = str(user_id)
        self.created = datetime.datetime.utcnow()
        self.updated_by = str(user_id)
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self
        