# dreamcraft.py
import datetime
from discord import Embed

from models import Channel, User
from commands import *
from config.setup import Setup

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills

class DreamcraftHandler():
    """
    DreamcraftHandler class for parsing commands and assigning execution
    """
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.command = args[0].lower()
        self.messages = []

    async def handle(self):
        switcher = {
            'cheat': CheatCommand,
            'user': UserCommand,
            'u': UserCommand,
            'channel': ChannelCommand,
            'chan': ChannelCommand,
            'character': CharacterCommand,
            'char': CharacterCommand,
            'c': CharacterCommand,
            'stats': CharacterCommand,
            'scenario': ScenarioCommand,
            'scene': SceneCommand,
            's': SceneCommand,
            'zone': ZoneCommand,
            'z': ZoneCommand,
            'roll': RollCommand,
            'r': RollCommand,
            'reroll': RollCommand,
            're': RollCommand,
            'invoke': RollCommand,
            'i': RollCommand,
            'compel': RollCommand,
            'available': RollCommand,
            'av': RollCommand,
            'stress': CharacterCommand,
            'st': CharacterCommand,
            'consequence': CharacterCommand,
            'con': CharacterCommand
            # 'combine': RollCommand,
            # 'concede': RollCommand
        }

        self.answer()        
        if not self.messages:
            self.shortcuts()
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: CharacterCommand)
                # Execute the function and store the returned messages
                instance = func(self.ctx, self.args)      
                # Call the run() method for the command
                self.messages = instance.run()
            else:
                self.messages = [f'Unknown command: {self.command}']  
        # Concatenate messages and send
        if self.command == 'cheat':
            [await self.send(f'{m}\n') for m in self.messages]
        else:
            await self.send('\n'.join(self.messages))

    async def send(self, message):
        if message:
            await self.ctx.send(embed=Embed(title='Dreamcraft Bot', colour=13400320, description=message))
    
    def answer(self):
        self.messages = []
        self.search = str(self.args[0])
        if self.search.lower() in ['yes', 'y']:
            guild = self.ctx.guild if self.ctx.guild else self.ctx.author
            user = User().find(self.ctx.author.name, guild.name)
            if user.question:
                self.args = tuple(user.question.split(' '))
                self.search = str(self.args[0])
                self.command = self.args[0].lower()
            else:
                self.messages.append('You have no pending questions to answer')
        elif self.search.lower() in ['no', 'n']:
            guild = self.ctx.guild if self.ctx.guild else self.ctx.author
            user = User().find(self.ctx.author.name, guild.name)
            if user.question:
                self.messages.append(f'_{user.question}_ command canceled')
                user.question = ''
                if (not user.created):
                    user.created = datetime.datetime.utcnow()
                user.updated = datetime.datetime.utcnow()
                user.save()
            else:
                self.messages.append('You have no pending questions')

    def shortcuts(self):
        # shortcut for updating approaches on a character (must enter full name)
        approach = [s for s in APPROACHES if self.search.lower() == s.split(' - ')[0].lower()] if len(self.args) > 0 else None
        if approach:
            self.command = 'c'
            self.args = ('c', 'app', approach[0], self.args[1])
        # shortcut for updating skills on a character (must enter full name)
        skill = [s for s in SKILLS if self.search.lower() == s.split(' - ')[0].lower()] if len(self.args) > 0 else None
        if skill:
            self.command = 'c'
            self.args = ('c', 'sk', skill[0], self.args[1])