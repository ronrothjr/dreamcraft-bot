# scenario_command
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Character, User, Log
from config.setup import Setup
from services.scenario_service import ScenarioService
from utils import Dialog, T

scenario_svc = ScenarioService()
SETUP = Setup()
SCENARIO_HELP = SETUP.scenario_help

class ScenarioCommand():
    """
    Handle 'scenario' commands and subcommands

    Subcommands:
        help - display a set of instructions on ScenarioCommand usage
        note - add a note to the scenario
        say - add dialog to the scene from the scenario
        story - display the scenario's story
        new - create new scenarios by name
        name, n - display scenarios by name
        description, desc - add/edit the Description in the engeagement
        select, = - display existing engeagement
        character, char, c - edit the scenario as a character
        list, l - display a list of existing scenarios
        players, player, p - add players to the scenario
        delete - remove an scenario (archive)
    """

    def __init__(self, parent, ctx, args, guild, user, channel):
        """
        Command handler for ScenarioCommand

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
        ScenarioCommand - object for processing scenario commands and subcommands
        """

        self.parent = parent
        self.new = parent.new
        self.delete = parent.delete
        self.ctx = ctx
        self.args = args[1:]
        self.guild = guild
        self.user = user
        self.command = self.args[0].lower() if len(self.args) > 0 else 'n'
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.can_edit = self.user.role == 'Game Master' if self.user and self.scenario else True
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

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
                'name': self.select,
                'n': self.select,
                'select': self.select,
                '=': self.select,
                'note': self.note,
                'say': self.say,
                'story': self.story,
                'description': self.description,
                'desc': self.description,
                'character': self.character,
                'char': self.character,
                'c': self.character,
                'approaches': self.character,
                'approach': self.character,
                'apps': self.character,
                'app': self.character,
                'skills': self.character,
                'skill': self.character,
                'sks': self.character,
                'sk': self.character,
                'aspects': self.character,
                'aspect': self.character,
                'a': self.character,
                'stunts': self.character,
                'stunt': self.character,
                's': self.character,
                'custom': self.character,
                'stress': self.character,
                'st': self.character,
                'consequences': self.character,
                'consequence':self.character,
                'con': self.character,
                'players': self.player,
                'player': self.player,
                'p': self.player,
                'list': self.scenario_list,
                'l': self.scenario_list,
                'delete': self.delete_scenario,
                'd': self.delete_scenario
            }
            if self.new and not self.user.command or self.user.command and 'new' in self.user.command:
                func = self.new_scenario
            elif self.delete:
                func = self.delete_scenario
            # Get the function from switcher dictionary
            elif self.command in switcher:
                func = switcher.get(self.command, lambda: self.select)
            else:
                match = self.search(self.args)
                if match:
                    self.args = ('select',) + self.args
                    self.command = 'select'
                    func = self.select
                else:
                    self.args = ('n',) + self.args
                    self.command = 'n'
                    func = self.select
            if func:
                # Execute the function
                messages = func(self.args)
            # Send messages
            return messages
        except Exception as err:
            traceback.print_exc()
            # Log every error
            scenario_svc.log(
                str(self.scenario.id) if self.scenario else str(self.user.id),
                self.scenario.name if self.scenario else self.user.name,
                str(self.user.id),
                self.guild.name,
                'Error',
                {
                    'command': self.command,
                    'args': self.args,
                    'traceback': traceback.format_exc()
                }, 'created')
            return list(err.args)

    def help(self, args):
        """Returns the help text for the command"""
        return [SCENARIO_HELP]

    def search(self, args):
        """Search for an existing Scenario using the command string
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        params = {'name__icontains': ' '.join(args[0:]), 'guild': self.guild.name, 'channel_id': str(self.channel.id), 'archived': False}
        return scenario_svc.search(args, Scenario.filter, params)

    def get_parent(self, args):
        messages = []
        if (self.user and self.scenario and self.scenario.parent_id):
            messages.extend(scenario_svc.get_parent_by_id(Scenario.filter, self.user, self.scenario.parent_id))
        else:
            messages.append('No parent found')
        return messages

    def note(self, args):
        """Add a note to the Scenario story
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if self.scenario:
            Log().create_new(str(self.scenario.id), f'Scenario: {self.scenario.name}', str(self.user.id), self.guild.name, 'Scenario', {'by': self.user.name, 'note': ' '.join(args[1:])}, 'created')
            return ['Log created']
        else:
            return ['No active scenario to log']

    def say(self, args):
        """Add dialog to the Scenario story
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.scenario:
            return ['No active scenario to log']
        else:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.scenario.id), f'Scenario: {self.scenario.name}', str(self.user.id), self.guild.name, 'Scenario', {'by': self.user.name, 'note': f'***Narrator*** says, "{note_text}"'}, 'created')
            return ['Log created']

    def story(self, args):
        """Disaply the Scenario story
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages =[]
        command = 'scenario ' + (' '.join(args))
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['scenario']:
                self.args = cancel_args
                self.command = self.args[0]
                return self.run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()
        response = Dialog({
            'svc': scenario_svc,
            'user': self.user,
            'title': 'Story',
            'type': 'view',
            'type_name': 'Scenario Log',
            'command': command,
            'getter': {
                'method': Log.get_by_page,
                'params': {
                    'params': {'parent_id': str(self.scenario.id)},
                    'sort': 'created'
                },
                'parent_method': Scenario.get_by_page,
                'parent_params': {
                    'params': {'category__in': ['Character','Aspect','Stunt']},
                    'sort': 'created'
                }
            },
            'formatter': lambda log, num, page_num, page_size: log.get_string(self.user), # if log.category == 'Log' else log.get_string()
            'cancel': canceler,
            'page_size': 10
        }).open()
        messages.extend(response)
        return messages

    def dialog(self, dialog_text, char=None):
        """Display Scenario information and help text
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        char, name, get_string, get_short_string = scenario_svc.get_info('scenario', self.scenario, self.channel)
        category = 'Scenario'
        dialog = {
            'create_scenario': ''.join([
                '**CREATE or SCENARIO**```css\n',
                '.d new scenario "YOUR SCENARIOR\'S NAME"```'
            ]),
            'active_scenario': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n' if self.can_edit else '',
                f':point_down:\n\n{get_string}'
            ]),
            'active_scenario_short': ''.join([
                f'***YOU ARE CURRENTLY EDITING...:***\n',
                f':point_down:\n\n{get_short_string}'
            ]),
            'rename_delete': ''.join([
                f'\n\n_Is ***{name}*** not the {category.lower()} name you wanted?_',
                f'```css\n.d scenario rename "NEW NAME"```_Want to remove ***{name}***?_',
                '```css\n.d scenario delete```'
            ]),
            'go_back_to_parent': ''.join([
                f'\n\n***You can GO BACK to the parent scenario, aspect, or stunt***',
                '```css\n.d scenario parent```'
            ])
        }
        dialog_string = ''
        if dialog_text == 'all':
            if not char:
                dialog_string += dialog.get('create_scenario', '')
            dialog_string += dialog.get('rename_delete', '')
        elif category == 'Scenario':
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_scenario', '')
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
        else:
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_scenario', '') if self.can_edit else ''
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
                dialog_string += dialog.get('go_back_to_parent', '') if self.can_edit else ''
        return dialog_string
    
    def new_scenario(self, args):
        """Create a new Scenario by name
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if len(args) == 0:
            if not self.scenario:
                return [
                    'No active scenario or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(scenario_svc.get_string(self.scenario, self.channel, self.user))
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_scenario_short')]
            scenario_name = ' '.join(args)
            if len(args) > 1 and args[1] == 'rename':
                scenario_name = ' '.join(args[2:])
                if not self.scenario:
                    return [
                        'No active scenario or name provided\n\n',
                        self.dialog('all')
                    ]
                else:
                    scenario = Scenario().find(self.user, scenario_name, self.guild.name)
                    if scenario:
                        return [f'Cannot rename to _{scenario_name}_. Scenario already exists']
                    else:
                        self.scenario.name = scenario_name
                        scenario_svc.save(self.scenario, self.user)
                        messages.append(self.dialog(''))
            else:
                def canceler(cancel_args):
                    if cancel_args[0].lower() in ['scenario']:
                        return ScenarioCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                    else:
                        self.parent.args = cancel_args
                        self.parent.command = self.parent.args[0]
                        return self.parent.get_messages()

                def selector(selection):
                    self.scenario = selection
                    self.channel.set_active_scenario(self.scenario, self.user)
                    self.user.set_active_character(self.scenario.character)
                    scenario_svc.save_user(self.user)
                    return [self.dialog('')]

                messages.extend(Dialog({
                    'svc': scenario_svc,
                    'user': self.user,
                    'title': 'Scenario List',
                    'command': 'new scenario ' + ' '.join(args),
                    'type': 'select',
                    'type_name': 'SCENARIO',
                    'getter': {
                        'method': Scenario.get_by_page,
                        'params': {'params': {'name__icontains': scenario_name, 'channel_id': str(self.channel.id), 'guild': self.guild.name, 'archived': False}}
                    },
                    'formatter': lambda item, item_num, page_num, page_size: f'_SCENARIO #{item_num+1}_\n{scenario_svc.get_string(item, self.channel)}',
                    'cancel': canceler,
                    'select': selector,
                    'confirm': {
                        'method': Scenario().get_or_create,
                        'params': {'user': self.user, 'name': scenario_name, 'channel': self.channel, 'guild': self.guild.name}
                    }
                }).open())
        return messages
    
    def select(self, args):
        """Select an existing Scenario by name
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if len(args) == 0:
            if not self.scenario:
                return [
                    'No active scenario or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.scenario.get_string())
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_scenario_short')]
            if len(args) == 1 and self.scenario:
                return [self.dialog('')]
            scenario_name = ' '.join(args[1:])
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['scenario']:
                    return ScenarioCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

            def selector(selection):
                self.scenario = selection
                self.channel.set_active_scenario(self.scenario, self.user)
                self.user.set_active_character(self.scenario.character)
                scenario_svc.save_user(self.user)
                return [self.dialog('')]

            messages.extend(Dialog({
                'svc': scenario_svc,
                'user': self.user,
                'title': 'Scenario List',
                'command': 'scenario ' + ' '.join(args),
                'type': 'select',
                'type_name': 'SCENARIO',
                'getter': {
                    'method': Scenario.get_by_page,
                    'params': {'params': {'name__icontains': scenario_name, 'channel_id': str(self.channel.id), 'guild': self.guild.name, 'archived': False}}
                },
                'formatter': lambda item, item_num, page_num, page_size: f'_SCENARIO #{item_num+1}_\n{scenario_svc.get_string(item, self.channel)}',
                'cancel': canceler,
                'select': selector
            }).open())
        return messages

    def scenario_list(self, args):
        """Display a dialog for viewing and selecting Scenarios
        
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
            if cancel_args[0].lower() in ['scenario']:
                return ScenarioCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        messages.extend(Dialog({
            'svc': scenario_svc,
            'user': self.user,
            'title': 'Scenario List',
            'command': 'scenario ' + (' '.join(args)),
            'type': 'view',
            'getter': {
                'method': Scenario().get_by_channel,
                'params': {'channel': self.channel, 'archived': False}
            },
            'formatter': lambda item, item_num, page_num, page_size: f'{item.get_short_string(self.channel)}',
            'cancel': canceler
        }).open())
        return messages

    def description(self, args):
        """Add/edit the description for a Scenario
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if len(args) == 1:
            return ['No description provided']
        if not self.scenario:
            return ['You don\'t have an active scenario.\nTry this: ".d s name {name}"']
        else:
            description = ' '.join(args[1:])
            self.scenario.description = description
            self.scenario.updated_by = str(self.user.id)
            self.scenario.updated = T.now()
            self.scenario.save()
            return [
                f'Description updated to "{description}"',
                self.scenario.get_string(self.channel)
            ]

    def character(self, args):
        """Edit the Scenario as a character
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if self.user:
            self.user.active_character = str(self.scenario.character.id)
            self.user.updated_by = str(self.user.id)
            self.user.updated = T.now()
            self.user.save()
        command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args, guild=self.guild, user=self.user, channel=self.channel, char=self.scenario.character)
        return command.run()

    def player(self, args):
        """Add/remove a player from the Scenario
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        return scenario_svc.player(args, self.channel, self.scenario, self.user)

    def delete_scenario(self, args):
        """Delete (archive) the current active Scenario
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        return scenario_svc.delete_item(args, self.user, self.scenario, Scenario().find, {'guild': self.guild.name, 'channel_id': str(self.channel.id)})