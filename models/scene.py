# scene.py
from mongoengine import *
from models.channel import Channel
from models.character import Character
from models.aspect import Aspect

class Scene(Document):
    name = StringField(required=True)
    description = StringField()
    channel = ReferenceField(Channel)
    char_id = StringField()
    active_user = StringField()
    characters = ListField(StringField())

    def create_new(self, channel, name):
        self.name = name
        self.channel = channel.id
        self.save()
        return self

    def find(self, channel, name):
        filter = Scene.objects(channel=channel.id,name__icontains=name)
        user = filter.first()
        return user

    def get_or_create(self, channel, name):
        user = self.find(channel, name)
        if user is None:
            user = self.create_new(channel, name)
        return user

    def get_by_id(self, id):
        scene = Scene.objects(id=id).first()
        return scene

    def set_active_user(self, user):
        self.active_user = str(user.id)
        self.save()

    def get_by_channel(self, channel):
        scenes = Scene.objects(channel=channel.id).all()
        return scenes

    def get_string_aspects(self):
        return f'\n            Aspects:\n                ' + ('\n                '.join([a.get_string() for a in Aspect().get_by_parent_id(self.id)]))

    def get_string_characters(self):
        return f'\n            Characters:\n                ' + ('\n                '.join(self.characters))

    def get_string(self, channel):
        active = ''
        if str(self.id) == channel.active_scene:
            active = ' (Active)'
        description = ''
        if self.description:
            description = f' - "{self.description}"'
        aspects = f'{self.get_string_aspects()}'
        characters = ''
        if self.characters:
            characters = f'{self.get_string_characters()}'
        return f'\n        {self.name}{active}{description}{aspects}{characters}'
        