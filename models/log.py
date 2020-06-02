# log.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import datetime
from mongoengine import Document, StringField, ReferenceField, DynamicField, BooleanField, DateTimeField
from bson.objectid import ObjectId
from utils import TextUtils, T

class Log(Document):
    parent_id = StringField(required=True)
    user_id = StringField()
    guild = StringField()
    name = StringField()
    category = StringField()
    data = DynamicField()
    action = StringField()
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
    def get_by_page(cls, params, page_num=1, page_size=5, sort='-created'):
        if page_num:
            offset = (page_num - 1) * 5
            logs = cls.filter(**params).order_by(sort).skip(offset).limit(page_size).all()
        else:
            logs = cls.filter(**params).order_by(sort).all()
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

    def create_new(self, parent_id, name, user_id, guild, category, data, action):
        self.parent_id = parent_id
        self.user_id = user_id
        self.guild = guild
        self.name = name
        self.category = category
        self.data = data
        self.action = action
        self.created_by = str(user_id)
        self.created = T.now()
        self.updated_by = str(user_id)
        self.updated = T.now()
        self.save()
        return self

    def get_string(self, user=None):
        data = ''
        if self.data:
            for d in self.data:
                if '_id' not in d and d not in ['updated_by', 'created_by', 'updated', 'created']:
                    cleaned = d.replace('_', ' ')
                    data += f'\n    _{cleaned}:_ {self.get_date_string(self.data[d], user)}'
        action = self.action if self.action else 'updated'
        if action != 'created' and 'archived' in self.data:
            action = 'archived' if self.data['archived'] else 'restored'
        undo = ''.join([
            f'**{self.name}** _({self.category})_' if self.name else f'**{self.category}**',
            f' _{action} on: {T.to(self.updated, user)}_{data}'
        ])
        return undo

    def get_short_string(self, user=None):
        data = [f'{self.get_date_string(self.data[d], user)}' for d in self.data if '_id' not in d and d not in ['updated_by', 'created_by', 'updated', 'created']]
        return ': '.join(data)

    def get_date_string(self, d, user=None):
        if isinstance(d, datetime.date) or isinstance(d, datetime.datetime):
            return T.to(d, user)
        else:
            return d