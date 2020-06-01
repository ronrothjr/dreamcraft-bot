# cheat_command.py

from config.setup import Setup

SETUP = Setup()
CHEATS = SETUP.cheats

class CheatCommand():
    """
    Handle 'cheat' commands and subcommands
    """

    def __init__(self, parent, ctx, args, guild=None, user=None, channel=None):
        """
        Command handler for cheat command

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
        char : Character, optional
            The database character object 

        Returns
        -------
        CharacterCommand - object for processing cheat commands
        """
    
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