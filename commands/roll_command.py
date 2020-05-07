# roll_command.py
import datetime
from models import Channel, Scene, User, Character
from utils import Roll

class RollCommand():
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.invoke_index = [i for i in range(0, len(self.args)) if self.args[i] in ['invoke', 'i']]
        self.compel_index = [i for i in range(0, len(self.args)) if self.args[i] in ['compel', 'c']]
        self.command = args[0].lower()
        self.channel = Channel().get_or_create(self.ctx.channel.name, self.ctx.guild.name)
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.user = User().get_or_create(self.ctx.author.name, self.ctx.guild.name)
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        messages = [self.char.get_string_name(self.user)]
        errors = []
        last_roll = None
        invokes = self.get_invokes()
        errors.extend([i[1] for i in invokes if i[0] == 'error'])
        compels = self.get_compels()
        errors.extend([c[1] for c in compels if c[0] == 'error'])
        if self.invoke_index and self.compel_index:
            errors.append('You cannot invoke and compel on the same roll')
        if errors:
            return [e for e in errors]
        if self.command in ['available', 'avail', 'av']:
            return self.available_aspects()
        if self.command in ['roll', 'r']:
            skill = self.args[1] if len(self.args) > 1 else ''
            last_roll = Roll(self.char).roll(skill, invokes)
            self.char.last_roll = last_roll
            messages.append(self.char.last_roll['roll_text'])
        elif self.command in ['reroll', 're']:
            if not invokes:
                return ['You did not include an invoke for the reroll']
            else:
                last_roll = Roll(self.char).reroll(invokes)
                self.char.last_roll = last_roll
                messages.append(self.char.last_roll['roll_text'])
        if invokes:
            if len(invokes) < self.char.fate_points+1:
                self.char.fate_points -= len(invokes)
                messages.append(''.join([f'Invoked "{i[0]}" and used 1 fate point' for i in invokes]))
                messages.append(self.char.get_string_fate())
            else:
                return [f'{self.char.name} does not have enough fate points']
        if compels:
            if len(compels) + self.char.fate_points <= 5:
                self.char.fate_points += len(compels)
                messages.append(''.join([f'Compeled "{c}" and added 1 fate point' for c in compels]))
                messages.append(self.char.get_string_fate())
            else:
                return [f'{self.char.name} already has the maximum fate points (5)']
        if (not self.char.created):
            self.char.created = datetime.datetime.utcnow()
        self.char.updated = datetime.datetime.utcnow()
        self.char.save()
        return messages


    def get_invokes(self):
        invokes = []
        for i in self.invoke_index:
            if len(self.args) < i+1:
                invokes.append(['error', f'An invoke is mssing an aspect'])
                continue
            aspect = self.find_aspect(self.args[i+1])
            if not aspect:
                invokes.append(['error', f'{self.args[i+1]} not found in availabe aspects'])
                continue
            if self.command in ['reroll', 're'] and len(self.args) <= i+2:
                invokes.append(['error', f'Reroll invoke on {aspect} is missing +2 or (re)roll'])
                continue
            if self.command in ['reroll', 're'] and len(self.args) > i+2 and self.args[i+2] not in ['+2', 're', 'reroll']:
                invokes.append(['error', f'Reroll invoke on {aspect} is missing +2 or (re)roll'])
                continue
            check_invokes = []
            check_invokes.extend(invokes)
            if self.command in ['reroll', 're']:
                check_invokes.extend(self.char.last_roll['invokes'])
            if [dup for dup in check_invokes if aspect == dup[0]]:
                invokes.append(['error', f'{aspect} cannot be invoked more than once on the same roll'])
                continue
            if self.command in ['reroll', 're']:
                invokes.append([aspect, '+2 bonus' if self.args[i+2] == '+2' else 'reroll'])
            else:
                invokes.append([aspect, '+2 bonus'])
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

    def available_aspects(self):
        available = []
        if self.char.high_concept:
            available.append(f'{self.char.high_concept} (character \'{self.char.name}\')')
        if self.char.trouble:
            available.append(f'{self.char.trouble} (character \'{self.char.name}\')')
        char_aspects = [f'{a.name} (character \'{self.char.name}\')' for a in Character().get_by_parent(self.char)] if self.char else []
        available.extend(char_aspects)
        sc_aspects = [f'{a.name} (scene \'{self.sc.name}\')' for a in Character().get_by_parent(self.sc)] if self.sc else []
        available.extend(sc_aspects)
        return ['**Available aspects:**\n        ' + '\n        '.join([a for a in available]) if available else 'No available aspects to invoke']

    def find_aspect(self, aspect):
        aspect = aspect.replace('_', ' ')
        if self.char:
            if self.char.high_concept and aspect.lower() in self.char.high_concept.lower():
                return self.char.high_concept
            if self.char.trouble and aspect.lower() in self.char.trouble.lower():
                return self.char.trouble
            aspects = [a.name for a in Character().get_by_parent(self.char, aspect)]
            if aspects:
                return aspects[0]
            aspects = [a.name for a in Character().get_by_parent(self.sc, aspect)]
            if aspects:
                return aspects[0]
