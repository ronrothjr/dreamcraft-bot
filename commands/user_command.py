# user_command.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import pytz
from config.setup import Setup
from models.user import User
from services import BaseService
from utils import T

SETUP = Setup()
USER_HELP = SETUP.user_help

base_svc = BaseService()

class UserCommand():
    """
    Handle 'user', 'u' commands and subcommands

    Subcommands:
        help - display a set of instructions on UserCommand usage
        user, u - display and create new users by name
        timezone, tz - set or display a list of existing timezones
        url, website, contact - set the contact url for the user
    """

    def __init__(self, parent, ctx, args, guild, user, channel):
        """
        Command handler for UserCommand

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
        UserCommand - object for processing user commands and subcommands
        """

        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.guild = guild
        self.user = user
        self.channel = channel
        self.command = self.args[0].lower() if len(self.args) > 0 else 'u'

    def run(self):
        """
        Execute the channel commands by validating and finding their respective methods

        Returns
        -------
        list(str) - a list of messages in response the command validation and execution
        """
        
        try:
            # List of subcommands mapped the command methods
            switcher = {
                'help': self.help,
                'user': self.get_user,
                'u': self.get_user,
                'timezone': self.time_zone,
                'tz': self.time_zone,
                'url': self.url,
                'website': self.url,
                'contact': self.url
            }
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: self.time_zone)
                # Execute the function
                messages = func()
            else:
                messages = [f'Unknown command: {self.command}']
            # Send messages
            return messages
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
            return list(err.args)

    def help(self):
        """Returns the help text for the command"""

        return [USER_HELP]

    def get_user(self):
        """Diplsay the current user information"""

        return [self.user.get_string()]
    
    def time_zone(self):
        """Set/edit the user's timezone information"""

        tz_help = 'Try this:```css\n.d u timezone "ZONE SEARCH"\n/* "ZONE SEARCH" must be at least 3 characters */```'
        tz_search = ''.join([
            'Try one of these searches:```css\n',
            '.d u tz US/\n',
            '.d u tz America\n',
            '.d u tz Canada\n',
            '.d u tz Europe\n',
            '.d u tz Asia\n',
            '.d u tz Atlantic\n',
            '.d u tz Pacific\n',
            '.d u tz Indian\n',
            '.d u tz Africa\n',
            '.d u tz Australia\n',
            '.d u tz Antarctica\n',
            '```'
        ])
        if len(self.args) == 0:
            if not self.user:
                return ['No active user or name provided']
        if len(self.args) < 2:
            return [f'No time zone provided. {tz_help}',tz_search]
        if self.args[1] in ['list', 'l']:
            if len(self.args) <3:
                return [f'No time zone search term provided. {tz_help}', tz_search]
            if len(self.args[2]) <3:
                return ['No time zone search term must be at least 3 characters```css\n/* EXAMPLES */\n.d u tz New_York\n.d u timezone London```']
            search = self.args[2].lower()
            tz = [tz for tz in pytz.all_timezones if search in tz.lower()]
            if len(tz) == 0:
                return [f'Time zone \'{search}\' not found', tz_search]
            return ['\n'.join(tz)]
        else:
            search = self.args[1].lower()
            tz = [tz for tz in pytz.all_timezones if search in tz.lower()]
            if len(tz) == 0:
                return [f'Time zone \'{search}\' not found', tz_search]
            if len(tz) > 1:
                timezones = '\n'.join([f'.d u tz {t}' for t in tz])
                return [f'Time zone search \'{search}\' returned more than one. Try one of these:```css\n{timezones}```']
            self.user.time_zone = tz[0]
            self.user.updated_by = str(self.user.id)
            self.user.updated = T.now()
            self.user.save()
        return [f'Saved time zone as ***{tz[0]}***\n\n{self.user.get_string()}']

    def url(self):
        """Set/edit the user's contact information"""

        if len(self.args) < 2:
            return [f'No contact info provided.```css\n.d u contact "CONTACT INFO"```']
        self.user.url = ' '.join(self.args[1:])
        self.user.updated_by = str(self.user.id)
        self.user.updated = T.now()
        self.user.save()
        return [self.user.get_string()]