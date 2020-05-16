# scenario.py
import datetime
from mongoengine import *
from mongoengine import signals
from models.character import User
from models.character import Character
from models.log import Log

class Scenario(Document):
    name = StringField(required=True)
    description = StringField()
    guild = StringField()
    channel_id = StringField()
    character = ReferenceField(Character)
    active_user = StringField()
    characters = ListField(StringField())
    archived = BooleanField(default=False)
    history_id = StringField()
    created_by = StringField()
    created = DateTimeField(required=True)
    updated_by = StringField()
    updated = DateTimeField(required=True)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if document.history_id:
            user = User().get_by_id(document.updated_by)
            user.history_id = document.history_id
            user.updated_by = document.updated_by
            user.updated = document.updated
            user.save()
            print({'history_id': document.history_id})
        else:
            changes = document._delta()[0]
            action = 'updated'
            if 'created' in kwargs:
                action = 'created' if kwargs['created'] else action
            if action == 'updated' and 'archived' in changes:
                action = 'archived' if changes['archived'] else 'restored'
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, document.category, changes, action)
            user = User().get_by_id(document.updated_by)
            if user.history_id:
                user.history_id = None
                user.updated_by = document.updated_by
                user.updated = document.updated
                user.save()
            print(changes)

    @staticmethod
    def query():
        return Scenario.objects

    @staticmethod
    def filter(**params):
        return Scenario.objects.filter(**params)

    def create_new(self, user, guild, channel_id, name, archived):
        self.name = name
        self.guild = guild
        self.channel_id = channel_id
        self.created_by = str(user.id)
        self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, guild, channel_id, name, archived=False):
        filter = Scenario.objects(guild=guild, channel_id=channel_id, name__icontains=name, archived=archived)
        user = filter.first()
        return user

    def get_or_create(self, user, guild, channel, name, archived=False):
        scenario = self.find(guild, str(channel.id), name, archived)
        if scenario is None:
            scenario = self.create_new(user, guild, str(channel.id), name, archived)
            scenario.character = Character().get_or_create(user, name, guild, scenario, 'Scenario', archived)
            scenario.updated_by = str(user.id)
            scenario.updated = datetime.datetime.utcnow()
            scenario.save()
        return scenario

    def get_by_id(self, id):
        scenario = Scenario.objects(id=id).first()
        return scenario

    def set_active_user(self, user):
        self.active_user = str(user.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
        self.save()

    def get_by_channel(self, channel):
        scenarios = Scenario.objects(channel_id=str(channel.id)).all()
        return scenarios

    def get_string_characters(self, channel):
        characters = [Character.get_by_id(id) for id in self.characters]
        characters = '***\n                ***'.join(c.name for c in characters if c)
        return f'\n            _Characters:_\n                ***{characters}***'

    def get_string(self, channel=None):
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Scenario)_ ' if str(self.id) == channel.active_scenario else ''
        description = f' - "{self.description}"' if self.description else ''
        characters = f'{self.get_string_characters()}' if self.characters else ''
        aspects = ''
        stress = ''
        if self.character:
            name = f'***{self.character.name}***' if self.character.name else name
            description = f' - "{self.character.description}"' if self.character.description else description
            aspects = self.character.get_string_aspects()
            stress = self.character.get_string_stress() if self.character.has_stress else ''
        return f'\n        {name}{active}{description}{characters}{aspects}{stress}'


signals.post_save.connect(Scenario.post_save, sender=Scenario)
        