# zone.py
import datetime
from mongoengine import *
from mongoengine import signals
from models.character import Character
from models.log import Log

class Zone(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    description = StringField()
    channel_id = StringField()
    scene_id = StringField()
    character = ReferenceField(Character)
    active_user = StringField()
    characters = ListField(StringField())
    archived = BooleanField(default=False)
    created_by = StringField()
    created = DateTimeField(required=True)
    updated_by = StringField()
    updated = DateTimeField(required=True)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        changes = document._delta()[0]
        Log().create_new(str(document.id), document.name, document.updated_by, document.guild, 'Zone', changes)
        print(changes)

    @staticmethod
    def query():
        return Zone.objects

    @staticmethod
    def filter(**params):
        return Zone.objects.filter(**params)

    def create_new(self, user, guild, channel_id, scene_id, name, archived):
        self.name = name
        self.guild = guild
        self.channel_id = channel_id
        self.scene_id = scene_id
        self.created_by = str(user.id)
        self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, guild, channel_id, scene_id, name, archived=False):
        filter = Zone.objects(guild=guild, channel_id=channel_id, scene_id=scene_id, name__icontains=name, archived=archived)
        zone = filter.first()
        return zone

    def get_or_create(self, user, guild, channel, scene, name, archived=False):
        zone = self.find(guild, str(channel.id), str(scene.id), name, archived)
        if zone is None:
            zone = self.create_new(user, guild, str(channel.id), str(scene.id), name, archived)
            zone.character = Character().get_or_create(user, name, guild, zone, 'Zone', archived)
            zone.save()
        return zone

    def get_by_id(self, id):
        zone = Zone.objects(id=id).first()
        return zone

    def set_active_user(self, user):
        self.active_user = str(user.id)
        if (not self.created):
            self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
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


signals.post_save.connect(Zone.post_save, sender=Zone)
        