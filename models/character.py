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
    stress = DynamicField()
    consequences = DynamicField()
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    def create_new(self, user, name, guild):
        self.user = user
        self.name = name
        self.guild = guild
        self.refresh = 3
        self.fate_points = 3
        self.stress = [[['1', ''],['1', ''],['1', '']],[['1', ''],['1', ''],['1', '']]]
        self.consequences = [['2', ''],['4', ''],['6', '']]
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

    def get_string_name(self, user):
        active = ''
        if str(self.id) == user.active_character:
            active = ' _(Active)_'
        return f'***{self.name}***{active}'

    def get_string_fate(self, user):
        return f'\n**Fate Points:** {self.fate_points} (_Refresh:_ {self.refresh})'
        
    def get_string_aspects(self):
        aspects = Aspect().get_by_parent_id(self.id)
        aspects_string = '\n        '.join([a.get_string() for a in aspects]) if aspects else '_None_'
        return f'\n**Aspects:**\n        {aspects_string}'

    def get_string_stunts(self):
        return f'\n**Stunts:**\n        ' + ('\n        '.join(self.stunts))

    def get_string_skills(self):
        title = 'Approaches' if self.use_approaches else 'Skills'
        return f'\n**{title}:**\n        ' + ('\n        '.join([f'{key}: {self.skills[key]}' for key in self.skills]))

    def get_string_stress(self):
        stress = ['_Physical:_ ', '_Mental:_   ']
        for t in range(0, len(self.stress)):
            for s in range(0, len(self.stress[t])):
                stress[t] += ' [X]' if self.stress[t][s][1] else ' [   ]'
        return f'\n**Stress:**\n        ' + ('\n        '.join(stress))

    def get_string_consequenses(self):
        consequences = ['_Mild:_           ', '_Moderate:_ ', '_Severe:_       ']
        for c in range(0, len(self.consequences)):
            check = ' [X]' if self.consequences[c][1] else ' [   ]'
            description = ''
            if self.consequences[c][1] and len(self.consequences[c]) == 3:
                description = f' - {self.consequences[c][2]}'
            consequences[c] += f'_{self.consequences[c][0]}_ {check}{description}'
        return f'\n**Consequences:**\n        ' + ('\n        '.join([c for c in consequences]))

    def get_string(self, user):
        name = self.get_string_name(user)
        fate_points = f'\n**Fate Points:** {self.fate_points} (_Refresh:_ {self.refresh})'
        description = f'\n"{self.description}"' if self.description else ''
        high_concept = f'\n**High Concept:** {self.high_concept}' if self.high_concept else ''
        trouble = f'\n**Trouble:** {self.trouble}' if self.trouble else ''
        aspects = f'{self.get_string_aspects()}'
        stunts = f'{self.get_string_stunts()}' if self.stunts else ''
        skills = f'{self.get_string_skills()}' if self.skills else ''
        stress = self.get_string_stress()
        consequenses = self.get_string_consequenses()
        return f'{name}{description}{high_concept}{trouble}{fate_points}{skills}{aspects}{stunts}{stress}{consequenses}'

    def get_short_string(self, user):
        name = self.get_string_name(user)
        if str(self.id) == user.active_character:
            active = ' _(Active)_'
        fate_points = self.get_string_fate(user)
        description = f'\n"{self.description}"' if self.description else ''
        high_concept = f'\n**High Concept:** {self.high_concept}' if self.high_concept else ''
        trouble = f'\n**Trouble:** {self.trouble}' if self.trouble else ''
        return f'{name}{active}{description}{high_concept}{trouble}{fate_points}'