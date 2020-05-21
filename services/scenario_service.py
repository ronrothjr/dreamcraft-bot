# scenario_service.py
import traceback
import copy
from bson.objectid import ObjectId
from models import User, Channel, Scenario, Scene, Character
from config.setup import Setup
from utils import TextUtils, Dialog, T

class ScenarioService():
    def search(self, args, method, params):
        if len(args) == 0:
            return None
        item = method(**params).first()
        if item:
            return item
        else:
            return None

    def save(self, item, user):
        if item:
            item.updated_by = str(user.id)
            item.updated = T.now()
            item.history_id = ''
            item.save()

    def save_user(self, user):
        if user:
            user.updated_by = str(user.id)
            user.updated = T.now()
            user.save()

    def get_parent_by_id(self, method, user, parent_id):
        parent = method(id=ObjectId(parent_id)).first()
        if parent:
            user.active_character = str(parent.id)
            self.save_user(user)
            return [parent.get_string(user)] if parent.get_string else f'***{parent.name}*** selected as Active Scenario'
        return ['No parent found']

    def get_scenario_info(self, scenario, channel, user=None):
        name = scenario.name if scenario else 'your scenario'
        get_string = self.get_string(scenario, channel) if scenario else ''
        get_short_string = scenario.get_short_string(channel) if scenario else ''
        return scenario.character if scenario else None, name, get_string, get_short_string

    def get_string(self, item, channel=None, user=None):
        name = f'***{item.name}***'
        active = ''
        if channel:
            active = ' _(Active Scenario)_ ' if str(item.id) == channel.active_scenario else ''
        description = f' - "{item.description}"' if item.description else ''
        scenes = self.get_scenes(item)
        scenes_str = self.get_scenes_str(scenes, channel)
        characters = self.get_string_characters(scenes, user)
        aspects = ''
        stress = ''
        if item.character:
            name = f'***{item.character.name}***' if item.character.name else name
            description = f' - "{item.character.description}"' if item.character.description else description
            aspects = item.character.get_string_aspects()
            stress = item.character.get_string_stress() if item.character.has_stress else ''
        return f'        {name}{active}{description}{scenes_str}{characters}{aspects}{stress}'

    def get_scenes(self, item):
        return list(Scene.get_by_scenario(scenario=item, page_num=0))

    def get_characters(self, scenes):
        scenario_characters = []
        [[scenario_characters.append(c) for c in Character.filter(id__in=[ObjectId(id) for id in s.characters]).all() if c not in scenario_characters] for s in scenes]
        return scenario_characters

    def get_scenes_str(self, scenes, channel):
        scenes_str = '\n                '.join([s.get_short_string(channel) for s in scenes if s] if scenes else '')
        return f'\n\n            _Scenes:_\n                {scenes_str}' if scenes_str else ''

    def get_string_characters(self, scenes, user):
        scenario_characters = []
        [[scenario_characters.append(c) for c in Character.filter(id__in=[ObjectId(id) for id in s.characters]).all() if c not in scenario_characters] for s in scenes]
        character_strings = [f'***{c.name}***' + (' _(Active Character)_' if user and user.active_character == str(c.id) else '') for c in scenario_characters if c]
        characters = '\n               '.join(character_strings)
        return f'\n\n            _Characters:_\n                {characters}' if scenes else ''
