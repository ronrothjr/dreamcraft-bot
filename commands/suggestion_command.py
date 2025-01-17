# suggestion_command.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import pytz
from config.setup import Setup
from models import User
from models import Suggestion
from services import SuggestionService
from utils import T, Dialog

SETUP = Setup()
SUGGESTION_HELP = SETUP.suggestion_help

suggestion_svc = SuggestionService()

class SuggestionCommand():
    """
    Handle 'suggestion', 'suggest' commands and subcommands

    Subcommands:
        help - display a set of instructions on SuggestionCommand usage
        name, n - display and create new suggestions by name
        list, l - display a list of existing suggestions
        delete - remove an suggestion (archive)
    """

    def __init__(self, parent, ctx, args, guild, user, channel):
        """
        Command handler for SuggestionCommand

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
        SuggestionCommand - object for processing suggestion commands and subcommands
        """

        self.parent = parent
        self.new = parent.new
        self.delete = parent.delete
        self.ctx = ctx
        self.args = args[1:] if args[0] in ['suggestion', 'suggest'] else args
        self.command = self.args[0].lower() if len(self.args) > 0 else ''
        self.guild = guild
        self.user = user
        self.channel = channel
        self.can_edit = self.user.role == 'Admin' if self.user else False

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
                'list': self.suggestion_list,
                'l': self.suggestion_list,
                'name': self.name,
                'n': self.name,
                'delete': self.delete_suggestion
            }
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: self.name)
            else:
                self.args = ('n',) + self.args
                self.command = 'n'
                func = self.name
                # Execute the function
            messages = func(self.args)
            # Send messages
            return messages
        except Exception as err:
            traceback.print_exc()
            return list(err.args)

    def help(self):
        """Returns the help text for the command"""
        return [SUGGESTION_HELP]

    def name(self, args):
        """Display and create a new Suggestion by name
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if len(args) < 2:
            raise Exception('syntax: ```css\n.d suggest "SUGGESTION TEXT"```')
        suggestion = Suggestion().create_new(name=self.user.name, text=' '.join(args[1:]))
        messages.append(suggestion.get_string(self.user))
        return messages

    def suggestion_list(self, args):
        """Display a dialog for viewing and selecting Suggestions
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['suggestion','suggest']:
                return SuggestionCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        def formatter(item, item_num, page_num, page_size):
            return item.get_short_string(self.user)

        messages.extend(Dialog({
            'svc': suggestion_svc,
            'user': self.user,
            'title': 'Suggestion List',
            'command': 'suggestion ' + (' '.join(args)),
            'type': 'view',
            'type_name': 'SUGGESTION',
            'page_size': 1,
            'getter': {
                'method': Suggestion.get_by_page,
                'params': {'params': {'archived': False}}
            },
            'formatter': formatter,
            'cancel': canceler
        }).open())
        return messages

    def delete_suggestion(self, args):
        """Delete (archive) the current active Suggestion
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.can_edit:
            raise Exception('You are not allowed to delete suggestions.')
        return suggestion_svc.delete_suggestion(args, self.user)