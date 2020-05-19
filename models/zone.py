# zone.py
import datetime
from mongoengine import *
from mongoengine import signals
from models.character import User
from models.character import Character
from models.log import Log

class Zone(Document):
    parent_id = StringField()
    name = StringField(required=True)
    guild = StringField(required=True)
    description = StringField()
    channel_id = StringField()
    scene_id = StringField()
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
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, 'Zone', changes, action)
            user = User().get_by_id(document.updated_by)
            if user.history_id:
                user.history_id = None
                user.updated_by = document.updated_by
                user.updated = document.updated
                user.save()
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

    def get_by_channel(self, channel, archived=False):
        zones = Zone.objects(channel_id=str(channel.id), archived=archived).all()
        return zones

    @classmethod
    def get_by_page(cls, params, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * 5
            logs = cls.filter(**params).order_by('name', 'created').skip(offset).limit(page_size).all()
        else:
            logs = cls.filter(**params).order_by('name', 'created').all()
        return logs

    @classmethod
    def get_by_parent(cls, **params):
        items = cls.filter(**params).all()
        return [items] if items else []

    def archive(self, user):
            self.reverse_archive(self.user)
            self.archived = True
            self.updated_by = str(user.id)
            self.updated = datetime.datetime.utcnow()
            self.save()

    def reverse_archive(self, user):
        for z in Zone().get_by_parent(parent_id=str(self.id)):
            z.reverse_archive(self.user)
            z.archived = True
            z.updated_by = str(user.id)
            z.updated = datetime.datetime.utcnow()
            z.save()

    def restore(self, user):
            self.reverse_restore(self.user)
            self.archived = False
            self.updated_by = str(user.id)
            self.updated = datetime.datetime.utcnow()
            self.save()

    def reverse_restore(self, user):
        for z in Zone().get_by_parent(parent_id=str(self.id)):
            z.reverse_restore(self.user)
            z.archived = False
            z.updated_by = str(user.id)
            z.updated = datetime.datetime.utcnow()
            z.save()

    def get_string_characters(self, channel):
        characters = [Character.get_by_id(id) for id in self.characters]
        characters = '***\n                ***'.join(c.name for c in characters if c)
        return f'\n            _Characters:_\n                ***{characters}***'

    def get_string(self, channel):
        name = f'***{self.name}***'
        active = ''
        if channel:
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

    def get_short_string(self, channel):
        name = f'***{self.name}***'
        active = ''
        if channel:
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
        