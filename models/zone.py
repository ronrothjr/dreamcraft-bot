# zone.py
import datetime
from mongoengine import *
from models.character import Character

class Zone(Document):
    name = StringField(required=True)
    description = StringField()
    channel_id = StringField()
    scene_id = StringField()
    character = ReferenceField(Character)
    active_user = StringField()
    characters = ListField(StringField())
    archived = BooleanField(default=False)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    @staticmethod
    def query():
        return Zone.objects

    @staticmethod
    def filter(**params):
        return Zone.objects.filter(**params)

    def create_new(self, user, channel_id, scene_id, name, archived):
        self.name = name
        self.channel_id = channel_id
        self.scene_id = scene_id
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, channel_id, scene_id, name, archived=False):
        filter = Zone.objects(channel_id=channel_id, scene_id=scene_id, name__icontains=name, archived=archived)
        zone = filter.first()
        return zone

    def get_or_create(self, user, channel, scene, name, archived=False):
        zone = self.find(str(channel.id), str(scene.id), name, archived)
        if zone is None:
            zone = self.create_new(user, str(channel.id), str(scene.id), name, archived)
            zone.character = Character().get_or_create(user, name, channel.guild, zone, 'Zone', archived)
            zone.save()
        return zone

    def get_by_id(self, id):
        zone = Zone.objects(id=id).first()
        return zone

    def set_active_user(self, user):
        self.active_user = str(user.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()

    def get_by_channel(self, channel):
        zones = Zone.objects(channel_id=str(channel.id)).all()
        return zones

    def get_string_characters(self, channel):
        characters = [Character.get_by_id(id) for id in self.characters]
        characters = '***\n                ***'.join(c.name for c in characters if c)
        return f'\n            _Characters:_\n                ***{characters}***'

    def get_string(self, channel):
        name = f'***{self.name}***'
        active = ' _(Active Zone)_ ' if str(self.id) == channel.active_zone else ''
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
        