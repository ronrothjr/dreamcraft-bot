# base_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import copy
from bson.objectid import ObjectId
from models import User, Channel, Log
from config.setup import Setup
from utils import TextUtils, Dialog, T

class BaseService():
    """Servcie class for handling common methods for view, save, and update of database models"""

    def log(self, parent_id, name, user_id, guild, category, data, action):
        """Create log entry
        
        Parameters
        ----------
        parent_id : str
            The id of the record being edited
        name : str
            The name of the record being edited
        user_id : str
            The user id performing the action
        guild : str
            The guild name (or private channel name)
        category : str
            The kind of object being edited
        data : dict
            The data for the log entry
        action : str
            The action being performed: created or updated
        """

        # Log every comand
        Log().create_new(parent_id, name, user_id, guild, category, data, action)

    def search(self, args, method, params):
        """Search for an item using a provided method and params

        Parameters
        ----------
        args : list(str)
            List of strings with subcommands
        method : function
            The mongoengine Document method for filtering an item
        params : dict
            The dictionary of params to search for an item

        Returns
        -------
        item - mongoengine Document
        """

        if len(args) == 0:
            return None
        item = method(**params).first()
        if item:
            return item
        else:
            return None

    def save(self, item, user):
        """Save an item

        Parameters
        ----------
        item : mongoengine.Document
            The item to save
        user : User
            The user to save as the updated_by
        """

        if item:
            item.updated_by = str(user.id)
            item.updated = T.now()
            item.history_id = ''
            item.save()

    def save_user(self, user):
        """Save a User Document

        Parameters
        ----------
        user : User
            The User mongoengine Document for saving
        """

        if user:
            user.updated_by = str(user.id)
            user.updated = T.now()
            user.save()

    def get_parent_by_id(self, method, user, parent_id):
        """Set the parent as the active item

        Parameters
        ----------
        method : function
            The mongoengine Document method for filtering an item
        user : User
            The User mongoengine Document for saving
        parent_id : str
            The ObjectId string value for the parent of the item
        
        Returns
        -------
        list(str) - the array of response strings
        """

        parent = method(id=ObjectId(parent_id)).first()
        if parent:
            user.active_character = str(parent.id)
            self.save_user(user)
            return [parent.get_string(user)] if parent.get_string else f'***{parent.name}*** selected as Active'
        return ['No parent found']

    def get_info(self, type_name, item, user, param=None):
        """Get item string information for display

        Parameters
        ----------
        type_name : str
            The string name of the item
        item : mongoengine.Document
            The item used to get string information
        user : User
            The User mongoengine Document for displaying active records
        param : object
            The additaional param for dislaying item information

        Returns
        -------
        tuple(mongoengine.Document, str, str, str)
            item : mongoengine.Document
                The item used to get string information
            name : str
                The name value of the item
            get_string : str
                The long display string of the item
            get_short_string : str
                The short display string of the item
        """

        name = item.name if item else f'your {type_name}'
        if param:
            get_string = item.get_string(user, param) if item else ''
        else:
            get_string = item.get_string(user) if item else ''
        get_short_string = item.get_short_string(user) if item else ''
        return item if item else None, name, get_string, get_short_string

    def delete_item(self, args, user, item, method, params):
        """Delete an item

        Parameters
        ----------
        args : list(str)
            List of strings with subcommands
        user : User
            The User mongoengine Document for displaying active records
        item : mongoengine.Document
            The item used to get string information
        method : function
            The mongoengine Document method for filtering an item
        params : dict
            The dictionary of params to search for an item

        Returns
        -------
        list(str) - the array of response strings
        """

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
            if hasattr(item, 'character'):
                item.character.archive(user)
            item.archived = True
            self.save(item, user)
            messages.append(f'***{search}*** removed')
            if channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages