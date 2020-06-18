# scenario_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import copy
from bson.objectid import ObjectId
from models import User, Channel, Scenario, Scene, Character
from config.setup import Setup
from utils import TextUtils, Dialog, T
from services.base_service import BaseService

class ScenarioService(BaseService):

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

    def player(self, args, channel, scenario, user):
        if len(args) == 1:
            return ['No characters added']
        if not scenario:
            return ['You don\'t have an active scenario.\nTry this: ```css\n.d new scenario "Scenario Name"```']
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [scenario.get_string_characters(channel)]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            char = ' '.join(args[2:])
            [scenario.characters.remove(s) for s in scenario.characters if char.lower() in s.lower()]
            self.save(scenario, user)
            return [
                f'{char} removed from scenario characters',
                scenario.get_string_characters(channel)
            ]
        else:
            search = ' '.join(args[1:])
            char = Character().find(None, search, channel.guild)
            if char:
                scenario.characters.append(str(char.id))
            else:
                return [f'***{search}*** not found. No character added to _{scenario.name}_']
            self.save(scenario, user)
            return [
                f'Added {char.name} to scenario characters',
                scenario.get_string_characters(channel)
            ]
