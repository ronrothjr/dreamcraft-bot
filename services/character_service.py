# character_service.py
import traceback
import datetime
import copy
from bson.objectid import ObjectId
from models import User, Character, Stunt
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
    def save(self, char):
        if char:
            if (not char.created):
                char.created = datetime.datetime.utcnow()
            char.updated = datetime.datetime.utcnow()
            char.save()

    def save_user(self, user):
        if user:
            if (not user.created):
                user.created = datetime.datetime.utcnow()
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

    # def name(self, args):
    #     messages = []
    #     if len(args) == 0:
    #         if not self.char:
    #             return [
    #                 'No active character or name provided\n\n',
    #                 self.dialog('all')
    #             ]
    #         messages.append(self.dialog('active_character') + '\n')
    #     else:
    #         if len(args) == 1 and args[1].lower() == 'short':
    #             return [self.dialog('active_character_short')]
    #         char_name = ' '.join(args[1:])
    #         if len(args) > 1 and args[1] == 'rename':
    #             char_name = ' '.join(args[2:])
    #             if not self.char:
    #                 return [
    #                     'No active character or name provided\n\n',
    #                     self.dialog('all')
    #                 ]
    #             else:
    #                 char = Character().find(self.user, char_name, self.guild.name)
    #                 if char:
    #                     return [
    #                         f'Cannot rename to _{char_name}_. Character already exists'
    #                     ]
    #                 else:
    #                     self.char.name = char_name
    #                     self.save()
    #         else:
    #             self.char = Character().get_or_create(self.user, char_name, self.guild.name)
    #             self.user.set_active_character(self.char)
    #             self.save_user()
    #         messages.append(self.dialog('active_character'))
    #         messages.append(f'\n\n_Is ***{self.char.name}*** not the character name you wanted?_\
    #             ```css\n.d c rename NEW_NAME```_Want to remove ***{self.char.name}***?_\
    #             ```css\n.d c delete {self.char.name}```')
    #         messages.append(self.dialog(''))
    #     return messages

    # def character_list(self, args):
    #     characters = Character().get_by_user(self.user)
    #     if len(characters) == 0:
    #         return ['You don\'t have any characters.\nTry this: ```css\n.d c CHARACTER_NAME```']
    #     else:
    #         return [f'{c.get_short_string(self.user)}\n' for c in characters]

    # def delete_character(self, args):
    #     messages = []
    #     search = ''
    #     if len(args) == 1:
    #         if not self.char:
    #             return ['No active character for deletion']
    #         search = self.char.name
    #         self.char = Character().find(self.user, search, self.guild.name, None, self.char.category, False)
    #     else:
    #         search = ' '.join(args[1:])
    #         self.char = Character().find(self.user, search, self.guild.name, None, 'Character', False)
    #     if not self.char:
    #         return [f'{search} was not found. No changes made.\nTry this: ```css\n.d c CHARACTER_NAME```']
    #     else:
    #         search = self.char.name
    #         parent_id = str(self.char.parent_id) if self.char.parent_id else ''
    #         self.char.reverse_delete()
    #         self.char.delete()
    #         messages.append(f'***{search}*** removed')
    #         if parent_id:
    #             messages.extend(self.get_parent_by_id(parent_id))
    #     return messages

    # def description(self, args):
    #     messages = []
    #     if len(args) == 1:
    #         messages.append('No description provided')
    #     if not self.char:
    #         messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
    #     else:
    #         description = ' '.join(args[1:])
    #         self.char.description = description
    #         self.save()
    #         messages.append(f'Description updated to {description}\n')
    #         messages.append(self.dialog('active_character_short') + '\n')
    #         messages.append(self.dialog(''))
    #     return messages

    # def high_concept(self, args):
    #     messages = []
    #     if len(args) == 2 or (len(args) == 1 and args[1].lower() != 'concept'):
    #         messages.append('No high concept provided')
    #     if not self.char:
    #         messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
    #     else:
    #         hc = ''
    #         if args[1].lower() == 'concept':
    #             hc = ' '.join(args[2:])
    #         else:
    #             hc = ' '.join(args[1:])
    #         self.char.high_concept = hc
    #         self.save()
    #         messages.append(f'High Concept updated to _{hc}_\n')
    #         messages.append(self.dialog('active_character_short') + '\n')
    #         messages.append(self.dialog(''))
    #     return messages

    # def trouble(self, args):
    #     messages = []
    #     if len(args) == 1:
    #         messages.append('No trouble provided')
    #     if not self.char:
    #         messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
    #     else:
    #         trouble = ' '.join(args[1:])
    #         self.char.trouble = trouble
    #         self.save()
    #         messages.append(f'Trouble updated to _{trouble}_\n')
    #         messages.append(self.dialog('active_character_short') + '\n')
    #         messages.append(self.dialog(''))
    #     return messages

    # def fate(self, args):
    #     if not self.char:
    #         return ['You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```']
    #     elif args[1].lower() in ['refresh', 'r']:
    #         if not self.char.refresh:
    #             self.char.refresh = 3
    #         refresh = int(args[2]) if len(args) == 3 and args[2].isdigit() else self.char.refresh
    #         self.char.refresh = refresh
    #         self.char.fate_points = self.char.refresh
    #     elif args[1] == '+':
    #         if not self.char.fate_points:
    #             self.char.fate_points = 0
    #         points = int(args[2]) if len(args) == 3 and args[2].isdigit() else 1
    #         self.char.fate_points += points if self.char.fate_points < 5 else 0
    #     elif args[1] == '-':
    #         if not self.char.fate_points:
    #             self.char.fate_points = 2
    #         points = int(args[2]) if len(args) == 3 and args[2].isdigit() else 1
    #         self.char.fate_points += points if self.char.fate_points < 5 else 0
    #     self.save()
    #     return [f'Fate Points: {self.char.fate_points}']

    # def custom(self, args):
    #     if not self.char:
    #         raise Exception('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
    #     messages = []
    #     if len(args) == 1:
    #         raise Exception('No custom name provided. Try this: ```css\n.d c custom CUSTOM_NAME\n/* EXAMPLE:\n.d c custom Home World */```')
    #     if len(args) == 2:
    #         raise Exception('No custom property information provided. Try this: ```css\n.d c custom CUSTOM_NAME_ABBREVIATION CUSTOM_PROPERTY_INFORMATION\n/* EXAMPLE:\n.d c custom Home Earth (alternate history) */```')
    #     if args[1] in ['delete', 'd']:
    #         custom_properties = copy.deepcopy(self.char.custom_properties) if self.char.custom_properties else {}
    #         display_name = TextUtils.clean(args[2])
    #         property_name = display_name.lower().replace(' ', '_')
    #         if property_name not in custom_properties:
    #             raise Exception('***{self.char.name}*** does not have a custom property named {display_name}')
    #         custom_properties.pop(property_name, None)
    #     else:
    #         display_name = TextUtils.clean(args[1])
    #         property_name = display_name.lower().replace(' ', '_')
    #         property_value = ' '.join(args[2:])
    #         custom_properties = copy.deepcopy(self.char.custom_properties) if self.char.custom_properties else {}
    #         custom_properties[property_name] = {
    #             'display_name': display_name,
    #             'property_value': property_value
    #         }
    #     self.char.custom_properties = custom_properties
    #     self.save()
    #     messages.append(self.dialog('active_character'))
    #     messages.append(f'\n\n_Is ***{self.char.name}*** not the character name you wanted?_\
    #         ```css\n.d c rename NEW_NAME```_Want to remove ***{self.char.name}***?_\
    #         ```css\n.d c delete {self.char.name}```')
    #     messages.append(self.dialog(''))
    #     return messages

    # def approach(self, args):
    #     messages = []
    #     if args[1].lower() == 'help':
    #         app_str = '\n        '.join(APPROACHES)
    #         messages.append(f'**Approaches:**\n        {app_str}')
    #     elif len(args) < 3:
    #         messages.append('Approach syntax: .d (app)roach {approach} {bonus}')
    #     else:
    #         if not self.char:
    #             messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
    #         else:
    #             if args[1].lower() == 'delete' or args[1].lower() == 'd':
    #                 skill = [s for s in APPROACHES if args[2][0:2].lower() == s[0:2].lower()]
    #                 skill = skill[0].split(' - ')[0] if skill else args[2]
    #                 if skill in self.char.skills:
    #                     new_skills = {}
    #                     for key in self.char.skills:
    #                         if key != skill:
    #                             new_skills[key] = self.char.skills[key]
    #                     self.char.skills = new_skills
    #                 self.save()
    #                 messages.append(f'Removed {skill}')
    #             else:
    #                 for i in range(1, len(args), 2):
    #                     abbr = args[i][0:2].lower()
    #                     val = args[i+1]
    #                     skill = [s for s in APPROACHES if abbr == s[0:2].lower()]
    #                     skill = skill[0].split(' - ')[0] if skill else args[i]
    #                     self.char.skills[skill] = val
    #                     messages.append(f'Updated {skill} to {val}')
    #                 self.char.use_approaches = True
    #                 self.save()
    #             messages.append(self.char.get_string_skills() + '\n')
    #             messages.append(self.dialog(''))
    #     return messages

    # def skill(self, args):
    #     messages = []
    #     if args[1].lower() == 'help':
    #         sk_str = '\n        '.join(SKILLS)
    #         messages.append(f'**Skills:**\n        {sk_str}')
    #     elif len(args) != 3 and len(args) != 2:
    #         messages.append('Skill syntax: .d (sk)ill {skill} {bonus}')
    #     else:
    #         if not self.char:
    #             messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
    #         else:
    #             if args[1].lower() == 'delete' or args[1].lower() == 'd':
    #                 skill = [s for s in SKILLS if args[2][0:2].lower() == s[0:2].lower()]
    #                 skill = skill[0].split(' - ')[0] if skill else args[2]
    #                 if skill in self.char.skills:
    #                     new_skills = {}
    #                     for key in self.char.skills:
    #                         if key != skill:
    #                             new_skills[key] = self.char.skills[key]
    #                     self.char.skills = new_skills
    #                 self.save()
    #                 messages.append(f'Removed {skill} skill') 
    #             else:
    #                 skill = [s for s in SKILLS if args[1][0:2].lower() == s[0:2].lower()]
    #                 skill = skill[0].split(' - ')[0] if skill else args[1]
    #                 self.char.skills[skill] = args[2]
    #                 self.char.use_approaches = False
    #                 self.save()
    #                 messages.append(f'Updated {skill} to {args[2]}')                
    #             messages.append(self.char.get_string_skills() + '\n')
    #             messages.append(self.dialog(''))
    #     return messages

    # def aspect(self, args):
    #     messages = []
    #     if len(args) == 1:
    #         if not self.asp:
    #             return ['You don\'t have an active aspect.\nTry this: ```css\n.d c a {aspect}```']
    #         messages.append(f'{self.asp.get_string(self.char)}')
    #     if not self.char:
    #         return ['You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```']
    #     elif args[1].lower() == 'list':
    #         return [self.char.get_string_aspects(self.user)]
    #     elif args[1].lower() == 'delete' or args[1].lower() == 'd':
    #         aspect = ' '.join(args[2:])
    #         for a in Character().get_by_parent(self.char, aspect, 'Aspect'):
    #             aspect = str(a.name)
    #             a.reverse_delete()
    #             a.delete()
    #         messages.append(f'"{aspect}" removed from aspects')
    #         messages.append(self.char.get_string_aspects(self.user))
    #     elif args[1].lower() in ['character', 'char', 'c']:
    #         if not self.asp:
    #             return ['You don\'t have an active aspect.\nTry this: ```css\n.d c a {aspect}```']
    #         self.user.active_character = str(self.asp.id)
    #         self.save_user()
    #         self.char.active_aspect = str(self.asp.id)
    #         self.char.active_character = str(self.asp.id)
    #         self.save()
    #         command = CharacterCommand(self.ctx, args[1:], self.asp)
    #         messages.extend(command.run())
    #     else:
    #         aspect = ' '.join(args[1:])
    #         self.asp = Character().get_or_create(self.user, aspect, self.guild.name, self.char, 'Aspect')
    #         self.char.active_aspect = str(self.asp.id)
    #         self.save()
    #         messages.append(self.char.get_string_aspects(self.user) + '\n')
    #         messages.append(self.dialog('edit_active_aspect'))
    #     return messages

    # def stunt(self, args):
    #     messages = []
    #     if len(args) == 1:
    #         if not self.stu:
    #             return ['You don\'t have an active stunt.\nTry this: ```css\n.d c a {aspect}```']
    #         messages.append(f'{self.stu.get_string(self.char)}')
    #     if not self.char:
    #         return ['You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```']
    #     elif args[1].lower() == 'list':
    #         return [self.char.get_string_stunts(self.user)]
    #     elif args[1].lower() == 'delete' or args[1].lower() == 'd':
    #         stunt = ' '.join(args[2:])
    #         for s in Character().get_by_parent(self.char, stunt, 'Stunt'):
    #             stunt = str(s.name)
    #             s.reverse_delete()
    #             s.delete()
    #         messages.append(f'"{stunt}" removed from stunts')
    #         messages.append(self.char.get_string_stunts(self.user))
    #     elif args[1].lower() in ['character', 'char', 'c']:
    #         self.user.active_character = str(self.stu.id)
    #         self.save_user()
    #         self.char.active_stunt = str(self.stu.id)
    #         self.char.active_character = str(self.stu.id)
    #         self.save()
    #         command = CharacterCommand(self.ctx, args[1:], self.stu)
    #         messages.extend(command.run())
    #     else:
    #         stunt = ' '.join(args[1:])
    #         self.stu = Character().get_or_create(self.user, stunt, self.guild.name, self.char, 'Stunt')
    #         self.char.active_stunt = str(self.stu.id)
    #         self.char.active_character = str(self.stu.id)
    #         self.save()
    #         messages.append(self.char.get_string_stunts(self.user) + '\n')
    #     messages.append(self.dialog(''))
    #     return messages

    # def get_available_stress(self, stress_type):
    #     return sum([1 for s in self.char.stress[stress_type] if s[1] == O]) if self.char.stress else 0

    # def stress(self, args, check_user=None):
    #     messages = []
    #     if len(args) == 1:
    #         messages.append(STRESS_HELP)
    #         return messages
    #     if args[1].lower() == 'help':
    #         messages.append(STRESS_HELP)
    #         return messages
    #     modified = None
    #     stress_titles = self.char.stress_titles if self.char.stress_titles else STRESS_TITLES
    #     stress_checks = []
    #     [stress_checks.append(t[0:2].lower()) for t in stress_titles]
    #     [stress_checks.append(t.lower()) for t in stress_titles]
    #     stress_check_types = ' or '.join([f'({t[0:2 ].lower()}){t[2:].lower()}' for t in stress_titles])
    #     if not self.char:
    #         messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
    #         return messages
    #     if len(args) == 1:
    #         messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_stress()}')
    #         return messages
    #     if args[1] in ['title', 't']:
    #         if len(args) == 2:
    #             messages.append('No stress title provided')
    #             return messages
    #         titles = []
    #         if self.char.stress_titles:
    #             titles = copy.deepcopy(self.char.stress_titles)
    #         if args[2] in ['delete', 'd']:
    #             if not titles:
    #                 messages.append('You have not defined any custom stress titles')
    #                 return messages
    #             title = ' '.join(args[3:])
    #             indeces = [i for i in range(0, len(titles)) if title.lower() in titles[i].lower()]
    #             if not indeces:
    #                 messages.append(f'_{title}_ not found in custom stress titles')
    #                 return messages
    #             else:
    #                 stress = copy.deepcopy(self.char.stress)
    #                 modified = [stress[i] for i in range(0, len(stress)) if title.lower() not in titles[i].lower()]
    #                 titles = [t for t in titles if title.lower() not in t.lower()]
    #                 self.char.stress_titles = titles if titles else None
    #                 messages.append(f'_{title}_ removed from stress titles')
    #                 self.char.stress = modified
    #                 messages.append(f'{self.char.get_string_stress()}')
    #         else:
    #             total = args[2]
    #             title = ' '.join(args[3:])
    #             if total == "None":
    #                 self.char.stress = None
    #                 self.char.stress_titles = None
    #                 messages.append(f'{self.char.get_string()}')
    #             elif total == "FATE":
    #                 self.char.stress = STRESS
    #                 self.char.stress_titles = None
    #             elif total == "FAE":
    #                 self.char.stress = SETUP.stress_FAE
    #                 self.char.stress_titles = SETUP.stress_titles_FAE
    #             elif total == "Core":
    #                 self.char.stress = SETUP.stress_Core
    #                 self.char.stress_titles = SETUP.stress_titles_Core
    #             else:
    #                 if not total.isdigit():
    #                     messages.append('Stress shift must be a positive integer')
    #                     return messages
    #                 stress_boxes = []
    #                 [stress_boxes.append(['1', O]) for i in range(0, int(total))]
    #                 matches = [t for t in titles if title.lower() in t.lower()]
    #                 modified = copy.deepcopy(self.char.stress) if self.char.stress_titles and self.char.stress else []
    #                 if matches:
    #                     for i in range(0, len(titles)):
    #                         if title.lower() in titles[i].lower():
    #                             modified[i] = stress_boxes
    #                 else:
    #                     titles.append(title)
    #                     self.char.stress_titles = titles
    #                     modified.append(stress_boxes)
    #                     messages.append(f'_{title}_ added to stress titles')
    #                 self.char.stress = modified
    #             messages.append(f'{self.char.get_string_stress()}')
    #     elif args[1] in ['refresh', 'r']:
    #         modified = copy.deepcopy(self.char.stress)
    #         if len(args) == 3:
    #             if args[2].lower() not in stress_checks:
    #                 messages.append(f'{args[2].lower()} is not a valid stress type for ***{self.char.name}*** - {stress_check_types}')
    #                 return messages
    #             else:
    #                 stress_type_str = args[2].lower()
    #                 stress_type = [i for i in range(0, len(stress_titles)) if stress_type_str in [stress_titles[i].lower()[0:2], stress_titles[i].lower()]][0]
    #                 stress_type_name = stress_titles[stress_type]
    #                 for s in range(0, len(self.char.stress[stress_type])):
    #                     modified[stress_type][s][1] = O
    #                 messages.append(f'Refreshed all of ***{self.char.name}\'s*** _{stress_type_name}_ stress')
    #                 self.char.stress = modified
    #                 messages.append(f'{self.char.get_string_stress()}')
    #         else:
    #             for i in range(0, len(self.char.stress)):
    #                 for s in range(0, len(self.char.stress[i])):
    #                     modified[i][s][1] = O
    #             messages.append(f'Refreshed all of ***{self.char.name}\'s*** stress')
    #             self.char.stress = modified
    #             messages.append(f'{self.char.get_string_stress()}')
    #     elif args[1] in ['delete', 'd']:
    #         if len(args) == 2:
    #             messages.append(f'No stress type provided - {stress_check_types}')
    #             return messages
    #         if args[2].lower() not in stress_checks:
    #             messages.append(f'{args[2].lower()} is not a valid stress type for ***{self.char.name}*** - {stress_check_types}')
    #             return messages
    #         if len(args) == 3:
    #             args = args + ('1',)
    #         if len(args) == 4:
    #             shift = args[3]
    #             if not shift.isdigit():
    #                 messages.append('Stress shift must be a positive integer')
    #                 return messages
    #             shift_int = int(shift)
    #             stress_type_str = args[2].lower()
    #             stress_type = [i for i in range(0, len(stress_titles)) if stress_type_str in [stress_titles[i].lower()[0:2], stress_titles[i].lower()]][0]
    #             stress_type_name = stress_titles[stress_type]
    #             available = self.get_available_stress(stress_type)
    #             if available == len(self.char.stress[stress_type]):
    #                 messages.append(f'***{self.char.name}*** has no _{stress_type_name}_ stress to remove')
    #                 return messages
    #             modified = copy.deepcopy(self.char.stress)
    #             for s in range(len(self.char.stress[stress_type])-1,-1,-1):
    #                 if shift_int > 0 and self.char.stress[stress_type][s][1] == X:
    #                     shift_int -= 1
    #                     modified[stress_type][s][1] = O
    #             messages.append(f'Removed {shift} from ***{self.char.name}\'s*** _{stress_type_name}_ stress')
    #             self.char.stress = modified
    #             messages.append(f'{self.char.get_string_stress()}')
    #     else:
    #         if len(args) == 2:
    #             args = args + ('1',)
    #         if args[1].lower() not in stress_checks:
    #             messages.append(f'{args[1].lower()} is not a valid stress type for ***{self.char.name}*** - {stress_check_types}')
    #             return messages
    #         shift = args[2]
    #         if not shift.isdigit():
    #             messages.append('Stress shift must be a positive integer')
    #             return messages
    #         stress_type_str = args[1].lower()
    #         stress_type = [i for i in range(0, len(stress_titles)) if stress_type_str in [stress_titles[i].lower()[0:2], stress_titles[i].lower()]][0]
    #         stress_type_name = stress_titles[stress_type]
    #         shift_int = int(shift)
    #         available = self.get_available_stress(stress_type)
    #         if shift_int > available:
    #             messages.append(f'***{self.char.name}*** cannot absorb {shift} {stress_type_name} stress ({available} available)')
    #             return messages
    #         modified = copy.deepcopy(self.char.stress)
    #         for s in range(0,len(self.char.stress[stress_type])):
    #             if shift_int > 0 and self.char.stress[stress_type][s][1] == O:
    #                 shift_int -= 1
    #                 modified[stress_type][s][1] = X
    #         if not check_user:
    #             messages.append(f'***{self.char.name}*** absorbed {shift} {stress_type_name} stress')
    #             self.char.stress = modified
    #             messages.append(f'{self.char.get_string_stress()}')
    #     if check_user:
    #         return messages
    #     else:
    #         self.save()
    #     return messages

    # def consequence(self, args):
    #     messages = []
    #     if args[1].lower() == 'help':
    #         messages.append(CONSEQUENCES_HELP)
    #         return messages
    #     modified = None
    #     consequences = copy.deepcopy(self.char.consequences) if self.char.consequences else CONSEQUENCES
    #     consequences_titles = copy.deepcopy(self.char.consequences_titles) if self.char.consequences_titles else CONSEQUENCES_TITLES
    #     consequences_shifts = copy.deepcopy(self.char.consequences_shifts) if self.char.consequences_shifts else CONSEQUENCES_SHIFTS
    #     consequences_name = 'Condition' if self.char.consequences_titles else 'Consequence'
    #     consequences_checks = []
    #     [consequences_checks.append(t[0:2].lower()) for t in consequences_titles]
    #     [consequences_checks.append(t.lower()) for t in consequences_titles]
    #     consequences_check_types = ' or '.join([f'({t[0:2].lower()}){t[2:].lower()}' for t in consequences_titles])
    #     if len(args) == 1:
    #         messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_consequences()}')
    #         return messages
    #     if args[1] in ['title', 't']:
    #         if len(args) == 2:
    #             messages.append(f'No Condition title provided')
    #             return messages
    #         if args[2] in ['delete', 'd']:
    #             if not self.char.consequences_titles:
    #                 messages.append('You have not defined any Condition titles')
    #                 return messages
    #             title = ' '.join(args[3:])
    #             indeces = [i for i in range(0, len(consequences_titles)) if title.lower() in consequences_titles[i].lower()]
    #             if not indeces:
    #                 messages.append(f'_{title}_ not found in Condition titles')
    #                 return messages
    #             else:
    #                 modified_consequences = []
    #                 modified_titles = []
    #                 modified_shifts = []
    #                 for i in range(0, len(consequences_titles)):
    #                     if title.lower() not in consequences_titles[i].lower():
    #                         modified_consequences.append(consequences[i])
    #                         modified_titles.append(consequences_titles[i])
    #                         modified_shifts.append(consequences_shifts[i])
    #                 self.char.consequences = modified_consequences
    #                 self.char.consequences_titles = modified_titles if modified_titles else None
    #                 self.char.consequences_shifts = modified_shifts if modified_shifts else None
    #                 messages.append(f'_{title}_ removed from Conditions titles')
    #         else:
    #             total = args[2]
    #             title = ' '.join(args[3:])
    #             if total == "None":
    #                 self.char.consequences = None
    #                 self.char.consequences_titles = None
    #                 self.char.consequences_shifts = None
    #                 messages.append(f'{self.char.get_string()}')
    #             elif total == "FATE":
    #                 self.char.consequences = CONSEQUENCES
    #                 self.char.consequences_titles = None
    #                 self.char.consequences_shifts = None
    #             else:
    #                 if not total.isdigit():
    #                     messages.append('Stress shift must be a positive integer')
    #                     return messages
    #                 if not self.char.consequences_titles:
    #                     consequences = []
    #                     consequences_titles = []
    #                     consequences_shifts = []
    #                 matches = [i for i in range(0, len(consequences_titles)) if title.lower() in consequences_titles[i].lower()]
    #                 if matches:
    #                     for i in range(0, len(consequences_titles)):
    #                         if title.lower() in consequences_titles[i].lower():
    #                             consequences[i] = [total, O]
    #                             consequences_titles[i] = title
    #                             consequences_shifts[i] = total
    #                     messages.append(f'Updated the _{title} ({total})_ Conditions title')
    #                 else:
    #                     consequences.append([total, O])
    #                     consequences_titles.append(title)
    #                     consequences_shifts.append(total)
    #                     messages.append(f'_{title} ({total})_ added to Conditions titles')
    #                 self.char.consequences = consequences
    #                 self.char.consequences_titles = consequences_titles
    #                 self.char.consequences_shifts = consequences_shifts
    #     elif args[1] in ['delete', 'd']:
    #         if len(args) == 2:
    #             messages.append(f'No severity provided - {consequences_check_types}')
    #             return messages
    #         if args[2].lower() not in consequences_checks:
    #             messages.append(f'{args[2].lower()} is not a valid severity - {consequences_check_types}')
    #             return messages
    #         severity_str = args[2].lower()
    #         severity = [i for i in range(0, len(consequences_titles)) if 1 if severity_str in [consequences_titles[i].lower()[0:2], consequences_titles[i].lower()]][0]
    #         severity_shift = consequences_shifts[severity]
    #         severity_name = consequences_titles[severity]
    #         if self.char.consequences[severity][1] == O:
    #             messages.append(f'***{self.char.name}*** does not currently have a _{severity_name}_ {consequences_name}')
    #             return messages
    #         previous = copy.deepcopy(self.char.consequences)
    #         modified = copy.deepcopy(self.char.consequences)
    #         modified[severity] = [severity_shift, O]
    #         self.char.consequences = modified
    #         aspect = severity_name if self.char.consequences_titles else previous[severity][2]
    #         messages.append(f'Removed ***{self.char.name}\'s*** _{severity_name}_ from {consequences_name} ("{aspect}")')
    #         messages.extend(self.aspect(['a', 'd', aspect]))
    #     else:
    #         if len(args) == 2 and not self.char.consequences_titles:
    #             messages.append('Missing Consequence aspect')
    #             return messages
    #         if args[1].lower() not in consequences_checks:
    #             messages.append(f'{args[1].lower()} is not a valid severity - {consequences_check_types}')
    #             return messages
    #         severity_str = args[1].lower()
    #         severity = [i for i in range(0, len(consequences_titles)) if 1 if severity_str in [consequences_titles[i].lower()[0:2], consequences_titles[i].lower()]][0]
    #         severity_shift = consequences_shifts[severity]
    #         severity_name = consequences_titles[severity]
    #         if self.char.consequences[severity][1] == X:
    #             messages.append(f'***{self.char.name}*** already has a _{severity_name}_ {consequences_name} ("{self.char.consequences[severity][2]}")')
    #             return messages
    #         aspect = severity_name if self.char.consequences else ' '.join(args[2:])
    #         modified = copy.deepcopy(self.char.consequences)
    #         if self.char.consequences_titles:
    #             modified[severity] = [severity_shift, X]
    #         else:
    #             modified[severity] = [severity_shift, X, aspect]
    #         messages.append(f'***{self.char.name}*** absorbed {severity_shift} shift for a {severity_name} {consequences_name} "{aspect}"')
    #         messages.extend(self.aspect(['a', aspect]))
    #         self.char.consequences = modified
    #     messages.append(f'{self.char.get_string_consequences()}')
    #     self.save()
    #     return messages