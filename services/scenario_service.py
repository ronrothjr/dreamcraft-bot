# scenario_service.py
import traceback
import datetime
import copy
from bson.objectid import ObjectId
from models import User, Channel, Scenario
from config.setup import Setup
from utils import TextUtils, Dialog

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

    def get_parent_by_id(self, method, user, parent_id):
        parent = method(id=ObjectId(parent_id)).first()
        if parent:
            user.active_character = str(parent.id)
            self.save_user(user)
            return [parent.get_string(user)] if parent.get_string else f'***{parent.name}*** selected as Active Scenario'
        return ['No parent found']

    def get_scenario_info(self, scenario, user):
        name = scenario.name if scenario else 'your scenario'
        get_string = scenario.get_string(user) if scenario else ''
        get_short_string = scenario.get_short_string(user) if scenario else ''
        return scenario.character, name, get_string, get_short_string
