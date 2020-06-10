# dreamcraft.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import os
import re
from dotenv import load_dotenv
import traceback

from models import Channel, User, Character, Log
from services import BaseService
from commands import *
from config.setup import Setup
from utils import T

load_dotenv()
PREFIX = os.getenv('DISCORD_PREFIX')
COMMAND = os.getenv('DISCORD_COMMAND')

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
from config.setup import Setup

base_svc = BaseService()

class DreamcraftHandler():
    """
    DreamcraftHandler class for parsing commands and assigning execution
    """

    def __init__(self, ctx, args):
        """
        Command handler for .d, the Dreamcraft Bot command

        Parameters
        ----------
        ctx : object(Context)
            The Discord.Context object used to retrieve and send information to Discord users
        args : array(str)
            The arguments sent to the bot to parse and evaluate

        Returns
        -------
        DreamcraftHandler - object for processing Context object and args (list of strings in a command)
        """
        self.ctx = ctx
        self.args = args
        self.guild = ctx.guild if ctx.guild else ctx.author
        self.user = User().get_or_create(ctx.author.name, self.guild.name, ctx.author.discriminator, ctx.author.display_name)
        # The 'channel' variable can either be the name of the channel on a server or 'private' if Direct Message
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        # Add the user to the list of channel users
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

    def get_messages(self):
        """
        Processes Context and args through command string parsing

        Returns
        -------
        tuple(title: str, message: str)
            title : str
                The title of the response message
            message : str
                The string for the response message content
        """

        try:

            modules = {
                'Channel': ChannelCommand,
                'Scenario': ScenarioCommand,
                'Scene': SceneCommand,
                'Character': CharacterCommand,
                'Undo': UndoCommand,
                'User': UserCommand,
                'Zone': ZoneCommand,
                'Session': SessionCommand,
                'Engagement': EngagementCommand,
                'Revision': RevisionCommand,
                'Suggestion': SuggestionCommand
            }
            switcher = {
                'cheat': CheatCommand,
                'undo': UndoCommand,
                'redo': UndoCommand,
                'log': UndoCommand,
                'l': UndoCommand,
                'revision': RevisionCommand,
                'rev': RevisionCommand,
                'suggestion': SuggestionCommand,
                'suggest': SuggestionCommand,
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
                'engagement': EngagementCommand,
                'engage': EngagementCommand,
                'e': EngagementCommand,
                'attack': RollCommand,
                'attk': RollCommand,
                'defend': RollCommand,
                'def': RollCommand,
                'roll': RollCommand,
                'r': RollCommand,
                'reroll': RollCommand,
                're': RollCommand,
                'invoke': RollCommand,
                'i': RollCommand,
                'compel': RollCommand,
                'available': RollCommand,
                'avail': RollCommand,
                'av': RollCommand,
                'stress': CharacterCommand,
                'st': CharacterCommand,
                'consequence': CharacterCommand,
                'con': CharacterCommand
                # 'assist': RollCommand,
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
                # Log every comand
                base_svc.log(str(self.user.id), self.user.name, str(self.user.id), self.guild.name, 'Command', {
                    'command': self.command,
                    'module': self.module,
                    'args': self.args
                }, 'created')
                if self.func:
                    # Execute the function and store the returned messages
                    instance = self.func(ctx=self.ctx, args=self.args, guild=self.guild, user=self.user, channel=self.channel, parent=self)
                    # Call the run() method for the command
                    self.messages = instance.run()
                else:
                    self.messages = [f'Unknown command: {self.command}']
                
            # Concatenate messages and send
            if self.command == 'cheat':
                return self.module, [f'{m}\n' for m in self.messages]
            else:
                return self.module, '\n'.join(self.messages)
    
        except Exception as err:
            traceback.print_exc()    
            # Log every error
            base_svc.log(
                str(self.user.id),
                self.user.name,
                str(self.user.id),
                self.guild.name,
                'Error',
                {
                    'command': self.command,
                    'args': self.args,
                    'traceback': traceback.format_exc()
                }, 'created')
            return 'Oops!', 'Hey, bugs happen! We\'re working on it...'

    def get_answer(self):
        """
        Check for an answer if a dialog has been recorded in the user's record

        A dialog records the original command, the question string, and the answer.
        The command will track the previous command that started the dialog.
        The question will store the current state of the dialog.
        The answer is stored for processing by the command handler.
        """

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
        """
        Check for standard approach names and skill names to update the active character

        Approach and skill names must be completely spelled out in order to trigger the shortcut feature.
        """
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