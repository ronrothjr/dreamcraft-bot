# base_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import copy
from bson.objectid import ObjectId
from models import User, Channel
from config.setup import Setup
from utils import TextUtils, Dialog, T

class BaseService():
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
            return [parent.get_string(user)] if parent.get_string else f'***{parent.name}*** selected as Active'
        return ['No parent found']

    def get_info(self, type_name, item, user, param=None):
        name = item.name if item else f'your {type_name}'
        if param:
            get_string = item.get_string(user, param) if item else ''
        else:
            get_string = item.get_string(user) if item else ''
        get_short_string = item.get_short_string(user) if item else ''
        return item if item else None, name, get_string, get_short_string

    def delete_item(self, args, guild, channel, user, item, method, params):
        messages = []
        search = ''
        if len(args) == 1:
            if not item:
                raise Exception('No item provided for deletion')
        else:
            search = ' '.join(args[1:])
            params['name'] = search
            item = method(**params)
        if not item:
            return [f'{search} was not found. No changes made.']
        else:
            search = str(item.name)
            channel_id = str(item.channel_id) if hasattr(item, 'channel_id') else ''
            item.character.archive(user)
            item.archived = True
            self.save(item, user)
            messages.append(f'***{search}*** removed')
            if channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages