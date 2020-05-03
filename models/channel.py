# channel.py
from mongoengine import *

class Channel(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    active_scene = StringField()
    users = ListField(StringField())

    def create_new(self, name, guild):
        self.name = name
        self.guild = guild
        self.save()
        return self

    def find(self, name, guild):
        return Channel.objects(name=name, guild=guild).first()

    def get_or_create(self, name, guild):
        channel = self.find(name, guild)
        if channel is None:
            channel = self.create_new(name, guild)
        return channel

    def set_active_scene(self, scene):
        self.active_scene = str(scene.id)
        self.save()

    def get_users_string(self):
        return 'Players:\n' + ''.join([f'        {u}\n' for u in self.users])

    def get_string(self):
        users = ''
        if self.users:
            users = 'Players:\n' + ''.join([f'        {u}\n' for u in self.users])
        scenes = ''
        return f'{users}'