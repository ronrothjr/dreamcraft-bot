# character_service.py
import traceback
import datetime
import copy
from bson.objectid import ObjectId
from models import User, Character
from config.setup import Setup
from utils.text_utils import TextUtils

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
CHARACTER_HELP = SETUP.character_help
STRESS_HELP = SETUP.stress_help
CONSEQUENCES_HELP = SETUP.consequences_help
X = SETUP.x
O = SETUP.o
STRESS = SETUP.stress
STRESS_TITLES = SETUP.stress_titles
CONSEQUENCES = SETUP.consequences
CONSEQUENCES_TITLES = SETUP.consequences_titles
CONSEQUENCES_SHIFTS = SETUP.consequence_shifts

class CharacterService():
    def save(self, char, user):
        if char:
            if (not char.created):
                char.created = datetime.datetime.utcnow()
            char.updated_by = str(user.id)
            char.updated = datetime.datetime.utcnow()
            char.history_id = ''
            char.save()

    def save_user(self, user):
        if user:
            if (not user.created):
                user.created = datetime.datetime.utcnow()
            user.updated_by = str(user.id)
            user.updated = datetime.datetime.utcnow()
            user.save()

    def get_parent_by_id(self, char, user, parent_id):
        parent = Character.filter(id=ObjectId(parent_id)).first()
        if parent:
            user.active_character = str(parent.id)
            self.save_user(user)
            return [parent.get_string(user)] if parent.get_string else f'***{parent.name}*** selected as Active Character'
        return ['No parent found']

    def get_char_info(self, char, user):
        name = char.name if char else 'your character'
        get_string = char.get_string(user) if char else ''
        get_short_string = char.get_short_string(user) if char else ''
        return char, name, get_string, get_short_string
