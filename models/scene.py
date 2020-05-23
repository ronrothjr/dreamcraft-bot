# scene.py
from bson import ObjectId
from mongoengine import Document, StringField, ReferenceField, ListField, BooleanField, DateTimeField, signals
from models.character import User
from models.character import Character
from models.zone import Zone
from models.engagement import Engagement
from models.log import Log
from utils import T

class Scene(Document):
    parent_id = StringField()
    name = StringField(required=True)
    guild = StringField(required=True)
    description = StringField()
    channel_id = StringField()
    scenario_id = StringField()
    character = ReferenceField(Character)
    characters = ListField(StringField())
    archived = BooleanField(default=False)
    history_id = StringField()
    started_on = DateTimeField()
    ended_on = DateTimeField()
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
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, 'Scene', changes, action)
            user = User().get_by_id(document.updated_by)
            if user.history_id:
                user.history_id = None
                user.updated_by = document.updated_by
                user.updated = document.updated
                user.save()
            print(changes)

    @staticmethod
    def query():
        return Scene.objects

    @staticmethod
    def filter(**params):
        return Scene.objects.filter(**params)

    def create_new(self, user, guild, channel_id, scenario_id, name, archived):
        self.name = name
        self.guild = guild
        self.channel_id = channel_id
        self.scenario_id = scenario_id
        self.created_by = str(user.id)
        self.created = T.now()
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()
        return self

    def find(self, guild, channel_id, scenario_id, name, archived=False):
        filter = Scene.objects(guild=guild, channel_id=channel_id, scenario_id=scenario_id, name__icontains=name, archived=archived)
        scene = filter.first()
        return scene

    def get_or_create(self, user, guild, channel, scenario, name, archived=False):
        scene = self.find(guild, str(channel.id), str(scenario.id), name, archived)
        if scene is None:
            scene = self.create_new(user, guild, str(channel.id), str(scenario.id), name, archived)
            scene.character = Character().get_or_create(user, name, guild, scene, 'Scene', archived)
            scene.save()
        return scene

    def get_by_id(self, id):
        scene = Scene.objects(id=id).first()
        return scene

    @classmethod
    def get_by_channel(cls, channel, archived=False, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * 5
            items = cls.filter(channel_id=str(channel.id), archived=archived).skip(offset).limit(page_size).all()
        else:
            items = cls.filter(channel_id=str(channel.id), archived=archived).order_by('name', 'created').all()
        return items

    @classmethod
    def get_by_scenario(cls, scenario, archived=False, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * 5
            items = cls.filter(scenario_id=str(scenario.id), archived=archived).skip(offset).limit(page_size).all()
        else:
            items = cls.filter(scenario_id=str(scenario.id), archived=archived).order_by('name', 'created').all()
        return items

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
            self.reverse_archive(user)
            self.archived = True
            self.updated_by = str(user.id)
            self.updated = T.now()
            self.save()

    def reverse_archive(self, user):
        for s in Scene().get_by_parent(parent_id=str(self.id)):
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
        for s in Scene().get_by_parent(parent_id=str(self.id)):
            s.reverse_restore(user)
            s.archived = False
            s.updated_by = str(user.id)
            s.updated = T.now()
            s.save()

    def get_string_engagements(self, channel):
        engagements = '\n                '.join(f'***{e.name}***' + (f' _(Active {str(e.type_name).title()})_' if str(e.id) == channel.active_engagement else f' _({str(e.type_name).title()})_') for e in Engagement.filter(scene_id=str(self.id), archived=False) if e)
        return f'\n\n            _Engagements:_\n                {engagements}' if engagements else ''

    def get_string_zones(self, channel):
        zones = '\n                '.join(f'{z.get_short_string(channel)}' for z in Zone.filter(scene_id=str(self.id), archived=False) if z)
        return f'            _Zones:_\n                {zones}' if zones else ''

    def get_string_characters(self, user=None):
        characters = '\n                '.join(f'***{c.name}***' + (' _(Active Character)_' if user and str(c.id) == user.active_character else '') for c in Character.filter(id__in=[ObjectId(id) for id in self.characters], archived=False) if c)
        return f'            _Characters:_\n                {characters}'

    def get_short_string_characters(self, user=None):
        characters = ', '.join(c.name for c in Character.filter(id__in=[ObjectId(id) for id in self.characters], archived=False) if c)
        return f'\n...({characters})'

    def get_string(self, channel=None, user=None):
        if not user.time_zone:
            raise Exception('No time zone defined```css\n.d user timezone New_York```')
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Scene)_ ' if str(self.id) == channel.active_scene else ''
        start = ''
        if self.started_on:
            start = f'\n_Started On:_ ***{T.to(self.started_on, user)}***' if self.started_on else ''
        end = ''
        if self.ended_on:
            end = f'\n_Ended On:_ ***{T.to(self.ended_on, user)}***' if self.ended_on else ''
        description = f' - "{self.description}"' if self.description else ''
        zones = f'\n\n{self.get_string_zones(channel)}'
        characters = f'\n\n{self.get_string_characters(user)}' if self.characters else ''
        engagements = self.get_string_engagements(channel)
        aspects = ''
        stress = ''
        if self.character:
            name = f'***{self.character.name}***' if self.character.name else name
            description = f' - "{self.character.description}"' if self.character.description else description
            aspects = self.character.get_string_aspects()
            stress = self.character.get_string_stress() if self.character.has_stress else ''
        return f'        {name}{active}{start}{end}{description}{zones}{engagements}{characters}{aspects}{stress}'

    def get_short_string(self, channel=None, user=None):
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Scene)_ ' if channel and str(self.id) == channel.active_scene else ''
        characters = f' {self.get_short_string_characters(user)}' if self.characters else ''
        return f'        {name}{active}{characters}'


signals.post_save.connect(Scene.post_save, sender=Scene)
        