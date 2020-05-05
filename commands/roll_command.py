# roll_command.py

from models import Channel, Scene, User, Character, Aspect
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
        messages =[]
        last_roll = None
        invokes = self.get_invokes()
        errors = [i[1] for i in invokes if i[0] == 'error']
        if errors:
            return [e for e in errors]
        compels = self.get_compels()
        if self.command in ['available', 'avail', 'av']:
            return self.available_aspects()
        if self.command in ['roll', 'r']:
            skill = self.args[1] if len(self.args) > 1 else ''
            last_roll = Roll(self.char).roll(skill, invokes)
            self.char.last_roll = last_roll
        elif self.command in ['reroll', 're']:
            if not invokes:
                return ['You did not include an invoke for the reroll']
            else:
                last_roll = Roll(self.char).reroll(invokes)
                self.char.last_roll = last_roll
        elif self.command in ['invoke', 'i']:
            last_roll = Roll(self.char).invoke(invokes)
            self.char.last_roll = last_roll
        if invokes:
            if len(invokes) < self.char.fate_points+1:
                self.char.fate_points -= len(invokes)
            else:
                return ['You do not have enough fate points']
        if compels:
            if len(compels) + self.char.fate_points <= 5:
                self.char.fate_points += len(compels)
                messages.append(''.join([f'\nCompeled "{i}" and added 1 fate point' for i in compels]))
            else:
                return ['Your compel(s) would exceed maximum fate points']
        self.char.save()
        return [self.char.last_roll['roll_text']]


    def get_invokes(self):
        invokes = []
        for i in self.invoke_index:
            aspect = self.find_aspect(self.args[i+1])
            if aspect and i+2 < len(self.args) and self.args[i+2] in ['+2', 're', 'reroll']:
                check_invokes = []
                check_invokes.extend(invokes)
                if self.command in ['reroll', 're']:
                    check_invokes.extend(self.char.last_roll['invokes'])
                duplicate_invokes = [dup for dup in check_invokes if aspect == dup[0]]
                if duplicate_invokes:
                    invokes.append(['error', f'{aspect} was already invoked'])
                else:
                    invokes.append([aspect, 'reroll' if self.args[i+2] in ['re', 'reroll'] else '+2 bonus'])
            else:
                invokes.append(['error', f'{self.args[i+1]} not found or invoke missing +2 or (re)roll'])
        return invokes

    def get_compels(self):
        compels = []
        for i in self.compel_index:
            aspect = self.find_aspect(self.args[i+1])
            if aspect:
                duplicate_aspect = [dup for dup in self.char.last_roll['invokes'] if aspect == dup[0]]
                if duplicate_aspect:
                    compels.append(['error', f'{aspect} was already invoked'])
                else:
                    compels.append(aspect)
        return compels

    def available_aspects(self):
        available = []
        if self.char.high_concept:
            available.append(f'{self.char.high_concept} (character \'{self.char.name}\')')
        if self.char.trouble:
            available.append(f'{self.char.trouble} (character \'{self.char.name}\')')
        char_aspects = [f'{a.name} (character \'{self.char.name}\')' for a in Aspect().get_by_parent_id(self.char.id)]
        available.extend(char_aspects)
        sc_aspects = [f'{a.name} (scene \'{self.sc.name}\')' for a in Aspect().get_by_parent_id(self.sc.id)]
        available.extend(sc_aspects)
        return ['**Available aspects:**\n        ' + '\n        '.join([a for a in available]) if available else 'No available aspects to invoke']

    def find_aspect(self, aspect):
        aspect = aspect.replace('_', ' ')
        if self.char:
            if self.char.high_concept and aspect.lower() in self.char.high_concept.lower():
                return self.char.high_concept
            if self.char.trouble and aspect.lower() in self.char.trouble.lower():
                return self.char.trouble
            aspects = [a.name for a in Aspect().get_by_parent_id(self.char.id, aspect)]
            if aspects:
                return aspects[0]
            aspects = [a.name for a in Aspect().get_by_parent_id(self.sc.id, aspect)]
            if aspects:
                return aspects[0]
