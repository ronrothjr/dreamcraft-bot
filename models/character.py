# character.py
import datetime
from mongoengine import *
from mongoengine import signals
from bson.objectid import ObjectId

from models.user import User
from config.setup import Setup
from models.log import Log
from utils.text_utils import TextUtils

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
    use_approaches = BooleanField()
    fate_points = IntField()
    refresh = IntField()
    last_roll = DynamicField()
    stress = DynamicField()
    stress_titles = ListField()
    consequences = DynamicField()
    consequences_titles = ListField()
    consequences_shifts = ListField()
    image_url = StringField()
    is_boost = BooleanField()
    has_stress = BooleanField()
    custom_properties = DynamicField()
    archived = BooleanField(default=False)
    history_id = StringField()
    created_by = StringField()
    created = DateTimeField(required=True)
    updated_by = StringField()
    updated = DateTimeField(required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated = datetime.datetime.utcnow()

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
            changes = {}
            for c in document._delta()[0]:
                changes[c.replace('.', '__')] = document._delta()[0][c]
            action = 'updated'
            if 'created' in kwargs:
                action = 'created' if kwargs['created'] else action
            if action == 'updated' and 'archived' in changes:
                action = 'archived' if changes['archived'] else 'restored'
            Log().create_new(str(document.id), document.name, document.updated_by, document.guild, document.category, changes, action)
            user = User().get_by_id(document.updated_by)
            if user.history_id:
                user.history_id = None
                user.updated_by = document.updated_by
                user.updated = document.updated
                user.save()
            print(changes)

    @staticmethod
    def query():
        return Character.objects

    @staticmethod
    def filter(**params):
        return Character.objects.filter(**params)

    @classmethod
    def find(cls, user, name, guild, parent=None, category='', archived=False):
        params = {}
        if user:
            params.update(user=user.id)
        if name:
            params.update(name__icontains=name)
        if guild:
            params.update(guild=guild)
        if parent:
            params.update(parent_id=str(parent.id))
        if category:
            params.update(category=category)
        params.update(archived=archived)
        character = cls.filter(**params).first()
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
    def get_by_page(cls, params, page_num=1, page_size=5):
        if page_num:
            offset = (page_num - 1) * 5
            logs = cls.filter(**params).order_by('name', 'created').skip(offset).limit(page_size).all()
        else:
            logs = cls.filter(**params).order_by('name', 'created').all()
        return logs

    @classmethod
    def get_by_parent(cls, parent, name='', category=''):
        characters = []
        params = {}
        if parent:
            params.update(parent_id=str(parent.id))
        if name:
            params.update(name__icontains=name)
        if category:
            params.update(category=category)
        if name:
            character = cls.filter(**params).first()
            characters = [character] if character else []
        else:
            characters = cls.filter(**params).all()
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
        self.created_by = str(user.id)
        self.created = datetime.datetime.utcnow()
        self.updated_by = str(user.id)
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def get_or_create(self, user, name, guild, parent=None, category='Character', archived=False):
        character = self.find(user, name, guild, parent, category, archived)
        if character is None:
            character = self.create_new(user, name, guild, str(parent.id) if parent else None, category, archived)
        return character

    def archive(self, user):
            self.reverse_archive(self.user)
            self.archived = True
            self.updated_by = str(user.id)
            self.updated = datetime.datetime.utcnow()
            self.save()

    def reverse_archive(self, user):
        for c in Character().get_by_parent(self):
            c.reverse_archive(self.user)
            c.archived = True
            c.updated_by = str(user.id)
            c.updated = datetime.datetime.utcnow()
            c.save()

    def reverse(self, user):
            self.reverse_restore(self.user)
            self.archived = False
            self.updated_by = str(user.id)
            self.updated = datetime.datetime.utcnow()
            self.save()

    def reverse_restore(self, user):
        for c in Character().get_by_parent(self):
            c.reverse_restore(self.user)
            c.archived = False
            c.updated_by = str(user.id)
            c.updated = datetime.datetime.utcnow()
            c.save()

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
        refresh = f' (_Refresh:_ {self.refresh})' if self.refresh else ''
        return f'{self.sep()}**Fate Points:** {self.fate_points}{refresh}' if self.fate_points is not None else ''

    def get_string_custom(self):
        custom = []
        if self.custom_properties:
            for cp in self.custom_properties:
                display_name = self.custom_properties[cp]['display_name']
                property_value = self.custom_properties[cp]['property_value']
                custom.append(f'**{display_name}:** {property_value}')
        return self.sep() + self.sep().join([c for c in custom]) if self.custom_properties else ''

    def get_invokable_objects(self, char=None):
        char = char if char else self
        available = []
        if char.high_concept or char.trouble:
            available.append({'char': char, 'parent': char})
        children = Character().get_by_parent(char, '', '')
        for child in children:
            if child.category in ['Aspect', 'Stunt']:
                available.append({'char': child, 'parent': char})
                available.extend(self.get_invokable_objects(child))
        return available

    def get_character_aspects(self, char=None):
        char = char if char else self
        available = self.get_invokable_objects(char)
        aspects_strings = []
        for obj in available:
            if obj['char'].high_concept:
                name = TextUtils.clean(obj['char'].name)
                high_concept = TextUtils.clean(obj['char'].high_concept)
                aspects_strings.append(f'***{high_concept}*** (High Concept of _\'{name}\'_)')
            if obj['char'].trouble:
                name = TextUtils.clean(obj['char'].name)
                trouble = TextUtils.clean(obj['char'].trouble)
                aspects_strings.append(f'***{trouble}*** (Trouble of _\'{name}\'_)')
            if obj.category in ['Aspect','Stunt']:
                name = TextUtils.clean(obj['char'].name)
                category = TextUtils.clean(obj['char'].category)
                parent = TextUtils.clean(obj['parent'].name)
                aspects_strings.append(f'***{name}*** ({category} of _\'{parent}\'_)')
        return aspects_strings

    def get_available_aspects(self, parent=None):
        available = []
        if self.high_concept:
            available.append(f'***{TextUtils.clean(self.high_concept)}*** (High Concept of _\'{self.name}\'_)')
        if self.trouble:
            available.append(f'***{TextUtils.clean(self.trouble)}*** (Trouble of _\'{self.name}\'_)')
        if self.category in ['Aspect', 'Stunt']:
            parent_string = f' of ***{parent.name}***' if parent else ''
            available.append(f'***{TextUtils.clean(self.name)}*** ({self.category}{parent_string})')
        return available

    def get_string_aspects(self, user=None):
        aspects = Character().get_by_parent(self, '', 'Aspect')
        aspects_string = self.sep().join([a.get_string(user) for a in aspects]) if aspects else ''
        return f'{self.nl()}{self.nl()}**Aspects:**{self.sep()}{aspects_string}' if aspects_string else ''

    def get_string_stunts(self, user=None):
        stunts = Character().get_by_parent(self, '', 'Stunt')
        stunts_string = self.sep().join([s.get_string(self) for s in stunts]) if stunts else ''
        return f'{self.nl()}{self.nl()}**Stunts:**{self.sep()}{stunts_string}' if stunts_string else ''

    def get_string_skills(self):
        title = 'Approaches' if self.use_approaches else 'Skills'
        skills_string = self.sep().join([f'{self.skills[key]} - {key}' for key in self.skills])
        return f'{self.sep()}{self.sep()}**{title}:**{self.sep()}{skills_string}' if skills_string else ''

    def get_string_stress(self):
        stress_name = '**_Stress:_** '
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
        return f'{self.nl()}{self.nl()}{stress_name}{stress_string}' if stress_string else ''

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
        return f'{self.nl()}{self.nl()}{consequences_name}{self.sep()}{consequences_string}' if consequences_string else ''

    def get_string(self, user=None):
        archived = '```css\nARCHIVED```' if self.archived else ''
        name = self.get_string_name(user)
        fate_points = self.get_string_fate()
        description = f'{self.sep()}"{self.description}"' if self.description else ''
        high_concept = f'{self.sep()}**High Concept:** {self.high_concept}' if self.high_concept else ''
        trouble = f'{self.sep()}**Trouble:** {self.trouble}' if self.trouble else ''
        custom = self.get_string_custom()
        aspects = self.get_string_aspects(user)
        stunts = self.get_string_stunts(user)
        skills = self.get_string_skills()
        stress = self.get_string_stress()
        consequenses = self.get_string_consequences()
        image = f'!image{self.image_url}!image' if self.image_url else ''
        return f'{archived}{name}{description}{high_concept}{trouble}{fate_points}{custom}{skills}{stress}{aspects}{stunts}{consequenses}{image}'

    def get_short_string(self, user=None):
        archived = '```css\nARCHIVED```' if self.archived else ''
        name = self.get_string_name(user)
        fate_points = self.get_string_fate()
        description = f'{self.nl()}"{self.description}"' if self.description else ''
        high_concept = f'{self.nl()}**High Concept:** {self.high_concept}' if self.high_concept else ''
        trouble = f'{self.nl()}**Trouble:** {self.trouble}' if self.trouble else ''
        return f'{archived}{name}{description}{high_concept}{trouble}{fate_points}'

    def get_guilds(self, options={}):
        pipeline = []
        match = {}
        if 'guild' in options and options['guild'] and len(options['guild']) > 0:
            match.update(guild={"$in":options['guild']})
        if 'user' in options and options['user'] and len(options['user']) > 0:
            match.update(user={"$in":options['user']})
        if match:
            pipeline.append({"$match": match})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}}})
        pipeline.append({"$project": {"guild": "$_id.guild"}})
        pipeline.append({"$sort": {"guild": 1}})
        guilds = list(Character.objects.aggregate(*pipeline))
        return guilds

    def get_stats(self, guild):
        guild = '' if guild.lower() == 'all' else guild

        pipeline = []
        if guild:
            pipeline.append({"$match": {"guild": guild}})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}}})
        pipeline.append({"$project": {"guild": "$_id.guild"}})
        pipeline.append({"$sort": {"guild": 1}})
        guilds = list(Character.objects.aggregate(*pipeline))

        pipeline = []
        pipeline.append({"$match": {'category': {"$in":['Scenario']}}})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}, "total": {"$sum": 1}}})
        pipeline.append({"$project": {"guild": "$_id.guild", "total": "$total"}})
        pipeline.append({"$sort": {"guild": 1, "total": 1}})
        scenarios_per_guild = list(Character.objects.aggregate(*pipeline))

        pipeline = []
        pipeline.append({"$match": {'category': {"$in":['Scene']}}})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}, "total": {"$sum": 1}}})
        pipeline.append({"$project": {"guild": "$_id.guild", "total": "$total"}})
        pipeline.append({"$sort": {"guild": 1, "total": 1}})
        scenes_per_guild = list(Character.objects.aggregate(*pipeline))

        pipeline = []
        pipeline.append({"$match": {'category': {"$in":['Zone']}}})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}, "total": {"$sum": 1}}})
        pipeline.append({"$project": {"guild": "$_id.guild", "total": "$total"}})
        pipeline.append({"$sort": {"guild": 1, "total": 1}})
        zones_per_guild = list(Character.objects.aggregate(*pipeline))

        pipeline = []
        pipeline.append({"$match": {'category': {"$in":['Character']}}})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}, "total": {"$sum": 1}}})
        pipeline.append({"$project": {"guild": "$_id.guild", "total": "$total"}})
        pipeline.append({"$sort": {"guild": 1, "total": 1}})
        characters_per_guild = list(Character.objects.aggregate(*pipeline))

        pipeline = []
        pipeline.append({"$match": {'category': {"$in":['Aspect']}}})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}, "total": {"$sum": 1}}})
        pipeline.append({"$project": {"guild": "$_id.guild", "total": "$total"}})
        pipeline.append({"$sort": {"guild": 1, "total": 1}})
        aspects_per_guild = list(Character.objects.aggregate(*pipeline))

        pipeline = []
        pipeline.append({"$match": {'category': {"$in":['Stunt']}}})
        pipeline.append({ "$group": {"_id": {"guild": "$guild"}, "total": {"$sum": 1}}})
        pipeline.append({"$project": {"guild": "$_id.guild", "total": "$total"}})
        pipeline.append({"$sort": {"guild": 1, "total": 1}})
        stunts_per_guild = list(Character.objects.aggregate(*pipeline))

        totals = {}
        for g in guilds:
            if g['guild']:
                guild = g['guild']
                totals[guild] = {
                    'Scenarios': next((c['total'] for c in scenarios_per_guild if guild == c['guild']), 0),
                    'Scenes': next((c['total'] for c in scenes_per_guild if guild == c['guild']), 0),
                    'Zones': next((c['total'] for c in zones_per_guild if guild == c['guild']), 0),
                    'Characters': next((c['total'] for c in characters_per_guild if guild == c['guild']), 0),
                    'Aspects': next((c['total'] for c in aspects_per_guild if guild == c['guild']), 0),
                    'Stunts': next((c['total'] for c in stunts_per_guild if guild == c['guild']), 0),
                }
        return totals


signals.pre_save.connect(Character.pre_save, sender=Character)
signals.post_save.connect(Character.post_save, sender=Character)