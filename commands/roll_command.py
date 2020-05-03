# roll_command.py

from models import Channel, Scene, User, Character
from utils import Roll

class RollCommand():
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.command = args[0].lower()
        self.channel = Channel().get_or_create(self.ctx.channel.name, self.ctx.guild.name)
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.user = User().get_or_create(self.ctx.author.name, self.ctx.guild.name)
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        last_roll = None
        invokes = self.get_invokes()
        compels = self.get_compels()
        if self.command == 'roll' or self.command == 'r':
            skill = self.args[1] if len(self.args) > 1 else ''
            last_roll = Roll(self.char).roll(skill, invokes)
            self.char.last_roll = last_roll
        elif self.command == 'reroll' or self.command == 're':
            last_roll = Roll(self.char).reroll()
            self.char.last_roll = last_roll
        elif self.command == 'invoke' or self.command == 'i':
            last_roll = Roll(self.char).invoke(invokes)
            self.char.last_roll = last_roll
        if invokes:
            if len(invokes) < self.char.fate_points+1:
                self.char.fate_points -= len(invokes)
                self.char.save()
            else:
                return ['You do not have enough fate points']
        elif compels:
            if len(compels) + self.char.fate_points < 5:
                self.char.fate_points += len(compels)
                self.char.save()
                return [''.join([f'\nCompeled "{i}" and added 1 fate point' for i in compels])]
            else:
                return ['Your compel(s) would exceed maximum fate points']
        return [self.char.last_roll['roll_text']]


    def get_invokes(self):
        invokes = []
        i = 2
        while i < len(self.args):
            if self.args[i].lower() == 'invoke' or self.args[i].lower() == 'i':
                aspect = self.find_aspect(self.args[i+1])
                if aspect:
                    invokes.append(aspect)
            i += 2
        return invokes

    def get_compels(self):
        compels = []
        i = 0
        while i < len(self.args):
            if self.args[i].lower() == 'compel' or self.args[i].lower() == 'c':
                aspect = self.find_aspect(self.args[i+1])
                if aspect:
                    compels.append(aspect)
            i += 2
        return compels

    def find_aspect(self, aspect):
        aspect = aspect.replace('_', ' ')
        if self.char:
            if aspect.lower() in self.char.high_concept.lower():
                return self.char.high_concept
            if aspect.lower() in self.char.trouble.lower():
                return self.char.trouble
            aspects = [a for a in self.char.aspects if aspect.lower() in a.lower()]
            if aspects:
                return aspects[0]
            aspects = [a for a in self.sc.aspects if aspect.lower() in a.lower()]
            if aspects:
                return aspects[0]
