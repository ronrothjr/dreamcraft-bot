# channel_command
from models import Channel, User, Character, Scene
from services import ChannelService, ScenarioService
from utils import Dialog, T

channel_svc = ChannelService()
scenario_svc = ScenarioService()

class ChannelCommand():
    """
    Handle 'channel' and 'chan' commands and subcommands

    Subcommands:
        channel, chan - display channel information
        list - dipslay a list of channels within the current guild
        users, u - display a list of users interacting wtih the channel
    """

    def __init__(self, parent, ctx, args, guild, user, channel):
        """
        Command handler for channel command

        Parameters
        ----------
        parent : DreamcraftHandler
            The handler for Dreamcraft Bot commands and subcommands
        ctx : object(Context)
            The Discord.Context object used to retrieve and send information to Discord users
        args : array(str)
            The arguments sent to the bot to parse and evaluate
        guild : Guild
            The guild object containing information about the server issuing commands
        user : User
            The user database object containing information about the user's current setttings, and dialogs
        channel : Channel
            The channel from which commands were issued        

        Returns
        -------
        ChannelCommand - object for processing channel subcommands
        """

        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'chan'
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
            'channel': self.chan,
            'chan': self.chan,
            'list': self.channel_list,
            'users': self.users,
            'u': self.users
        }
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: self.chan)
            # Execute the function
            messages = func(self.args)
        else:
            messages = [f'Unknown command: {self.command}']
        # Send messages
        return messages

    def chan(self, args):
        return [self.channel.get_string(self.user)]

    def channel_list(self, args):
        messages = []
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['chan']:
                return ChannelCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        def selector(selection):
            self.channel = selection
            return self.chan(self.args)

        def formatter(item, item_num, page_num, page_size):
            return f'_CHANNAL #{((page_num-1)*page_size)+item_num+1}_\n{item.get_short_string(self.user)}'

        messages.extend(Dialog({
            'svc': channel_svc,
            'user': self.user,
            'title': 'Channel List',
            'command': 'chan ' + (' '.join(args)),
            'type': 'select',
            'type_name': 'CHANNEL',
            'getter': {
                'method': Channel.get_by_page,
                'params': {'params': {'guild': self.guild.name, 'archived': False}}
            },
            'formatter': formatter,
            'cancel': canceler,
            'select': selector
        }).open())
        return messages

    def users(self, args):
        return [self.channel.get_users_string()]

