# channel.py
from bson import ObjectId
from mongoengine import Document, StringField,  ListField, BooleanField, DateTimeField, signals

from models.scenario import User
from models.scenario import Character
from models.scenario import Scenario
from models.scene import Scene
from models.zone import Zone
from models.session import Session
from models.engagement import Engagement
from models.log import Log
from utils import T

class Channel(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    active_scenario = StringField()
    active_scene = StringField()
    active_zone = StringField()
    active_session = StringField()
    active_engagement = StringField()
    users = ListField(StringField())
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
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, 'Channel', changes, action)
            user = User().get_by_id(document.updated_by)
            if user.history_id:
                user.history_id = None
                user.updated_by = document.updated_by
                user.updated = document.updated
                user.save()
            print(changes)

    @staticmethod
    def query():
        return Channel.objects

    @staticmethod
    def filter(**params):
        return Channel.objects.filter(**params)

    def create_new(self, name, guild, user):
        self.name = name
        self.guild = guild
        self.created_by = str(user.id)
        self.created = T.now()
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()
        return self

    def find(self, name, guild):
        return Channel.objects(name=name, guild=guild).first()

    def get_or_create(self, name, guild, user):
        channel = self.find(name, guild)
        if channel is None:
            channel = self.create_new(name, guild, user)
        return channel

    def get_by_id(self, id):
        channel = Channel.filter(id=id).first()
        return channel

    def set_active_scenario(self, scenario, user):
        self.active_scenario = str(scenario.id)
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()

    def set_active_scene(self, scene, user):
        self.active_scene = str(scene.id)
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()

    def set_active_zone(self, zone, user):
        self.active_zone = str(zone.id)
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()

    def set_active_session(self, session, user):
        self.active_session = str(session.id)
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()

    def set_active_engagement(self, engagement, user):
        self.active_engagement = str(engagement.id)
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()

    def get_users_string(self):
        users_string = '\n_Players:_\n        ' + '\n        '.join([f'***{u}*** ' for u in self.users]) if self.users else ''
        return f'{users_string}'

    def get_scenarios_string(self):
        scenario_list = Scenario.filter(channel_id=str(self.id), archived=False).all()
        scenarios = [s.get_short_string(self) for s in scenario_list]
        scenarios_string = '\n_Scenarios:_\n        ' + '\n        '.join([s for s in scenarios]) if scenarios else ''
        return f'{scenarios_string}'

    def get_scenes(self):
        scenes = list(Scene.filter(channel_id=str(self.id), archived=False).all())
        return scenes

    def get_scenes_string(self, scene_list):
        scenes = [s.get_short_string(self) for s in scene_list]
        scenes_string = '\n_Scenes:_\n        ' + '\n        '.join([s for s in scenes]) if scenes else ''
        return f'{scenes_string}'

    def get_engagements(self):
        engagements = list(Engagement.filter(channel_id=str(self.id), archived=False).all())
        return engagements

    def get_engagements_string(self, engagement_list):
        engagements = [s.get_short_string(self) for s in engagement_list]
        engagements_string = '\n_Engagements:_\n        ' + '\n        '.join([s for s in engagements]) if engagements else ''
        return f'{engagements_string}'

    def get_characters(self, scenes):
        characters_list = []
        [[characters_list.append(c) for c in Character.filter(id__in=[ObjectId(id) for id in s.characters]).all() if c not in characters_list] for s in scenes]
        return characters_list

    def get_characters_string(self, characters_list, user=None):
        characters = [f'***{c.name}***' + (' _(Active Character)_' if user and str(c.id) == user.active_character else '') for c in characters_list]
        characters_string = '\n_Characters:_\n        ' + '\n        '.join([x for x in characters]) if characters else ''
        return f'{characters_string}'

    def get_string(self, user=None):
        users = f'\n{self.get_users_string()}' if self.users else ''
        scenarios = f'\n{self.get_scenarios_string()}' if self.users else ''
        scenes_list = self.get_scenes()
        scenes = f'\n{self.get_scenes_string(scenes_list)}'
        engagements_list = self.get_engagements()
        engagements = f'\n{self.get_engagements_string(engagements_list)}'
        characters_list = self.get_characters(scenes_list)
        characters = f'\n{self.get_characters_string(characters_list, user)}'
        return f'_Channel:_ ***{self.name}***\n_Guild:_ ***{self.guild}***{users}{scenarios}{scenes}{engagements}{characters}'


signals.post_save.connect(Channel.post_save, sender=Channel)