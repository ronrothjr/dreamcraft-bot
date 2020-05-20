# roll_command.py
import traceback
import datetime
import random
import copy
from bson.objectid import ObjectId
from models import Channel, Scenario, Scene, Zone, User, Character
from commands import CharacterCommand
from config.setup import Setup

SETUP = Setup()
ROLL_HELP = SETUP.roll_help
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
FATE_DICE = SETUP.fate_dice

class RollCommand():
    def __init__(self, parent, ctx, args, guild=None, user=None, channel=None):
        self.parent = parent
        self.ctx = ctx
        self.args = args
        self.guild = guild
        self.user = user
        self.channel = channel
        self.invoke_index = [i for i in range(0, len(self.args)) if self.args[i] in ['invoke', 'i']]
        self.compel_index = [i for i in range(0, len(self.args)) if self.args[i] in ['compel', 'c']]
        self.command = args[0].lower()
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None
        self.skill = self.args[1] if len(args) > 1 else ''
        self.messages = []
        self.invokes = []
        self.compels = []
        self.errors = []
        self.invokes_cost = 0

    def run(self):
        try:
            if len(self.args) > 1 and self.args[1] == 'help':
                raise Exception(ROLL_HELP)
            if not self.char:
                raise Exception('No active character. Try this: ```css\n.d c CHARACTER_NAME```')
            self.messages = [self.char.get_string_name(self.user)]
            self.last_roll = None
            # parse skill from args
            self.get_skill()

            # find and validate invokes and compels
            self.validate()
            if self.errors:
                raise Exception(*[e.error for e in self.errors])

            if self.command in ['available', 'avail', 'av']:
                raise Exception(*self.available_aspects())
            if self.command in ['roll', 'r']:
                self.last_roll = self.roll()
                self.char.last_roll = self.last_roll
                self.messages.append(self.char.last_roll['roll_text'])
            elif self.command in ['reroll', 're']:
                if not self.invokes:
                    raise Exception('You did not include an invoke for the reroll')
                else:
                    self.invokes_cost = sum([invoke['fate_points'] for invoke in self.invokes])
                    self.last_roll = self.reroll()
                    self.char.last_roll = self.last_roll
                    self.messages.append(self.char.last_roll['roll_text'])

            if self.invokes:
                self.handle_invokes()

            if self.compels:
                self.handle_compels()

            self.save_char()

            return self.messages
        except Exception as err:
            traceback.print_exc()
            return list(err.args)

    def save_char(self):
        if (not self.char.created):
            self.char.created = datetime.datetime.utcnow()
        self.char.updated_by = str(self.user.id)
        self.char.updated = datetime.datetime.utcnow()
        self.char.save()

    # determine skill to validate
    def get_skill(self):
        if self.command in ['reroll', 're']:
            self.skill = self.char.last_roll['skill']
        elif not self.invoke_index or (self.invoke_index and self.invoke_index[0] > 1):
            self.skill = self.match_skill()

    def validate(self):
        self.get_invokes()
        self.errors.extend([i['error'] for i in self.invokes if i['aspect_name'] == 'error'])
        if self.errors:
            raise Exception(*self.errors)
        self.get_compels()
        self.errors.extend([c['error'] for c in self.compels if c['aspect_name'] == 'error'])
        if self.errors:
            raise Exception(*self.errors)
        if self.invoke_index and self.compel_index:
            raise Exception('You cannot invoke and compel on the same roll')

    def handle_invokes(self):
        char = self.get_parent_with_refresh(self.char)
        if char and self.invokes_cost >= char.fate_points + self.invokes_cost:
            raise Exception(f'***{char.name}*** does not have enough fate points')
        else:
            char.fate_points -= self.invokes_cost
            for invoke in self.invokes:
                if invoke['stress_titles']:
                    for i in range(0, len(invoke['stress_titles'])):
                        command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=self.args, guild=self.guild, user=self.user, channel=self.channel, char=invoke['stress_targets'][i])
                        stress_messages = command.stress(['st', invoke['stress_titles'][i], invoke['stress'][i][0][0]])
                        if 'cannot absorb' in ''.join(stress_messages):
                            raise Exception(*stress_messages)
                        self.messages.extend(stress_messages)
            self.messages.append(self.char.get_string_fate())

    def handle_compels(self):
            if len(self.compels) + self.char.fate_points <= 5:
                self.char.fate_points += len(self.compels)
                self.messages.append(''.join([f'Compelled "{c}" and added 1 fate point' for c in self.compels]))
                self.messages.append(self.char.get_string_fate())
            else:
                raise Exception(f'{self.char.name} already has the maximum fate points (5)')

    def get_invokes(self):
        self.re = self.command in ['reroll', 're']
        stress_targets = []
        for i in self.invoke_index:
            if len(self.args) < i+1 or self.skill and len(self.args) < i+2:
                self.invokes.append({'aspect_name': 'error', 'error': f'An invoke is mssing an aspect'})
                continue
            search = self.args[i+1]
            aspect_name = ''
            category = ''
            skills = []
            aspect = None
            fate_points = None
            asp = self.find_aspect(search)
            if asp:
                aspect = asp['char']
                category = asp['category']
                if category in ['High Concept', 'Trouble']:
                    aspect_name = getattr(aspect, category.lower().replace(' ','_'))
                    skills = []
                    fate_points = 0 if category == 'Stunt' else 1
                    stress = []
                    stress_titles = []
                else:
                    aspect_name = aspect.name
                    skills = aspect.skills if aspect.skills else []
                    if aspect.fate_points is not None:
                        fate_points = aspect.fate_points
                    else:
                        fate_points = 0 if category == 'Stunt' else 1
                    stress = aspect.stress if aspect.stress else []
                    stress_titles = aspect.stress_titles if aspect.stress_titles else []
                    stress_errors, stress_targets = self.validate_stress(aspect, stress, stress_titles, stress_targets)
                    [self.invokes.append({'aspect_name': 'error', 'error': s}) for s in stress_errors]
            else:
                self.invokes.append({'aspect_name': 'error', 'error': f'_{search}_ not found in availabe aspects'})
                continue
            if self.re and (len(self.args) <= i+2 or (len(self.args) > i+2 and self.args[i+2] not in ['+2', 're', 'reroll'])):
                self.invokes.append({'aspect_name': 'error', 'error': f'Reroll invoke on {aspect_name} is missing +2 or (re)roll'})
                continue
            check_invokes = []
            check_invokes.extend(self.invokes)
            if self.re:
                check_invokes.extend(self.char.last_roll['invokes'])
            if [dup for dup in check_invokes if aspect_name == dup['aspect_name']]:
                self.invokes.append({'aspect_name': 'error', 'error': f'{aspect_name} cannot be invoked more than once on the same roll'})
                continue
            invoke = {
                'aspect_name': aspect_name,
                'bonus_str': '+2',
                'skills': skills,
                'fate_points': fate_points,
                'category': category,
                'stress': stress,
                'stress_titles': stress_titles,
                'stress_targets': stress_targets
            }
            if self.re:
                invoke['bonus_str'] = '+2' if self.args[i+2] == '+2' else 'reroll'
            self.invokes.append(invoke)

    def validate_stress(self, aspect, stress, stress_titles, stress_targets):
        aspect_name = aspect.name
        stress_errors = []
        possible_targets = self.char.get_invokable_objects()
        for s in range(0, len(stress_titles)):
            targets = copy.deepcopy(possible_targets)
            parent_stress = self.get_parent_with_stress(self.char, stress_titles[s])
            if parent_stress:
                targets.append({'char': parent_stress, 'parent': parent_stress})
            stress_targets.append(None)
            has_stress = []
            for target in targets:
                stress_target = copy.deepcopy(target['char'])
                command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=self.args, guils=self.guild, user=self.user, channel=self.channel, char=stress_target)
                target_errors = command.stress(['st', stress_titles[s], stress[s][0][0]], stress_target)
                if target_errors:
                    for error in target_errors:
                        if 'cannot absorb' in error and aspect_name.lower() not in stress_target.name.lower():
                            has_stress.append(error)
                            continue
                else:
                    stress_targets[s] = stress_target
                    continue
            if stress_targets[s] is None:
                stress_errors.append(f'Cannot find a target to apply _{stress[s][0][0]} {stress_titles[s]}_ from **{aspect_name}**')
                if has_stress:
                    [stress_errors.append(has) for has in has_stress]
        return stress_errors, stress_targets        

    def get_compels(self):
        for i in self.compel_index:
            aspect = self.find_aspect(self.args[i+1])
            if len(self.args) < i+1:
                self.compels.append(['error', f'Mssing aspect'])
                continue
            if not aspect:
                self.compels.append(['error', f'{self.args[i+1]} not found in availabe aspects'])
                continue
            if [dup for dup in self.compels if aspect == dup]:
                self.compels.append(['error', f'{aspect} cannot be compeled more than once on the same roll'])
                continue
            self.compels.append(aspect)

    def get_parent_with_refresh(self, char):
        if char:
            if char.refresh:
               return char
            else:
                if char.parent_id:
                    parent = Character.get_by_id(char.parent_id)
                    return self.get_parent_with_refresh(parent)
        else:
            return None

    def get_parent_with_stress(self, char, stress):
        if char:
            if char.stress_titles and stress in char.stress_titles:
               return char
            else:
                if char.parent_id:
                    parent = Character.get_by_id(char.parent_id)
                    return self.get_parent_with_refresh(parent)
        else:
            return None

    def get_available_invokes(self, char=None):
        char = char if char else self.char
        self.available = char.get_invokable_objects() if char else []
        scenario_aspects = self.scenario.character.get_invokable_objects() if self.scenario else []
        self.available.extend(scenario_aspects)
        sc_aspects = self.sc.character.get_invokable_objects() if self.sc else []
        self.available.extend(sc_aspects)
        zone_aspects = self.zone.character.get_invokable_objects() if self.zone else []
        self.available.extend(zone_aspects)
        if self.sc and self.sc.characters:
            for char_id in self.sc.characters:
                char = Character.get_by_id(char_id)
                if char and not char.name == char.name:
                    self.available.extend(char.get_invokable_objects())
        if self.zone and self.zone.characters:
            for char_id in self.zone.characters:
                char = Character.get_by_id(char_id)
                if char and not char.name == self.char.name:
                    self.available.extend(char.get_invokable_objects())
        return self.available

    def available_aspects(self):
        self.get_available_invokes()
        self.available_invokes = []
        [self.available_invokes.extend(a['char'].get_available_aspects(a['parent'])) for a in self.available]
        if self.available_invokes:
            return ['**Available invokes:**\n        ' + '\n        '.join([a for a in self.available_invokes])]
        else:
            return ['No available aspects to invoke']

    def find_aspect(self, aspect):
        aspect = aspect.replace('_', ' ')
        available = self.get_available_invokes()
        aspects = []
        if self.char:
            for a in available:
                aspect_list = []
                if a['char'].category in ['Aspect','Stunt']:
                    aspect_list.append({'name': a['char'].name.lower(), 'category': a['char'].category})
                if a['char'].high_concept:
                    aspect_list.append({'name': a['char'].high_concept.lower(), 'category': 'High Concept'})
                if a['char'].trouble:
                    aspect_list.append({'name': a['char'].trouble.lower(), 'category': 'Trouble'})
                [
                    aspects.append({'char': a['char'], 'category': asp['category']}) \
                    for asp in aspect_list \
                    if aspect.lower() in asp['name'].lower()
                ]
                    
            if aspects:
                return aspects[0]
        return aspects

    def roll(self):
        skill_str, bonus = self.get_skill_bonus()
        bonus_invokes, bonus_invokes_total, invokes_bonus_string, invoke_string = \
            self.get_invoke_bonus()
        bonus += bonus_invokes_total
        dice_roll = self.roll_dice()
        final_roll = dice_roll['rolled'] + bonus
        skill_bonus_str = f' + ({self.skill}{skill_str})' if skill_str else ''
        skill_bonus_str += f' = {final_roll}' if skill_bonus_str or bonus_invokes else ''
        rolled = dice_roll['rolled']
        fate_roll_string = dice_roll['fate_roll_string']
        return {
            'roll_text': f'{self.char.name} rolled: {fate_roll_string} = {rolled}{invokes_bonus_string}{skill_bonus_str}{invoke_string}',
            'roll': dice_roll['rolled'],
            'skill': self.skill,
            'skill_str': skill_str,
            'bonus': bonus,
            'fate_dice_roll': dice_roll['fate_dice_roll'],
            'fate_roll_string': dice_roll['fate_roll_string'],
            'dice': dice_roll['dice'],
            'final_roll': final_roll,
            'invokes': self.invokes,
            'invokes_bonus': bonus_invokes_total,
            'invokes_bonus_string': invokes_bonus_string,
            'invoke_string': invoke_string
        }

    def reroll(self):
        self.char.last_roll['invokes'].extend(self.invokes)
        self.skill = self.char.last_roll['skill']
        self.invokes = self.char.last_roll['invokes']
        return self.roll()

    def match_skill(self):
        if self.skill !='':
            if self.char.use_approaches:
                skill_name = [s for s in APPROACHES if self.skill[0:2].lower() == s[0:2].lower()]
            else:
                skill_name = [s for s in SKILLS if self.skill[0:2].lower() == s[0:2].lower()]
            self.skill = skill_name[0].split(' - ')[0] if skill_name else self.skill
        return self.skill

    def get_skill_bonus(self):
        skill_str = ''
        bonus = 0
        if self.skill !='':
            skill_str = ' ' + self.char.skills[self.skill] if self.skill in self.char.skills else ''
            bonus = int(skill_str) if skill_str else 0
        return skill_str, bonus

    def get_invoke_bonus(self):
        bonus_invokes = []
        for invoke in self.invokes:
            bonus_str = invoke['bonus_str']
            if self.skill in invoke['skills']:
                bonus_str = invoke['skills'][self.skill]
            elif invoke['category'] == 'Stunt':
                bonus_str = '+0'
            invoke.update({'bonus_str': bonus_str})
        bonus_invokes = len([invoke for invoke in self.invokes if invoke['bonus_str'] == '+2'])
        bonus_invokes_total = sum([int(i['bonus_str']) for i in self.invokes if 'reroll' not in i['bonus_str']])
        invokes_bonus_string = f' + (Invokes bonus = {bonus_invokes_total})' if self.invokes and bonus_invokes_total else ''
        invoke_string = self.get_invoke_string()
        return bonus_invokes, bonus_invokes_total, invokes_bonus_string, invoke_string

    def get_invoke_string(self):
        invoke_strings = []
        for invoke in self.invokes:
            name = invoke['aspect_name']
            category = invoke['category']
            bonus_str = invoke['bonus_str']
            fate_points = invoke['fate_points']
            s = 's' if invoke['fate_points'] == 0 or invoke['fate_points'] > 1 else ''
            invoike_string = f'\n...invoked the "{name}" _{category}_ for {bonus_str} (cost {fate_points} fate point{s})'
            invoke_strings.append(invoike_string)
        return ''.join(invoke_strings)

    def roll_dice(self):
        dice = [random.choice(range(-1, 2)) for _ in range(4)]
        fate_dice_roll = [FATE_DICE[str(d)] for d in dice]
        return {
            'dice': dice,
            'fate_dice_roll': fate_dice_roll,
            'fate_roll_string': ''.join(fate_dice_roll),
            'rolled': sum(dice)
        }
