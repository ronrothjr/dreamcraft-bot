# dreamcraft.py

from models import Channel
from commands import *
from config.setup import Setup

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills

class DreamcraftHandler():
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.command = args[0].lower()

    async def handle(self):
        switcher = {
            'channel': ChannelCommand,
            'chan': ChannelCommand,
            'character': CharacterCommand,
            'char': CharacterCommand,
            'c': CharacterCommand,
            'scene': SceneCommand,
            's': SceneCommand,
            'roll': RollCommand,
            'r': RollCommand,
            'reroll': RollCommand,
            're': RollCommand,
            'invoke': RollCommand,
            'i': RollCommand,
            'compel': RollCommand
        }
        # shortcut for updating approaches on a character (must enter full name)
        approach = [s for s in APPROACHES if self.args[0].lower() == s.lower()] if len(self.args) > 0 else None
        if approach:
            self.command = 'c'
            self.args = ('c', 'app', approach[0], self.args[1])
        # shortcut for updating skills on a character (must enter full name)
        skill = [s for s in SKILLS if self.args[0].lower() == s.lower()] if len(self.args) > 0 else None
        if skill:
            self.command = 'c'
            self.args = ('c', 'sk', skill[0], self.args[1])
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: CharacterCommand)
            # Execute the function and store the returned messages
            instance = func(self.ctx, self.args)      
            # Call the run() method for the command
            messages = instance.run()
        else:
            messages = [f'Unknown command: {self.command}']  
        # Concatenate messages and send
        await self.send('\n'.join(messages))

    async def send(self, message):
        await self.ctx.send(message)