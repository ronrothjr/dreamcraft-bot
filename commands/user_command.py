# user_command.py

import pytz
import datetime
from config.setup import Setup
from models.user import User

SETUP = Setup()
USER_HELP = SETUP.user_help

class UserCommand():
    def __init__(self, parent, ctx, args, guild, user, channel):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.guild = guild
        self.user = user
        self.command = self.args[0].lower() if len(self.args) > 0 else 'u'

    def run(self):
        switcher = {
            'help': self.help,
            'user': self.get_user,
            'u': self.get_user,
            'timezone': self.time_zone,
            'tz': self.time_zone
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

    def help(self):
        return [USER_HELP]

    def get_user(self):
        return [self.user.get_string()]
    
    def time_zone(self):
        tz_help = 'Try this:```css\n.d u timezone ZONE_SEARCH\n/* ZONE_SEARCH must be at least 3 characters */```'
        if len(self.args) == 0:
            if not self.user:
                return ['No active user or name provided']
        if len(self.args) < 2:
            return [f'No time zone provided. {tz_help}']
        if self.args[1] in ['list', 'l']:
            if len(self.args) <3:
                return [f'No time zone search term provided. {tz_help}']
            if len(self.args[2]) <3:
                return ['No time zone search term must be at least 3 characters```css\n/* EXAMPLES */\n.d u timezone New York\n.d u timezone London```']
            search = self.args[2].lower()
            tz = [tz for tz in pytz.all_timezones if search in tz.lower()]
            if len(tz) == 0:
                return [f'Time zone \'{search}\' not found']
            if len(', '.join([t for t in tz])) > 2000:
                return [f'Results too large: please narrow your search']
            return [', '.join(tz)]
        else:
            search = self.args[1].lower()
            tz = [tz for tz in pytz.all_timezones if search in tz.lower()]
            if len(tz) == 0:
                return [f'Time zone \'{search}\' not found']
            if len(', '.join([t for t in tz])) > 1920:
                return [f'Results too large: please narrow your search']
            if len(tz) > 1:
                timezones = '\n'.join([f'.d u tz {t}' for t in tz])
                return [f'Time zone search \'{search}\' returned more than one. Try one of these:```css\n{timezones}```']
            self.user.time_zone = tz[0]
            if (not self.user.created):
                self.user.created = datetime.datetime.utcnow()
            self.user.updated_by = str(self.user.id)
            self.user.updated = datetime.datetime.utcnow()
            self.user.save()
        return [f'Saved time zone as _{tz[0]}\n\n{self.user.get_string()}_']