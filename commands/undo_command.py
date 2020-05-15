# undo_command
import datetime
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Character, User, Log
from config.setup import Setup
from services.character_service import CharacterService

char_svc = CharacterService()
SETUP = Setup()
UNDO_HELP = SETUP.undo_help

class UndoCommand():
    def __init__(self, parent, ctx, args):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'n'
        self.guild = ctx.guild if ctx.guild else ctx.author
        self.user = User().get_or_create(ctx.author.name, self.guild.name)
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        switcher = {
            'help': self.help,
            'list': self.undo_list,
            'l': self.undo_list
        }
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: self.name)
            # Execute the function
            messages = func(self.args)
        else:
            self.args = ('l',) + self.args
            self.command = 'l'
            func = self.undo_list
            # Execute the function
            messages = func(self.args)
        # Send messages
        return messages

    def help(self, args):
        return [UNDO_HELP]

    def format(self, undo):
        return ''.join([
            f'***{undo.category}', undo.name if undo.name else '', f'*** ({undo.updated})\n{undo.data}\n'
        ])

    def undo_list(self, args):
        logs = Log().get_by_user_id(str(self.user.id))
        if not logs:
            return ['You don\'t have any history to undo.']
        else:
            logs_string = '\n'.join([self.format(log) for log in logs])
            return [f'Undo history:\n\n{logs_string}\n        ']
