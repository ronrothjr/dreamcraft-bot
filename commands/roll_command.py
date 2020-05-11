# roll_command.py
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
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.invoke_index = [i for i in range(0, len(self.args)) if self.args[i] in ['invoke', 'i']]
        self.compel_index = [i for i in range(0, len(self.args)) if self.args[i] in ['compel', 'c']]
        self.command = args[0].lower()
        self.channel = Channel().get_or_create(self.ctx.channel.name, self.ctx.guild.name)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.user = User().get_or_create(self.ctx.author.name, self.ctx.guild.name)
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        if len(self.args) > 1 and self.args[1] == 'help':
            return [ROLL_HELP]
        messages = [self.char.get_string_name(self.user)]
        errors = []
        last_roll = None
        skill = ''
        if self.command in ['reroll', 're']:
            skill = self.char.last_roll['skill']
        elif self.invoke_index and self.invoke_index[0] > 1:
            skill = self.match_skill(self.args[1])
        invokes = self.get_invokes(skill)
        errors.extend([i['error'] for i in invokes if i['aspect_name'] == 'error'])
        compels = self.get_compels()
        errors.extend([c[1] for c in compels if c[0] == 'error'])
        if self.invoke_index and self.compel_index:
            errors.append('You cannot invoke and compel on the same roll')
        if errors:
            return [e for e in errors]
        if self.command in ['available', 'avail', 'av']:
            return self.available_aspects()
        if self.command in ['roll', 'r']:
            last_roll = self.roll(skill, invokes)
            self.char.last_roll = last_roll
            messages.append(self.char.last_roll['roll_text'])
        elif self.command in ['reroll', 're']:
            if not invokes:
                return ['You did not include an invoke for the reroll']
            else:
                last_roll = self.reroll(skill, invokes)
                self.char.last_roll = last_roll
                messages.append(self.char.last_roll['roll_text'])
        if invokes:
            char = self.get_parent_with_refresh(self.char)
            invokes_cost = sum([invoke['fate_points'] for invoke in invokes])  
            if char and invokes_cost >= char.fate_points + invokes_cost:
                return [f'***{char.name}*** does not have enough fate points']
            else:
                for invoke in invokes:
                    aspect_name = invoke['aspect_name']
                    invoke_cost = invoke['fate_points']
                    category = invoke['category']
                    s = 's' if invoke_cost == 0 or invoke_cost > 1 else ''
                    char.fate_points -= invoke_cost
                    messages.append(f'***{char.name}*** invoked the _{aspect_name}_ {category} and used {invoke_cost} fate point{s}')
                    if invoke['stress_titles']:
                        for i in range(0, len(invoke['stress_titles'])):
                            # self.get_parent_with_stress(self.char, invoke['stress_titles'][i])
                            stress_target = invoke['stress_targets'][i]
                            stress_title = invoke['stress_titles'][i]
                            stress_total = invoke['stress'][i][0][0]
                            stress_args = ['st', stress_title, stress_total]
                            command = CharacterCommand(self.ctx, self.args, stress_target)
                            stress_messages = command.stress(stress_args)
                            if 'cannot absorb' in ''.join(stress_messages):
                                return stress_messages
                            messages.extend(stress_messages)
                messages.append(self.char.get_string_fate())
        if compels:
            if len(compels) + self.char.fate_points <= 5:
                self.char.fate_points += len(compels)
                messages.append(''.join([f'Compelled "{c}" and added 1 fate point' for c in compels]))
                messages.append(self.char.get_string_fate())
            else:
                return [f'{self.char.name} already has the maximum fate points (5)']
        if (not self.char.created):
            self.char.created = datetime.datetime.utcnow()
        self.char.updated = datetime.datetime.utcnow()
        self.char.save()
        return messages

    def get_invokes(self, skill):
        invokes = []
        for i in self.invoke_index:
            if len(self.args) < i+1:
                invokes.append(['error', f'An invoke is mssing an aspect'])
                continue
            aspect_name = ''
            skills = []
            aspect = self.find_aspect(self.args[i+1])
            fate_points = None
            stress_targets = []
            if aspect:
                aspect_name = aspect.name
                skills = aspect.skills if aspect.skills else []
                fate_points = aspect.fate_points if aspect.fate_points is not None else (0 if aspect.category == 'Stunt' else 1)
                stress = aspect.stress if aspect.stress else []
                stress_titles = aspect.stress_titles if aspect.stress_titles else []
                stress_errors = []
                possible_targets = self.char.get_invokable_objects()
                for i in range(0, len(stress_titles)):
                    targets = copy.deepcopy(possible_targets)
                    parent_stress = self.get_parent_with_stress(self.char, stress_titles[i])
                    if parent_stress:
                        targets.append({'char': parent_stress, 'parent': parent_stress})
                    stress_targets.append(None)
                    has_stress = []
                    for target in targets:
                        stress_target = copy.deepcopy(target['char'])
                        command = CharacterCommand(self.ctx, self.args, stress_target)
                        target_errors = command.stress(['st', stress_titles[i], stress[i][0][0]], stress_target)
                        if target_errors:
                            for error in target_errors:
                                if 'cannot absorb' in error and aspect_name.lower() not in stress_target.name.lower():
                                    has_stress.append(error)
                                    continue
                        else:
                            stress_targets[i] = stress_target
                            continue
                    if stress_targets[i] is None:
                        stress_errors.append(f'Cannot find a target to apply _{stress[i][0][0]} {stress_titles[i]}_ from **{aspect_name}**')
                        if has_stress:
                            [stress_errors.append(has) for has in has_stress]
                [invokes.append({'aspect_name': 'error', 'error': s}) for s in stress_errors]
            else:
                invokes.append({'aspect_name': 'error', 'error': f'_{self.args[i+1]}_ not found in availabe aspects'})
                continue
            if self.command in ['reroll', 're'] and len(self.args) <= i+2:
                invokes.append({'aspect_name': 'error', 'error': f'Reroll invoke on {aspect_name} is missing +2 or (re)roll'})
                continue
            if self.command in ['reroll', 're'] and len(self.args) > i+2 and self.args[i+2] not in ['+2', 're', 'reroll']:
                invokes.append({'aspect_name': 'error', 'error': f'Reroll invoke on {aspect_name} is missing +2 or (re)roll'})
                continue
            check_invokes = []
            check_invokes.extend(invokes)
            if self.command in ['reroll', 're']:
                check_invokes.extend(self.char.last_roll['invokes'])
            if [dup for dup in check_invokes if aspect_name == dup['aspect_name']]:
                invokes.append({'aspect_name': 'error', 'error': f'{aspect_name} cannot be invoked more than once on the same roll'})
                continue
            if self.command in ['reroll', 're']:
                invokes.append({
                    'aspect_name': aspect_name,
                    'bonus_str': '+2 bonus' if self.args[i+2] == '+2' else 'reroll',
                    'skills': skills,
                    'fate_points': fate_points,
                    'category': aspect.category,
                    'stress': stress,
                    'stress_titles': aspect.stress_titles if aspect.stress_titles else [],
                    'stress_targets': stress_targets
                })
            else:
                invokes.append({
                    'aspect_name': aspect_name,
                    'bonus_str': '+2 bonus',
                    'skills': skills,
                    'fate_points': fate_points,
                    'category': aspect.category,
                    'stress': stress,
                    'stress_titles': stress_titles,
                    'stress_targets': stress_targets
                })
        return invokes

    def get_compels(self):
        compels = []
        for i in self.compel_index:
            aspect = self.find_aspect(self.args[i+1])
            if len(self.args) < i+1:
                compels.append(['error', f'Mssing aspect'])
                continue
            if not aspect:
                compels.append(['error', f'{self.args[i+1]} not found in availabe aspects'])
                continue
            if [dup for dup in compels if aspect == dup]:
                compels.append(['error', f'{aspect} cannot be compeled more than once on the same roll'])
                continue
            compels.append(aspect)
        return compels

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

    def get_available_invokes(self, char):
        available = char.get_invokable_objects() if char else []
        scenario_aspects = self.scenario.character.get_invokable_objects() if self.scenario else []
        available.extend(scenario_aspects)
        sc_aspects = self.sc.character.get_invokable_objects() if self.sc else []
        available.extend(sc_aspects)
        zone_aspects = self.zone.character.get_invokable_objects() if self.zone else []
        available.extend(zone_aspects)
        if self.sc and self.sc.characters:
            for char_id in self.sc.characters:
                char = Character.get_by_id(char_id)
                if char and not char.name == char.name:
                    available.extend(char.get_invokable_objects())
        if self.zone and self.zone.characters:
            for char_id in self.zone.characters:
                char = Character.get_by_id(char_id)
                if char and not char.name == self.char.name:
                    available.extend(char.get_invokable_objects())
        return available

    def available_aspects(self):
        aspect_list = self.get_available_invokes(self.char)
        available = []
        [available.extend(a['char'].get_available_aspects(a['parent'])) for a in aspect_list]
        return ['**Available invokes:**\n        ' + '\n        '.join([a for a in available]) if available else 'No available aspects to invoke']

    def find_aspect(self, aspect):
        aspect = aspect.replace('_', ' ')
        aspects = []
        if self.char:
            aspects = [i['char'] for i in self.get_available_invokes(self.char) if aspect.lower() in i['char'].name.lower()]
            if aspects:
                return aspects[0]
        return aspects

    def roll(self, skill='', invokes=[]):
        skill_str, bonus = self.get_skill_bonus(skill)
        bonus_invokes, bonus_invokes_total, invokes_bonus_string, invoke_string = \
            self.get_invoke_bonus(skill, invokes)
        bonus += bonus_invokes_total
        dice_roll = self.roll_dice()
        final_roll = dice_roll['rolled'] + bonus
        skill_bonus_str = f' + ({skill}{skill_str})' if skill_str else ''
        skill_bonus_str += f' = {final_roll}' if skill_bonus_str or bonus_invokes else ''
        rolled = dice_roll['rolled']
        fate_roll_string = dice_roll['fate_roll_string']
        return {
            'roll_text': f'{self.char.name} rolled: {fate_roll_string} = {rolled}{invokes_bonus_string}{skill_bonus_str}{invoke_string}',
            'roll': dice_roll['rolled'],
            'skill': skill,
            'skill_str': skill_str,
            'bonus': bonus,
            'fate_dice_roll': dice_roll['fate_dice_roll'],
            'fate_roll_string': dice_roll['fate_roll_string'],
            'dice': dice_roll['dice'],
            'final_roll': final_roll,
            'invokes': invokes,
            'invokes_bonus': bonus_invokes_total,
            'invokes_bonus_string': invokes_bonus_string,
            'invoke_string': invoke_string
        }

    def reroll(self, skill, invokes=[]):
        self.char.last_roll['invokes'].extend(invokes)
        return self.roll(self.char.last_roll['skill'], self.char.last_roll['invokes'])

    def match_skill(self, skill=''):
        if skill !='':
            if self.char.use_approaches:
                skill_name = [s for s in APPROACHES if skill[0:2].lower() == s[0:2].lower()]
            else:
                skill_name = [s for s in SKILLS if skill[0:2].lower() == s[0:2].lower()]
            skill = skill_name[0].split(' - ')[0] if skill_name else skill
        return skill

    def get_skill_bonus(self, skill=''):
        skill_str = ''
        bonus = 0
        if skill !='':
            skill_str = ' ' + self.char.skills[skill] if skill in self.char.skills else ''
            bonus = int(skill_str) if skill_str else 0
        return skill_str, bonus

    def get_invoke_bonus(self, skill, invokes):
        bonus_invokes = []
        [invoke.update({'bonus_str': invoke['skills'][skill] if skill in invoke['skills'] else ('+0' if invoke['category'] == 'Stunt' else '+2')}) for invoke in invokes]
        bonus_invokes = len([invoke for invoke in invokes if invoke['bonus_str'] == '+2'])
        bonus_invokes_total = sum([int(i['bonus_str']) for i in invokes])
        invokes_bonus_string = f' + (Invokes bonus = {bonus_invokes_total})' if invokes and bonus_invokes_total else ''
        invoke_string = self.get_invoke_string(invokes)
        return bonus_invokes, bonus_invokes_total, invokes_bonus_string, invoke_string

    def get_invoke_string(self, invokes):
        invoke_strings = []
        for invoke in invokes:
            name = invoke['aspect_name']
            bonus_str = invoke['bonus_str']
            fate_points = invoke['fate_points']
            s = 's' if invoke['fate_points'] == 0 or invoke['fate_points'] > 1 else ''
            invoike_string = f'\nInvoked "{name}" for {bonus_str} (cost {fate_points} fate point{s})'
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
