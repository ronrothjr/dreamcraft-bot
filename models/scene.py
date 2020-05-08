# scene.py
import datetime
from mongoengine import *
from models.channel import Channel
from models.character import Character

class Scene(Document):
    name = StringField(required=True)
    description = StringField()
    channel = ReferenceField(Channel)
    character = ReferenceField(Character)
    active_user = StringField()
    characters = ListField(StringField())
    archived = BooleanField(default=False)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    def create_new(self, user, channel, name, archived):
        self.name = name
        self.channel = channel.id
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, channel, name, archived):
        filter = Scene.objects(channel=channel.id, name__icontains=name, archived=archived)
        user = filter.first()
        return user

    def get_or_create(self, user, channel, name, archived=False):
        scene = self.find(channel, name, archived)
        if scene is None:
            scene = self.create_new(user, channel, name, archived)
            self.character = Character().get_or_create(user, name, channel.guild, scene, 'Scene', archived)
            scene.save()
        return scene

    def get_by_id(self, id):
        scene = Scene.objects(id=id).first()
        return scene

    def set_active_user(self, user):
        self.active_user = str(user.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()

    def get_by_channel(self, channel):
        scenes = Scene.objects(channel=channel.id).all()
        return scenes

    def get_string_characters(self):
        characters = '***\n                ***'.join(self.characters)
        return f'\n            _Characters:_\n                ***{characters}***'

    def get_string(self, channel):
        name = f'***{self.name}***'
        active = active = ' _(Active Scene)_' if str(self.id) == channel.active_scene else ''
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
        