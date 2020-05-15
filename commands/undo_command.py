# undo_command
import datetime
import math
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Character, User, Log
from utils import Pager
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

    def undo_list(self, args):
        command = 'undo ' + (' '.join(args))
        def format(undo):
            data = ''
            if undo.data:
                for d in undo.data:
                    if d not in ['updated_by', 'created_by', 'updated', 'created']:
                        cleaned = d.replace('_', ' ')
                        data += f'\n    _{cleaned}:_ {undo.data[d]}'
            return ''.join([
                f'**{undo.name}** _({undo.category})_' if undo.name else f'**{undo.category}**',
                f' _updated on: {undo.updated.strftime("%m/%d/%Y, %H:%M:%S")}_{data}\n'
        ])
        cancel_args, results = Pager(char_svc).manage_paging(
            title='Undo History',
            command=command,
            user=self.user,
            data_getter={
                'method': Log.get_by_page,
                'params': {
                    'params': {'user_id': str(self.user.id)}
                }
            },
            formatter=format)
        if cancel_args:
            if cancel_args[0].lower() == 'undo':
                self.args = cancel_args[1:]
                self.command = self.args[0]
                return self.run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()
        else:
            return [results]
        

