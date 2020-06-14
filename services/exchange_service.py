# exchange_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import copy
from bson.objectid import ObjectId
from models import User, Channel, Character, Exchange
from config.setup import Setup
from utils import TextUtils, T
from services.base_service import BaseService

class ExchangeService(BaseService):

    def player(self, args, channel, exchange, user):
        messages = []
        if len(args) == 1:
            raise Exception('No characters added')
        if not exchange:
            raise Exception('You don\'t have an active exchange. Try this:```css\n.d exchange EXCHANGE_NAME```')
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [exchange.get_string_characters(channel)]
        elif args[1].lower() in ['delete','d']:
            for char_name in args[2:]:
                char = Character().find(user=user, name=char_name, guild=channel.guild, category='Character')
                [exchange.characters.remove(s) for s in exchange.characters if char and str(char.id) == s]
                messages.append(f'***{char.name}*** removed from _{exchange.name}_ characters' if char else f'**{char_name}** was not found')
            self.save(exchange, user)
            messages.append(exchange.get_string_characters(user))
            return messages
        else:
            for char_name in args[1:]:
                char = Character().find(user=None, name=char_name, guild=channel.guild, category='Character')
                if char:
                    if str(char.id) in exchange.characters:
                        messages.append(f'***{char.name}*** is already in _{exchange.name}_ characters')
                    else:
                        exchange.characters.append(str(char.id))
                        messages.append(f'Added ***{char.name}*** to _{exchange.name}_ exchange characters')
                else:
                    messages.append(f'***{char_name}*** not found. No character added to _{exchange.name}_ characters')
            self.save(exchange, user)
            messages.append(exchange.get_string_characters(user))
            return messages

    def oppose(self, args, channel, exchange, user):
        messages = []
        if len(args) == 1:
            raise Exception('No opposition added')
        if not exchange:
            raise Exception('You don\'t have an active exchange. Try this:```css\n.d exchange EXCHANGE_NAME```')
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [exchange.get_string_opposition(channel)]
        elif args[1].lower() in ['delete','d']:
            for char_name in args[2:]:
                char = Character().find(user=user, name=char_name, guild=channel.guild, category='Character')
                [exchange.opposition.remove(s) for s in exchange.opposition if char and str(char.id) == s]
                messages.append(f'***{char.name}*** removed from the opposition in _{exchange.name}_' if char else f'**{char_name}** was not found')
            self.save(exchange, user)
            messages.append(exchange.get_string_opposition(user))
            return messages
        else:
            for char_name in args[1:]:
                char = Character().find(user=None, name=char_name, guild=channel.guild, category='Character')
                if char:
                    if str(char.id) in exchange.opposition:
                        messages.append(f'***{char.name}*** is already in the opposition in the _{exchange.name}_ exchange')
                    else:
                        exchange.opposition.append(str(char.id))
                        messages.append(f'Added ***{char.name}*** to the opposition in the _{exchange.name}_ exchange')
                else:
                    messages.append(f'***{char_name}*** not found. No opposition added to _{exchange.name}_')
            self.save(exchange, user)
            messages.append(exchange.get_string_opposition(user))
            return messages
