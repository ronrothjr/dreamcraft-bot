# scene_service.py
import traceback
import copy
from bson.objectid import ObjectId
from models import User, Zone
from config.setup import Setup
from utils import TextUtils, T

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
            item.updated_by = str(user.id)
            item.updated = T.now()
            item.history_id = ''
            item.save()

    def save_user(self, user):
        if user:
            user.updated_by = str(user.id)
            user.updated = T.now()
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
