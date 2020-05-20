# user.py
import datetime
from mongoengine import Document, StringField, BooleanField, DateTimeField
from bson.objectid import ObjectId

class User(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    role = StringField()
    active_character = StringField()
    time_zone = StringField()
    module = StringField()
    command =  StringField()
    question = StringField()
    answer = StringField()
    archived = BooleanField(default=False)
    history_id = StringField()
    created_by = StringField()
    created = DateTimeField(required=True)
    updated_by = StringField()
    updated = DateTimeField(required=True)

    def create_new(self, name, guild):
        self.guild = guild
        self.name = name
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    @staticmethod
    def filter(**params):
        return User.objects.filter(**params)

    def find(self, name, guild):
        filter = User.objects(name=name, guild=guild)
        user = filter.first()
        return user

    @classmethod
    def get_by_id(cls, id):
        character = cls.filter(id=ObjectId(id)).first()
        return character

    def get_or_create(self, name, guild):
        user = self.find(name, guild)
        if user is None:
            user = self.create_new(name, guild)
        return user

    def set_active_character(self, character):
        self.active_character = str(character.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()

    def get_string(self):
        tz = self.time_zone if self.time_zone else '_None_'
        return f'Player: {self.name}\nTimezone: {tz}'
        