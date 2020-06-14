# zone_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import copy
from bson.objectid import ObjectId
from models import User, Channel, Character, Zone
from config.setup import Setup
from utils import TextUtils, T
from services.base_service import BaseService

class ZoneService(BaseService):

    def player(self, args, channel, zone, user):
        messages = []
        if len(args) == 1:
            raise Exception('No characters added')
        if not zone:
            raise Exception('You don\'t have an active zone. Try this:```css\n.d zone ZONE_NAME```')
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [zone.get_string_characters(channel)]
        elif args[1].lower() in ['delete','d']:
            for char_name in args[2:]:
                char = Character().find(user=user, name=char_name, guild=channel.guild, category='Character')
                [zone.characters.remove(s) for s in zone.characters if char and str(char.id) == s]
                messages.append(f'***{char.name}*** removed from _{zone.name}_' if char else f'**{char_name}** was not found')
            self.save(zone, user)
            messages.append(zone.get_string_characters(user))
            return messages
        else:
            for char_name in args[1:]:
                char = Character().find(user=None, name=char_name, guild=channel.guild, category='Character')
                if char:
                    if str(char.id) in zone.characters:
                        messages.append(f'***{char.name}*** is already in _{zone.name}_')
                    else:
                        zone.characters.append(str(char.id))
                        messages.append(f'Added ***{char.name}*** to _{zone.name}_ zone')
                else:
                    messages.append(f'***{char_name}*** not found. No character added to _{zone.name}_')
            self.save(zone, user)
            messages.append(zone.get_string_characters(user))
            return messages

    def delete_zone(self, args, guild, channel, scene, zone, user):
        messages = []
        search = ''
        if len(args) == 1:
            if not zone:
                raise Exception('No zone provided for deletion')
        else:
            search = ' '.join(args[1:])
            zone = Zone().find(guild.name, str(channel.id), str(scene.id), search)
        if not zone:
            return [f'{search} was not found. No changes made.']
        else:
            search = str(zone.name)
            channel_id = str(zone.channel_id) if zone.channel_id else ''
            zone.character.archive(user)
            zone.archived = True
            self.save(zone, user)
            messages.append(f'***{search}*** removed')
            if channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages
