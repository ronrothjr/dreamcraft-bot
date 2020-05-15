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
        self.messages = self.get_messages()
        # Concatenate messages and send
        if self.command == 'cheat':
            [await self.send(f'{m}\n') for m in self.messages]
        else:
            await self.send('\n'.join(self.messages))

    def get_messages(self):
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
        self.messages = []
        self.search = str(self.args[0])
        self.answer()
        if not self.messages:
            self.shortcuts()
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: CharacterCommand)
                # Execute the function and store the returned messages
                instance = func(ctx=self.ctx, args=self.args, parent=self)      
                # Call the run() method for the command
                self.messages = instance.run()
            else:
                self.messages = [f'Unknown command: {self.command}']
        return self.messages

    async def send(self, message):
        if message:
            image_split = message.split('!image')
            message = image_split[0]
            if len(image_split) > 2:
                 message += ''.join(image_split[2:])
            embed = Embed(type='rich', colour=13400320, description=message)
            # embed.set_author(name='Dreamcraft Bot', icon_url='http://drive.google.com/uc?export=view&id=1jSmg-SJx5YwjgIepYA6SYjtPZ_aNQnNr')
            if len(image_split) > 1:
                embed.set_image(url=image_split[1])
            await self.ctx.send(embed=embed)

    def answer(self):
        guild = self.ctx.guild if self.ctx.guild else self.ctx.author
        user = User().find(self.ctx.author.name, guild.name)
        if user and user.command:
            answer = ' '.join(self.args[0:])
            self.args = tuple(user.command.split(' '))
            self.command = self.args[0].lower()
            if (not user.created):
                user.created = datetime.datetime.utcnow()
            user.answer = answer
            user.updated_by = str(user.id)
            user.updated = datetime.datetime.utcnow()
            user.save()

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