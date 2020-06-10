# user.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from mongoengine import Document, StringField, BooleanField, DateTimeField
from bson.objectid import ObjectId
from utils import T

class User(Document):
    name = StringField(required=True)
    discriminator = StringField()
    display_name = StringField()
    guild = StringField(required=True)
    role = StringField()
    active_character = StringField()
    time_zone = StringField()
    url = StringField()
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

    def create_new(self, name, guild, discriminator=None, display_name=None):
        self.guild = guild
        self.name = name
        if discriminator:
            self.discriminator = discriminator
        if display_name:
            self.display_name = display_name
        self.created = T.now()
        self.updated = T.now()
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

    def get_or_create(self, name, guild, discriminator=None, display_name=None):
        user = self.find(name, guild)
        if user is None:
            user = self.create_new(name, guild, discriminator, display_name)
        elif discriminator and not user.discriminator:
            user.discriminator = discriminator
            user.display_name = display_name
            user.updated = T.now()
            user.save()
        return user

    def set_active_character(self, character):
        self.active_character = str(character.id)
        self.updated = T.now()
        self.save()

    def get_string(self):
        tz = self.time_zone if self.time_zone else '_None_'
        url = self.url if self.url else '_None_'
        return f'_Player:_ ***{self.name}***\n_Timezone:_ ***{tz}***\n***Contact:*** _{url}_'
        