# scene_service.py
import traceback
import datetime
import copy
from bson.objectid import ObjectId
from models import User, Zone
from config.setup import Setup
from utils.text_utils import TextUtils

class ZoneService():
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
            if (not item.created):
                item.created = datetime.datetime.utcnow()
            item.updated_by = str(user.id)
            item.updated = datetime.datetime.utcnow()
            item.history_id = ''
            item.save()

    def save_user(self, user):
        if user:
            if (not user.created):
                user.created = datetime.datetime.utcnow()
            user.updated_by = str(user.id)
            user.updated = datetime.datetime.utcnow()
            user.save()

    def get_parent_by_id(self, char, user, parent_id):
        parent = Zone.filter(id=ObjectId(parent_id)).first()
        if parent:
            user.active_character = str(parent.id)
            self.save_user(user)
            return [parent.get_string(user)] if parent.get_string else f'***{parent.name}*** selected as Active Zone'
        return ['No parent found']

    def get_zone_info(self, zone, user):
        name = zone.name if zone else 'your zone'
        get_string = zone.get_string(user) if zone else ''
        get_short_string = zone.get_short_string(user) if zone else ''
        return zone.character, name, get_string, get_short_string
