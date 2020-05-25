# engagement.py
from mongoengine import Document, StringField, ReferenceField, ListField, BooleanField, DateTimeField, signals
from models.character import User
from models.character import Character
from models.log import Log
from utils import T

class Engagement(Document):
    parent_id = StringField()
    name = StringField(required=True)
    guild = StringField(required=True)
    description = StringField()
    channel_id = StringField()
    scene_id = StringField()
    type_name = StringField()
    character = ReferenceField(Character)
    characters = ListField(StringField())
    opposition = ListField(StringField())
    started_on = DateTimeField()
    ended_on = DateTimeField()
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
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, 'Engagement', changes, action)
            user = User().get_by_id(document.updated_by)
            if user.history_id:
                user.history_id = None
                user.updated_by = document.updated_by
                user.updated = document.updated
                user.save()
            print(changes)

    @staticmethod
    def query():
        return Engagement.objects

    @staticmethod
    def filter(**params):
        return Engagement.objects.filter(**params)

    def create_new(self, user, guild, channel_id, scene_id, name, archived):
        self.name = name
        self.guild = guild
        self.parent_id = scene_id
        self.channel_id = channel_id
        self.scene_id = scene_id
        self.created_by = str(user.id)
        self.created = T.now()
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()
        return self

    def find(self, guild, channel_id, scene_id, name, archived=False):
        filter = Engagement.objects(guild=guild, channel_id=channel_id, scene_id=scene_id, name__icontains=name, archived=archived)
        engagement = filter.first()
        return engagement

    def get_or_create(self, user, guild, channel, scene, name, archived=False):
        engagement = self.find(guild, str(channel.id), str(scene.id), name, archived)
        if engagement is None:
            engagement = self.create_new(user, guild, str(channel.id), str(scene.id), name, archived)
            engagement.character = Character().get_or_create(user, name, guild, engagement, 'Engagement', archived)
            engagement.save()
        return engagement

    def get_by_id(self, id):
        engagement = Engagement.objects(id=id).first()
        return engagement

    @classmethod
    def get_by_channel(cls, channel, archived=False, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * page_size
            items = cls.filter(channel_id=str(channel.id), archived=archived).skip(offset).limit(page_size).all()
        else:
            items = cls.filter(channel_id=str(channel.id), archived=archived).order_by('name', 'created').all()
        return items

    @classmethod
    def get_by_scene(cls, scene, archived=False, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * page_size
            items = cls.filter(scene_id=str(scene.id), archived=archived).skip(offset).limit(page_size).all()
        else:
            items = cls.filter(scene_id=str(scene.id), archived=archived).order_by('name', 'created').all()
        return items

    @classmethod
    def get_by_page(cls, params, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * page_size
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
        for z in Engagement().get_by_parent(parent_id=str(self.id)):
            z.reverse_archive(user)
            z.archived = True
            z.updated_by = str(user.id)
            z.updated = T.now()
            z.save()

    def restore(self, user):
            self.reverse_restore(user)
            self.archived = False
            self.updated_by = str(user.id)
            self.updated = T.now()
            self.save()

    def reverse_restore(self, user):
        for z in Engagement().get_by_parent(parent_id=str(self.id)):
            z.reverse_restore(user)
            z.archived = False
            z.updated_by = str(user.id)
            z.updated = T.now()
            z.save()

    def get_string_characters(self, channel=None):
        characters = [Character.get_by_id(id) for id in self.characters]
        characters = '***\n                ***'.join(c.name for c in characters if c)
        return f'            _Characters:_\n                ***{characters}***'

    def get_string(self, channel, user=None):
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Engagement)_ ' if str(self.id) == channel.active_engagement else ''
        start = ''
        if self.started_on:
            start = f'\n_Started On:_ ***{T.to(self.started_on, user)}***' if self.started_on else ''
        end = ''
        if self.ended_on:
            end = f'\n_Ended On:_ ***{T.to(self.ended_on, user)}***' if self.ended_on else ''
        description = f' - "{self.description}"' if self.description else ''
        characters = f'\n\n{self.get_string_characters()}' if self.characters else ''
        aspects = ''
        stress = ''
        if self.character:
            name = f'***{self.character.name}***' if self.character.name else name
            description = f' - "{self.character.description}"' if self.character.description else description
            aspects = self.character.get_string_aspects()
            stress = self.character.get_string_stress() if self.character.has_stress else ''
        return f'        {name}{active}{start}{end}{description}{characters}{aspects}{stress}'

    def get_short_string(self, channel=None):
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = f' _(Active {str(self.type_name).title()})_ ' if str(self.id) == channel.active_engagement else f' _({str(self.type_name).title()})_ '
        characters = f'\n{self.get_string_characters()}' if self.characters else ''
        description = f' - "{self.description}"' if self.description else ''
        if self.character:
            name = f'***{self.character.name}***' if self.character.name else name
            description = f' - "{self.character.description}"' if self.character.description else ''
        return f'        {name}{active}{description}{characters}'


signals.post_save.connect(Engagement.post_save, sender=Engagement)
        