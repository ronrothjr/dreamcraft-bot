# user.py
from mongoengine import *

class User(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    active_character = StringField()

    def create_new(self, name, guild):
        self.guild = guild
        self.name = name
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
        self.save()

    def get_string(self):
        return f'Player: {self.name}'
        