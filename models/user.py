# user.py
import datetime
from mongoengine import *
from mongoengine import signals

class User(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    role = StringField()
    active_character = StringField()
    time_zone = StringField()
    command =  StringField()
    question = StringField()
    answer = StringField()
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)\

    def create_new(self, name, guild):
        self.guild = guild
        self.name = name
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, name, guild):
        filter = User.objects(name=name, guild=guild)
        user = filter.first()
        return user

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
        