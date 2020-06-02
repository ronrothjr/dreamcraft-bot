# session.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from bson import ObjectId
from mongoengine import Document, StringField, ReferenceField, ListField, BooleanField, DateTimeField, signals
from models.character import User
from models.character import Character
from models.log import Log
from utils import T

class Session(Document):
    parent_id = StringField()
    name = StringField(required=True)
    guild = StringField(required=True)
    description = StringField()
    channel_id = StringField()
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
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, 'Session', changes, action)
            user = User().get_by_id(document.updated_by)
            if user.history_id:
                user.history_id = None
                user.updated_by = document.updated_by
                user.updated = document.updated
                user.save()
            print(changes)

    @staticmethod
    def query():
        return Session.objects

    @staticmethod
    def filter(**params):
        return Session.objects.filter(**params)

    def create_new(self, user, guild, channel_id, name, archived):
        self.name = name
        self.guild = guild
        self.channel_id = channel_id
        self.created_by = str(user.id)
        self.created = T.now()
        self.updated_by = str(user.id)
        self.updated = T.now()
        self.save()
        return self

    def find(self, guild, channel_id, name, archived=False):
        filter = Session.objects(guild=guild, channel_id=channel_id, name__icontains=name, archived=archived)
        session = filter.first()
        return session

    def get_or_create(self, user, guild, channel, name, archived=False):
        session = self.find(guild, str(channel.id), name, archived)
        if session is None:
            session = self.create_new(user, guild, str(channel.id), name, archived)
            session.character = Character().get_or_create(user, name, guild, session, 'Session', archived)
            session.save()
        return session

    def get_by_id(self, id):
        session = Session.objects(id=id).first()
        return session

    @classmethod
    def get_by_channel(cls, channel, archived=False, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * page_size
            items = cls.filter(channel_id=str(channel.id), archived=archived).skip(offset).limit(page_size).all()
        else:
            items = cls.filter(channel_id=str(channel.id), archived=archived).order_by('name', 'created').all()
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
            self.reverse_archive(self.user)
            self.archived = True
            self.updated_by = str(user.id)
            self.updated = T.now()
            self.save()

    def reverse_archive(self, user):
        for s in Session().get_by_parent(parent_id=str(self.id)):
            s.reverse_archive(self.user)
            s.archived = True
            s.updated_by = str(user.id)
            s.updated = T.now()
            s.save()

    def restore(self, user):
            self.reverse_restore(self.user)
            self.archived = False
            self.updated_by = str(user.id)
            self.updated = T.now()
            self.save()

    def reverse_restore(self, user):
        for s in Session().get_by_parent(parent_id=str(self.id)):
            s.reverse_restore(self.user)
            s.archived = False
            s.updated_by = str(user.id)
            s.updated = T.now()
            s.save()

    def get_string_characters(self, user=None):
        characters = '\n                '.join(f'***{c.name}***' + (' _(Active Character)_' if str(c.id) == user.active_character else '') for c in Character.filter(id__in=[ObjectId(id) for id in self.characters]) if c)
        return f'\n\n            _Characters:_\n                {characters}'

    def get_string(self, channel=None, user=None):
        if user and not user.time_zone:
            raise Exception('No time zone defined```css\n.d user timezone New_York```')
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Session)_ ' if str(self.id) == channel.active_session else ''
        start = ''
        if self.started_on:
            start = f'\n_Started On:_ ***{T.to(self.started_on, user)}***' if self.started_on else ''
        end = ''
        if self.ended_on:
            end = f'\n_Ended On:_ ***{T.to(self.ended_on, user)}***' if self.ended_on else ''
        description = f' - "{self.description}"' if self.description else ''
        characters = f'{self.get_string_characters(user)}' if self.characters else ''
        if self.character:
            name = f'***{self.character.name}***' if self.character.name else name
            description = f' - "{self.character.description}"' if self.character.description else description
        return f'        {name}{active}{start}{end}{description}{characters}'

    def get_short_string(self, channel=None):
        name = f'***{self.name}***'
        active = ''
        if channel:
            active = ' _(Active Session)_ ' if str(self.id) == channel.active_session else ''
        return f'        {name}{active}'


signals.post_save.connect(Session.post_save, sender=Session)
        