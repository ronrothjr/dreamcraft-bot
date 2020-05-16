# channel.py
import datetime
from mongoengine import *
from mongoengine import signals

from models.scenario import User
from models.scenario import Scenario
from models.scene import Scene
from models.zone import Zone
from models.log import Log

class Channel(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    active_scenario = StringField()
    active_scene = StringField()
    active_zone = StringField()
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
        return Channel.objects

    @staticmethod
    def filter(**params):
        return Channel.objects.filter(**params)

    def create_new(self, name, guild, user):
        self.name = name
        self.guild = guild
        self.created_by = str(user.id)
        self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
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
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
        self.save()

    def set_active_scene(self, scene, user):
        self.active_scene = str(scene.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
        self.save()

    def set_active_zone(self, zone, user):
        self.active_zone = str(zone.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
        self.save()

    def get_users_string(self):
        users_string = '\n***Players:***\n        ' + '\n        '.join([f'_{u}_ ' for u in self.users]) if self.users else ''
        return f'{users_string}'

    def get_scenarios_string(self):
        scenario_list = Scenario.filter(channel_id=str(self.id)).all()
        scenarios = [s.character.get_string() for s in scenario_list]
        scenarios_string = '\n***Scenarios:***\n        ' + '\n        '.join([s for s in scenarios]) if scenarios else ''
        return f'{scenarios_string}'

    def get_scenes_string(self):
        scene_list = Scene.filter(channel_id=str(self.id)).all()
        scenes = [s.character.get_string() for s in scene_list]
        scenes_string = '\n***Scenes:***\n        ' + '\n        '.join([s for s in scenes]) if scenes else ''
        return f'{scenes_string}'

    def get_string(self):
        users = f'\n{self.get_users_string()}' if self.users else ''
        scenarios = f'\n{self.get_scenarios_string()}' if self.users else ''
        scenes = f'\n{self.get_scenes_string()}' if self.users else ''
        return f'***Guild:*** {self.guild}\n***Channel:*** {self.name}{users}{scenarios}{scenes}'


signals.post_save.connect(Channel.post_save, sender=Channel)