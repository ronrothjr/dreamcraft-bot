# dreamcraft.py
import re
from dotenv import load_dotenv
from discord import Embed

from models import Channel, User, Character
from commands import *
from config.setup import Setup
from utils import T

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
from config.setup import Setup

class DreamcraftHandler():
    """
    DreamcraftHandler class for parsing commands and assigning execution
    """
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.guild = ctx.guild if ctx.guild else ctx.author
        self.user = User().get_or_create(ctx.author.name, self.guild.name)
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        if str(self.user.name) not in self.channel.users:
            self.channel.users.append(str(self.user.name))
            self.channel.updated_by = str(self.user.id)
            self.channel.updated = T.now()
            self.channel.save()
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None
        self.module = self.char.category if self.char else None
        self.command = args[0].lower()
        self.func = None
        self.messages = []

    async def handle(self):
        self.messages = self.get_messages()
        # Concatenate messages and send
        if self.command == 'cheat':
            [await self.send(f'{m}\n') for m in self.messages]
        else:
            await self.send('\n'.join(self.messages))

    def get_messages(self):
        modules = {
            'Channel': ChannelCommand,
            'Scenario': ScenarioCommand,
            'Scene': SceneCommand,
            'Character': CharacterCommand,
            'Undo': UndoCommand,
            'User': UserCommand,
            'Zone': ZoneCommand,
            'Session': SessionCommand
        }
        switcher = {
            'cheat': CheatCommand,
            'undo': UndoCommand,
            'redo': UndoCommand,
            'log': UndoCommand,
            'l': UndoCommand,
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
            'session': SessionCommand,
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
        self.get_answer()
        if not self.messages:
            self.shortcuts()
            # Get the function from switcher dictionary
            if switcher.get(self.command, None):
                self.func = switcher.get(self.command, None)
                self.module = re.sub(r'commands\.|_command', '', self.func.__module__).title()
                if self.module != self.user.module:
                    self.user.module = self.module
                    self.user.updated_by = str(self.user.id)
                    self.user.updated = T.now()
                    self.user.save()
            # Get the function from User object
            if self.func is None and self.user.module in modules:
                self.module = self.user.module
                self.func = modules.get(self.module, None)
                self.args = (self.module.lower(),) + self.args
            # Get the function from Character object
            if self.func is None and self.module in modules:
                self.func = modules.get(self.module, None)
                self.args = (self.module.lower(),) + self.args
            if self.func:
                # Execute the function and store the returned messages
                instance = self.func(ctx=self.ctx, args=self.args, guild=self.guild, user=self.user, channel=self.channel, parent=self)
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
            embed = Embed(type='rich', title=self.module, colour=13400320, description=message)
            # embed.set_author(name='Dreamcraft Bot', icon_url='http://drive.google.com/uc?export=view&id=1jSmg-SJx5YwjgIepYA6SYjtPZ_aNQnNr')
            if len(image_split) > 1:
                embed.set_image(url=image_split[1])
            await self.ctx.send(embed=embed)

    def get_answer(self):
        guild = self.ctx.guild if self.ctx.guild else self.ctx.author
        self.user = User().find(self.ctx.author.name, guild.name)
        if self.user and self.user.command:
            answer = ' '.join(self.args[0:])
            self.args = tuple(self.user.command.split(' '))
            self.command = self.args[0].lower()
            self.user.answer = answer
            self.user.updated_by = str(self.user.id)
            self.user.updated = T.now()
            self.user.save()

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