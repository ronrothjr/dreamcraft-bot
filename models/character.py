# character.py
import datetime
from mongoengine import *
from bson.objectid import ObjectId

from models.user import User
from models.stunt import Stunt
from config.setup import Setup

SETUP = Setup()
X = SETUP.x
O = SETUP.o
STRESS = SETUP.stress
STRESS_TITLES = SETUP.stress_titles
CONSEQUENCES = SETUP.consequences
CONSEQUENCES_TITLES = SETUP.consequences_titles
CONSEQUENCES_SHIFTS = SETUP.consequence_shifts

class Character(Document):
    name = StringField(required=True)
    guild = StringField(required=True)
    user = LazyReferenceField(User)
    parent_id = StringField()
    active_character = StringField()
    characters = ListField(StringField())
    category = StringField()
    description = StringField()
    high_concept = StringField()
    trouble = StringField()
    active_stunt = StringField()
    active_aspect = StringField()
    skills = DictField()
    stunts = ListField(StringField())
    use_approaches = BooleanField()
    fate_points = IntField()
    refresh = IntField()
    last_roll = DynamicField()
    stress = DynamicField()
    stress_titles = ListField()
    consequences = DynamicField()
    consequences_titles = ListField()
    consequences_shifts = ListField()
    is_boost = BooleanField()
    has_stress = BooleanField()
    archived = BooleanField(default=False)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    @staticmethod
    def query():
        return Character.objects

    @staticmethod
    def filter(**params):
        return Character.objects.filter(**params)

    @classmethod
    def find(cls, user, name, guild, parent, category, archived):
        if parent:
            character = cls.filter(user=user.id, name__icontains=name, guild=guild, parent_id=str(parent.id), category=category, archived=archived).first()
        else:
            character = cls.filter(user=user.id, name__icontains=name, guild=guild, category=category, archived=archived).first()
        return character

    @classmethod
    def get_by_id(cls, id):
        character = cls.filter(id=ObjectId(id)).first()
        return character

    @classmethod
    def get_by_user(cls, user):
        characters = cls.filter(user=user.id).all()
        return characters

    @classmethod
    def get_by_parent(cls, parent, name='', category=''):
        characters = []
        if name:
            character = cls.filter(parent_id=str(parent.id), name__icontains=name, category=category).first()
            characters = [character] if character else []
        else:
            characters = cls.filter(parent_id=str(parent.id), category=category).all()
        return characters

    def create_new(self, user, name, guild, parent_id, category, archived):
        self.user = user
        self.name = name
        self.guild = guild
        self.category = category
        if category == 'Character':
            self.refresh = 3
            self.fate_points = 3
            self.stress = STRESS
            self.consequences = CONSEQUENCES
        if parent_id:
            self.parent_id = parent_id
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def get_or_create(self, user, name, guild, parent=None, category='Character', archived=False):
        character = self.find(user, name, guild, parent, category, archived)
        if character is None:
            character = self.create_new(user, name, guild, str(parent.id) if parent else None, category, archived)
        return character

    def reverse_delete(self):
        for c in Character().get_by_parent(self):
            c.reverse_delete()
            c.delete()

    def get_string_name(self, user=None):
        active = ''
        category = f' _({self.category})_ ' if self.category else ''
        if user and str(self.id) == user.active_character:
            active = f' _(Active)_ '
        return f'***{self.name}***{active}{category}'

    def nl(self):
        return '\n' if self.category == 'Character' else '    '

    def sep(self):
        return '\n        ' if self.category == 'Character' else '    '

    def get_string_fate(self):
        return f'{self.nl()}**Fate Points:** {self.fate_points} (_Refresh:_ {self.refresh})' if self.fate_points is not None else ''

    def get_string_aspects(self, user=None):
        aspects = Character().get_by_parent(self, '', 'Aspect')
        aspects_string = self.sep().join([a.get_string(user) for a in aspects]) if aspects else ''
        return f'{self.nl()}**Aspects:**{self.sep()}{aspects_string}' if aspects_string else ''

    def get_string_stunts(self, user=None):
        stunts = Character().get_by_parent(self, '', 'Stunt')
        stunts_string = self.sep().join([s.get_string(self) for s in stunts]) if stunts else ''
        return f'{self.sep()}**Stunts:**{self.sep()}{stunts_string}' if stunts_string else ''

    def get_string_skills(self):
        title = 'Approaches' if self.use_approaches else 'Skills'
        skills_string = self.sep().join([f'{key}: {self.skills[key]}' for key in self.skills])
        return f'{self.sep()}**{title}:**{self.sep()}{skills_string}' if skills_string else ''

    def get_string_stress(self):
        stress_name = '**_Stress_** '
        stress_string = ''
        if self.stress:
            if self.stress_titles and len(self.stress_titles) == 1:
                stress_name = f'**_{self.stress_titles[0]}_** '
                stress = '  '.join([self.stress[0][s][1] for s in range(0, len(self.stress[0]))])
                stress_string = f' {stress}'
            else:
                stress = [f'_{s}:_ ' for s in self.stress_titles] if self.stress_titles else ['_Physical:_ ', '_Mental:_   ']
                for t in range(0, len(self.stress)):
                    for s in range(0, len(self.stress[t])):
                        stress[t] += f' {self.stress[t][s][1]}'
                stress_string = self.sep() + self.sep().join(stress)
        return f'{self.nl()}{stress_name}{stress_string}' if stress_string else ''

    def get_string_consequences(self):
        consequences_name = '**_Consequences:_** '
        consequences_string = ''
        if self.consequences:
            consequences_name = '**_Conditions:_** ' if self.consequences_titles else consequences_name
            consequences = [f'_{t}_ ' for t in self.consequences_titles] if self.consequences_titles else ['_Mild:_           ', '_Moderate:_ ', '_Severe:_       ']
            consequences_strings = []
            for c in range(0, len(self.consequences)):
                check = ' '+ self.consequences[c][1]
                description = f' - {self.consequences[c][2]}' if self.consequences[c][1] and len(self.consequences[c]) == 3 else ''
                consequences_strings.append(f'{check} _{self.consequences[c][0]}_ {consequences[c]}{description}')
            consequences_string = self.sep().join([c for c in consequences_strings])
        return f'{self.nl()}{consequences_name}{self.sep()}{consequences_string}' if consequences_string else ''

    def get_string(self, user=None):
        name = self.get_string_name(user)
        fate_points = self.get_string_fate()
        description = f'{self.sep()}"{self.description}"' if self.description else ''
        high_concept = f'{self.sep()}**High Concept:** {self.high_concept}' if self.high_concept else ''
        trouble = f'{self.sep()}**Trouble:** {self.trouble}' if self.trouble else ''
        aspects = self.get_string_aspects(user)
        stunts = self.get_string_stunts(user)
        skills = self.get_string_skills()
        stress = self.get_string_stress()
        consequenses = self.get_string_consequences()
        return f'{name}{description}{high_concept}{trouble}{fate_points}{skills}{stress}{aspects}{stunts}{consequenses}'

    def get_short_string(self, user=None):
        name = self.get_string_name(user)
        fate_points = self.get_string_fate(user)
        description = f'{self.nl()}"{self.description}"' if self.description else ''
        high_concept = f'{self.nl()}**High Concept:** {self.high_concept}' if self.high_concept else ''
        trouble = f'{self.nl()}**Trouble:** {self.trouble}' if self.trouble else ''
        return f'{name}{description}{high_concept}{trouble}{fate_points}'