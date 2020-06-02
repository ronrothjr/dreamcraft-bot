# scenario.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from mongoengine import Document, StringField, ReferenceField, ListField, BooleanField, DateTimeField, signals
from models.character import User
from models.character import Character
from models.log import Log
from utils import T

class Scenario(Document):
    parent_id = StringField()
    name = StringField(required=True)
    guild = StringField(required=True)
    description = StringField()
    channel_id = StringField()
    character = ReferenceField(Character)
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
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, 'Scenario', changes, action)
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
        self.created = T.now()
        self.updated_by = str(user.id)
        self.updated = T.now()
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
            scenario.updated = T.now()
            scenario.save()
        return scenario

    def get_by_id(self, id):
        scenario = Scenario.objects(id=id).first()
        return scenario

    @classmethod
    def get_by_channel(cls, channel, archived=False, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * page_size
            scenarios = cls.filter(channel_id=str(channel.id), archived=archived).skip(offset).limit(page_size).all()
        else:
            scenarios = cls.filter(channel_id=str(channel.id), archived=archived).order_by('name', 'created').all()
        return scenarios

    @classmethod
    def get_by_page(cls, params, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * page_size
            items = cls.filter(**params).order_by('name', 'created').skip(offset).limit(page_size).all()
        else:
            items = cls.filter(**params).order_by('name', 'created').all()
        return items

    @classmethod
    def get_by_parent(cls, **params):
        items = cls.filter(**params).all()
        return [items] if items else []

    def archive(self, user):
            self.reverse_archive(user)
            self.archived = True
            self.updated_by = str(user.id)
            self.updated = T.now()
            self.save()

    def reverse_archive(self, user):
        for s in Scenario().get_by_parent(parent_id=str(self.id)):
            s.reverse_archive(user)
            s.archived = True
            s.updated_by = str(user.id)
            s.updated = T.now()
            s.save()

    def restore(self, user):
            self.reverse_restore(user)
            self.archived = False
            self.updated_by = str(user.id)
            self.updated = T.now()
            self.save()

    def reverse_restore(self, user):
        for s in Scenario().get_by_parent(parent_id=str(self.id)):
            s.reverse_restore(user)
            s.archived = False
            s.updated_by = str(user.id)
            s.updated = T.now()
            s.save()

    def get_string_characters(self):
        scenes = list(Scene.get_by_scenario(scenario=self, page_num=0))
        characters = [Character.filter(id__in=[ObjectId(id) for id in s.characters]) for s in scenes]
        characters = '***\n                ***'.join(c.name for c in characters if c)
        return f'\n            _Characters:_\n                ***{characters}***'

    def get_string(self, channel=None):
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Scenario)_ ' if str(self.id) == channel.active_scenario else ''
        description = f' - "{self.description}"' if self.description else ''
        characters = '' # f'{self.get_string_characters()}'
        aspects = ''
        stress = ''
        if self.character:
            name = f'***{self.character.name}***' if self.character.name else name
            description = f' - "{self.character.description}"' if self.character.description else description
            aspects = self.character.get_string_aspects()
            stress = self.character.get_string_stress() if self.character.has_stress else ''
        return f'        {name}{active}{description}{characters}{aspects}{stress}'

    def get_short_string(self, channel=None):
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Scenario)_ ' if str(self.id) == channel.active_scenario else ''
        if self.character:
            name = f'***{self.character.name}***' if self.character.name else name
        return f'        {name}{active}'


signals.post_save.connect(Scenario.post_save, sender=Scenario)
        