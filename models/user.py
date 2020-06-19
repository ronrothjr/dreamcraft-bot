# user.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from mongoengine import Document, StringField, BooleanField, DateTimeField, DynamicField
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
    aliases = DynamicField()
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
        tz = f'\n_Timezone:_ ***{self.time_zone}***' if self.time_zone else '_None_'
        url = f'\n***Contact:*** _{self.url}_' if self.url else '_None_'
        al = ''
        if self.aliases:
            aliases = []
            for a in self.aliases:
                aliases.append(f'***{a}***\n. . . . .' + '\n. . . . .'.join([f'_{c}_' for c in self.aliases[a]]))
            al = '\n. . .'.join(a for a in aliases)
        alias_str = f'\n***Aliases:***\n. . .{al}' if al else ''
        return f'_Player:_ ***{self.name}***{tz}{url}{alias_str}'
        