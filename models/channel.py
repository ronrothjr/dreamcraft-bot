# channel.py
import datetime
from mongoengine import *

from models.scenario import Scenario
from models.scene import Scene

class Channel(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    active_scenario = StringField()
    active_scene = StringField()
    users = ListField(StringField())
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    @staticmethod
    def query():
        return Channel.objects

    @staticmethod
    def filter(**params):
        return Channel.objects.filter(**params)

    def create_new(self, name, guild):
        self.name = name
        self.guild = guild
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, name, guild):
        return Channel.objects(name=name, guild=guild).first()

    def get_or_create(self, name, guild):
        channel = self.find(name, guild)
        if channel is None:
            channel = self.create_new(name, guild)
        return channel

    def get_by_id(self, id):
        channel = Channel.filter(id=id).first()
        return channel

    def set_active_scenario(self, scenario):
        self.active_scenario = str(scenario.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()

    def set_active_scene(self, scene):
        self.active_scene = str(scene.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()

    def get_users_string(self):
        users_string = '***Players:***\n        ' + '\n        '.join([f'_{u}_ ' for u in self.users]) if self.users else ''
        return f'{users_string}'

    def get_scenarios_string(self):
        scenario_list = Scenario.filter(channel_id=str(self.id)).all()
        scenarios = [s.character.get_string() for s in scenario_list]
        scenarios_string = '***Scenarios:***\n        ' + '\n        '.join([s for s in scenarios]) if scenarios else ''
        return f'{scenarios_string}'

    def get_scenes_string(self):
        scene_list = Scene.filter(channel_id=str(self.id)).all()
        scenes = [s.character.get_string() for s in scene_list]
        scenes_string = '***Scenes:***\n        ' + '\n        '.join([s for s in scenes]) if scenes else ''
        return f'{scenes_string}'

    def get_string(self):
        users = f'\n{self.get_users_string()}' if self.users else ''
        scenarios = f'\n{self.get_sscenarios_string()}' if self.users else ''
        scenes = f'\n{self.get_scenes_string()}' if self.users else ''
        return f'***Guild:*** {self.guild}\n***Channel:*** {self.name}{users}{scenarios}{scenes}'