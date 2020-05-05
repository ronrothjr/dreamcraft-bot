# character.py
import datetime
from mongoengine import *

from models.user import User
from models.aspect import Aspect

class Character(Document):
    user = ReferenceField(User)
    name = StringField(required=True)
    guild = StringField(required=True)
    description = StringField()
    high_concept = StringField()
    trouble = StringField()
    stunts = ListField(StringField())
    active_stunt = StringField()
    skills = DictField()
    use_approaches = BooleanField()
    fate_points = IntField()
    refresh = IntField()
    last_roll = DynamicField()
    stress = DictField()
    consequences = DictField()
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    def create_new(self, user, name, guild):
        self.user = user
        self.name = name
        self.guild = guild
        self.refresh = 3
        self.fate_points = 3
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, user, name, guild):
        character = Character.objects(user=user.id, name__icontains=name, guild=guild).first()
        return character

    def get_or_create(self, user, name, guild):
        character = self.find(user, name, guild)
        if character is None:
            character = self.create_new(user, name, guild)
        return character

    def get_by_id(self, id):
        character = Character.objects(id=id).first()
        return character

    def get_by_user(self, user):
        characters = Character.objects(user=user.id).all()
        return characters

    def get_string_aspects(self):
        return f'**Aspects:**\n        ' + ('\n        '.join([a.get_string() for a in Aspect().get_by_parent_id(self.id)]))

    def get_string_stunts(self):
        return f'**Stunts:**\n        ' + ('\n        '.join(self.stunts))

    def get_string_skills(self):
        title = 'Approaches' if self.use_approaches else 'Skills'
        return f'**{title}:**\n        ' + ('\n        '.join([f'{key}: {self.skills[key]}' for key in self.skills]))

    def get_string(self, user):
        active = ''
        if str(self.id) == user.active_character:
            active = ' (Active)'
        fate_points = f'**Fate Points:** {self.fate_points} (_Refresh:_ {self.refresh})\n'
        description = ''
        if self.description:
            description = f'"{self.description}"\n'
        high_concept = ''
        if self.high_concept:
            high_concept = f'**High Concept:** {self.high_concept}\n'
        trouble = ''
        if self.trouble:
            trouble = f'**Trouble:** {self.trouble}\n'
        aspects = f'{self.get_string_aspects()}\n'
        stunts = ''
        if self.stunts:
            stunts = f'{self.get_string_stunts()}\n'
        skills = ''
        if self.skills:
            skills = f'{self.get_string_skills()}\n'
        return f'***{self.name}***_{active}_\n{description}{high_concept}{trouble}{fate_points}{skills}{aspects}{stunts}'

    def get_short_string(self, user):
        active = ''
        if str(self.id) == user.active_character:
            active = ' _(Active)_'
        fate_points = f'**Fate Points:** {self.fate_points} (Refresh: {self.refresh})\n'
        high_concept = ''
        if self.high_concept:
            high_concept = f'**High Concept:** {self.high_concept}\n'
        trouble = ''
        if self.trouble:
            trouble = f'**Trouble:** {self.trouble}\n'
        skills = ''
        if self.skills:
            skills = f'{self.get_string_skills()}\n'
        return f'***{self.name}***{active}\n{high_concept}{trouble}{fate_points}'