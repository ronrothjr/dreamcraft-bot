# channel_command
from models import Channel, User, Character, Scene
from services import ScenarioService
from utils import T

scenario_svc = ScenarioService()

class ChannelCommand():
    def __init__(self, parent, ctx, args, guild, user, channel):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'c'
        self.guild = guild
        self.user = user
        self.channel = channel
        if self.user.name not in self.channel.users:
            self.channel.users.append(self.user.name)
            self.channel.updated_by = str(self.user.id)
            self.channel.updated = T.now()
            self.channel.save()
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        switcher = {
            'c': self.chan,
            'users': self.users,
            'u': self.users
        }
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: self.chan)
            # Execute the function
            messages = func()
        else:
            messages = [f'Unknown command: {self.command}']
        # Send messages
        return messages

    def chan(self):
        return [self.channel.get_string(self.user)]

    def users(self):
        return [self.channel.get_users_string()]

