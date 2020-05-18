# cheat_command.py

from config.setup import Setup

SETUP = Setup()
CHEATS = SETUP.cheats

class CheatCommand():
    def __init__(self, parent, ctx, args, guild=None, user=None):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]

    def run(self):
        messages = []
        if not self.args:
            [messages.append(f'\n \n***{k}***{CHEATS[k]}') for k in CHEATS]
        else:
            search = ' '.join(self.args).lower()
            [messages.append(f'\n \n***{k}***{CHEATS[k]}') for k in CHEATS if search in k.lower() or search in CHEATS[k].lower()]
        return messages