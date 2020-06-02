# scene_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import copy
from bson.objectid import ObjectId
from models import User, Scenario, Scene, Character, Channel
from config.setup import Setup
from utils import TextUtils, T
from services.base_service import BaseService

class SceneService(BaseService):

    def player(self, args, channel, sc, user):
        messages = []
        if len(args) == 1:
            raise Exception('No characters added')
        if not sc:
            raise Exception('You don\'t have an active scene. Try this:```css\n.d scene SCENE_NAME```')
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [sc.get_string_characters(channel)]
        elif args[1].lower() in ['delete','d']:
            for char_name in args[2:]:
                char = Character().find(user=user, name=char_name, guild=channel.guild, category='Character')
                [sc.characters.remove(s) for s in sc.characters if char and str(char.id) == s]
                messages.append(f'\n***{char.name}*** removed from _{sc.name}_' if char else f'**{char_name}** was not found')
            self.save(sc, user)
            messages.append(sc.get_string_characters(user))
            return messages
        else:
            for char_name in args[1:]:
                char = Character().find(None, char_name, channel.guild)
                if char:
                    if str(char.id) in sc.characters:
                        messages.append(f'***{char.name}*** is already in _{sc.name}_')
                    else:
                        sc.characters.append(str(char.id))
                        messages.append(f'\nAdded ***{char.name}*** to _{sc.name}_ scene')
                else:
                    messages.append(f'***{char_name}*** not found. No character added to _{sc.name}_')
            self.save(sc, user)
            messages.append(sc.get_string_characters(user))
            return messages

    def delete_scene(self, args, guild, channel, scenario, sc, user):
        messages = []
        search = ''
        if len(args) == 1:
            if not sc:
                raise Exception('No scene provided for deletion')
        else:
            search = ' '.join(args[1:])
            sc = Scene().find(guild.name, str(channel.id), str(scenario.id), search)
        if not sc:
            return [f'{search} was not found. No changes made.']
        else:
            search = str(sc.name)
            scenario_id = str(sc.scenario_id) if sc.scenario_id else ''
            channel_id = str(sc.channel_id) if sc.channel_id else ''
            sc.character.archive(user)
            sc.archived = True
            sc.updated_by = str(user.id)
            sc.updated = T.now()
            sc.save()
            messages.append(f'***{search}*** removed')
            if scenario_id:
                secenario = Scenario().get_by_id(scenario_id)
                messages.append(secenario.get_string(channel))
            elif channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages