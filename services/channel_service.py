# channel_service

from models import Channel, User, Character, Scene

class ChannelService():
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'c'
        self.channel = Channel().get_or_create(self.ctx.channel.name, self.ctx.guild.name)
        self.user = User().get_or_create(self.ctx.author.name, self.ctx.guild.name)
        if self.user.name not in self.channel.users:
            self.channel.users.append(self.user.name)
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
            func = switcher.get(self.command, lambda: self.character)
            # Execute the function
            messages = func()
        else:
            messages = [f'Unknown command: {self.command}']
        # Send messages
        return messages

    def chan(self):
        return [self.channel.get_string()]

    def users(self):
        return [self.channel.get_users_string()]

