# character_command.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import datetime
from datetime import timezone
import copy
from bson.objectid import ObjectId
from services import CharacterService, SceneService, ScenarioService
from models import User, Channel, Scenario, Scene, Character, Log
from config.setup import Setup
from utils import TextUtils, Dialog
import inflect
p = inflect.engine()

char_svc = CharacterService()
scene_svc = SceneService()
scenario_svc = ScenarioService()
SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
CHARACTER_HELP = SETUP.character_help
COUNTERS_HELP = SETUP.counters_help
STRESS_HELP = SETUP.stress_help
CONSEQUENCES_HELP = SETUP.consequences_help
X = SETUP.x
O = SETUP.o
STRESS = SETUP.stress
STRESS_CATEGORIES = SETUP.stress_categories
STRESS_TITLES = SETUP.stress_titles
CONSEQUENCES = SETUP.consequences
CONSEQUENCES_CATEGORIES = SETUP.consequences_categories
CONSEQUENCES_TITLES = SETUP.consequences_titles
CONSEQUENCES_SHIFTS = SETUP.consequence_shifts

class CharacterCommand():
    """
    Handle 'character', 'char', 'c' commands and subcommands

    Subcommands:
        help - display a set of instructions on CharacterCommand usage
        note - add a note to the character
        say - add dialog to the scene from the character
        story - display the character's story
        stats - display statistics on Dreamcraft Bot usage
        parent, p - return viewing and editing focus to the character's parent component
        new - create new characters by name
        name, n - display characters by name
        select - display existing characters
        image - add an image to embed in the character sheet
        list, l - display a list of existing characters and NPCs
        delete - remove a character (archive)
        restore - restore a character from the archive
        copy - duplicate a character from one server to another (must have access to both)
        description, desc - add/edit the Description in the character sheet
        high, hc - add/edit the High Concept in the character sheet
        trouble, t - add/edit the Trouble in the character sheet
        fate, f - add/remove/refresh fate points
        aspects, aspect, a - add/delete aspects
        boost, b - add aspects as a boost
        approaches, approach, apps, app - add/edit approaches in the character sheet
        skills, skill, sks, sk - add/edit skills in the characater sheet
        stunts, stunt, s - add/delete stunts
        counters, counter, count, tickers, ticker, tick - add/edit counter tracks in the character sheet
        stress, st - add/edit stress tracks in the character sheet
        consequence, con - add/edit consequences and conditions in the character sheet
        custom - add/edit custom fields in the character sheet
        share - allow other users to view and copy your characters and npcs
        shared - view and copy characters and npcs shared by others
    """

    def __init__(self, parent, ctx, args, guild, user, channel, char=None):
        """
        Command handler for character command

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
        CharacterCommand - object for processing character commands and subcommands
        """

        self.parent = parent
        self.new = parent.new
        self.delete = parent.delete
        self.ctx = ctx
        self.args = args[1:] if args[0] in ['character', 'char', 'c'] else args
        self.npc = False
        if len(self.args) and self.args[0].lower() == 'npc':
            self.npc = True
            self.args = self.args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'select'
        self.guild = guild
        self.user = user
        self.channel = channel
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.char = char if char else (Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None)
        self.can_edit = str(self.user.id) == str(self.char.user.id) or self.user.role in ['Admin', 'Game Master'] if self.user and self.char else True
        self.can_copy = self.char.shared and self.char.shared.copy or self.user.role in ['Admin','Game Master'] if self.char else False
        self.asp = Character().get_by_id(self.char.active_aspect) if self.char and self.char.active_aspect else None
        self.stu = Character().get_by_id(self.char.active_stunt) if self.char and self.char.active_stunt else None

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
                'note': self.note,
                'say': self.say,
                'story': self.story,
                'stats': self.stats,
                'parent': self.get_parent,
                'p': self.get_parent,
                'name': self.select,
                'n': self.select,
                'select': self.select,
                'image': self.image,
                'list': self.character_list,
                'l': self.character_list,
                'delete': self.delete_character,
                'restore': self.restore_character,
                'copy': self.copy_character,
                'description': self.description,
                'desc': self.description,
                'high': self.high_concept,
                'hc': self.high_concept,
                'trouble': self.trouble,
                't': self.trouble,
                'fate': self.fate,
                'f': self.fate,
                'aspects': self.aspect,
                'aspect': self.aspect,
                'a': self.aspect,
                'approaches': self.approach,
                'approach': self.approach,
                'apps': self.approach,
                'app': self.approach,
                'skills': self.skill,
                'skill': self.skill,
                'sks': self.skill,
                'sk': self.skill,
                'stunts': self.stunt,
                'stunt': self.stunt,
                's': self.stunt,
                'counters': self.counter,
                'counter': self.counter,
                'count': self.counter,
                'tickers': self.counter,
                'ticker': self.counter,
                'tick': self.counter,
                'stress': self.stress,
                'st': self.stress,
                'consequence': self.consequence,
                'con': self.consequence,
                'custom': self.custom,
                'share': self.share,
                'shared': self.shared
            }
            if self.new and not self.user.command or self.user.command and 'new' in self.user.command:
                func = self.new_character
            elif self.delete:
                func = self.delete_character
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
            char_svc.log(
                str(self.char.id) if self.char else str(self.user.id),
                self.char.name if self.char else self.user.name,
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
        """Returns the help text for the command
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands
        """

        return [self.dialog('all')]

    def search(self, args):
        """Search for an existing Character using the command string
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        params = {'name__icontains': ' '.join(args[0:]), 'guild': self.guild.name, 'category': 'Character', 'archived': False, 'npc': self.npc}
        return char_svc.search(args, Character.filter, params)

    def canceler(self, args):
        """Handle a command that cancels a dialog
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        self.parent.args = args
        self.parent.command = self.parent.args[0]
        return self.parent.get_messages()

    def note(self, args):
        """Add a note the Character story
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if len(args) < 2:
            raise Exception('Note subcommand is missing content. Try this:```css\n.d c note "Something really cool just happened."')
        if self.char:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.char.id), f'Character: {self.char.name}', str(self.user.id), self.guild.name, 'Character', {'by': self.user.name, 'note': '"' + note_text + '"'}, 'created')
            return ['Log created']
        else:
            return ['No active character to log']

    def say(self, args):
        """Add dialog to the Character story
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if len(args) < 2:
            raise Exception('Say subcommand is missing content. Try this:```css\n.d c say "I\'m about to say something really cool."')
        if not self.char:
            return ['No active character to log']
        if not self.sc:
            return [f'{self.char.name} is not in a scene']
        else:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.sc.id), f'Character: {self.char.name}', str(self.user.id), self.guild.name, 'Character', {'by': self.user.name, 'note': f'***{self.char.name}*** says, "{note_text}"'}, 'created')
            return ['Log created']

    def story(self, args):
        """Disaply the Character story
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages =[]
        command = 'c ' + (' '.join(args))
        response = Dialog({
            'svc': char_svc,
            'user': self.user,
            'title': 'Story',
            'type': 'view',
            'type_name': 'Story Log',
            'command': command,
            'getter': {
                'method': Log.get_by_page,
                'params': {
                    'params': {'parent_id': str(self.char.id), 'data__note__exists': True},
                    'sort': 'created'
                },
                'parent_method': Character.get_by_page,
                'parent_params': {
                    'params': {'category__in': ['Character','Aspect','Stunt']},
                    'sort': 'created'
                }
            },
            'formatter': lambda log, num, page_num, page_size: log.get_string(self.user), # if log.category == 'Log' else log.get_string()
            'cancel': self.canceler,
            'page_size': 10
        }).open()
        messages.extend(response)
        return messages

    def stats(self, args):
        """Disaply stats for the current server
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        search = ' '.join(args[1:]) if len(args) > 1 else self.guild.name
        guilds = [g['guild'] for g in Character().get_guilds() if g['guild']]
        guild_list = f'***Guilds:***\n' + '\n'.join([f'    ***{g}***' for g in guilds])
        guild = search
        if not search.lower() == 'all':
            guild = next((g for g in guilds if search.lower() in g.lower()), None)
            if not guild:
                raise Exception(f'_{search}_ not found in guilds\n\n{guild_list}')
        stats = Character().get_stats(guild)
        stats_str = ''
        for s in stats:
            stats_str += f'\n\nGuild: ***{s}***'
            for t in stats[s]:
                stats_str += f'\n{stats[s][t]}  _{t}_'
        return [stats_str]

    def get_parent(self, args):
        """Get the Character's parent display string
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if (self.user and self.char and self.char.parent_id):
            messages.extend(char_svc.get_parent_by_id(Character.filter, self.user, self.char.parent_id))
        else:
            messages.append('No parent found')
        return messages

    def dialog(self, dialog_text, char=None):
        """Display Character information and help text
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        char = char if char else self.char
        char, name, get_string, get_short_string = char_svc.get_info('character', char, self.user)
        can_edit = str(self.user.id) == str(char.user.id) or self.user.role in ['Admin','Game Master'] if self.user and char else True
        category = char.category if char else 'Character'
        dialog = {
            'create_character': ''.join([
                '**CREATE or SELECT A CHARACTER**```css\n',
                '.d new character "YOUR CHARACTER\'S NAME"```'
            ]),
            'active_character': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n' if can_edit else '',
                f':point_down:\n\n{get_string}'
            ]),
            'rename_delete': ''.join([
                f'\n\n_Is ***{name}*** not the {category.lower()} name you wanted?_',
                f'```css\n.d c rename "NEW NAME"```_Want to remove ***{name}***?_',
                '```css\n.d c delete```'
            ]) if can_edit else '',
            'active_character_short': ''.join([
                f'***THIS IS YOUR ACTIVE CHARACTER:***\n',
                f':point_down:\n\n{get_short_string}'
            ]),
            'copy_and_share': ''.join([
                '\n***Share a character***```css\n.d c share anyone /* READ-ONLY */\n',
                '.d c share to copy /* LET OTHERS COPY */\n',
                '.d c share revoke /* TURN OFF SHARING */```',
                '\n***Copy a character***```css\n.d c shared /* VIEW SHARED CHARACTERS */\n',
                '.d c copy /* COPIES SELECTED CHARACTER */\n',
                '.d c copy to "SERVER NAME" /* COPIES YOUR CHARACTER TO ANOTHER SERVER */```'
            ]),
            'add_more_info': ''.join([
                f'Add more information about ***{name}***',
                '```css\n.d c description "CHARACTER DESCRIPTION"\n',
                '.d c high concept "HIGH CONCEPT"\n.d c trouble TROUBLE```'
            ]) if can_edit else '',
            'add_skills': ''.join([
                f'\nAdd approaches or skills for ***{name}***',
                '```css\n.d c approach Fo +4 Cl +2 Qu +1 Sn +2 Ca +1 Fl 0...\n',
                '/* Delete approaches/skills */\n',
                '.d c delete approach Forceful\n',
                '.d c delete skill Fight\n',
                '/* Custom approaches/skills should be spelled out */\n',
                '.d c approach Wanding +4 Potions +3 Broomstick +2\n',
                '/* GET LIST OF APPROACHES or ADD YOUR OWN */\n',
                '.d c approach help\n\n',
                '.d c skill Will +4 Rapport +2 Lore +1 ...\n',
                '/* Spaces require double quotes */\n',
                '.d c skill "Basket Weaving" +1 ...\n',
                '/* GET LIST OF SKILLS or ADD YOUR OWN */\n',
                '.d c skill help```'
            ]) if can_edit else '',
            'add_aspects_and_stunts': ''.join([
                f'\n\nAdd an aspect or two for ***{name}***',
                '```css\n.d c aspect "ASPECT NAME"\n',
                '.d c aspect delete "ASPECT NAME"\n',
                '/* Add custom aspect type */\n',
                '.d c aspect type "ASPECT TYPE"```',
                f'Give  ***{name}*** some cool stunts',
                '```css\n.d c stunt "STUNT NAME"\n',
                '.d c stunt delete "STUNT NAME"\n',
                '/* Add custom stunt type */\n',
                '.d c stunt type "STUNT TYPE"```'
            ]) if can_edit else '',
            'edit_active_aspect': ''.join([
                f'\n***You can edit this aspect as if it were a character***',
                '```css\n.d c aspect character\n',
                '/* THIS WILL SHOW THE ASPECT IS THE ACTIVE CHARACTER */\n',
                '.d c\n',
                '/* THIS WILL RETURN YOU TO EDITING THE CHARACTER */\n',
                '.d c parent```'
            ]) if can_edit else '',
            'edit_active_stunt': ''.join([
                f'\n***You can edit this stunt as if it were a character***',
                '```css\n.d c stunt character\n',
                '/* THIS WILL SHOW THE STUNT IS THE ACTIVE CHARACTER */\n',
                '.d c\n',
                '/* THIS WILL RETURN YOU TO EDITING THE CHARACTER */\n',
                '.d c parent```'
            ]) if can_edit else '',
            'manage_stress': ''.join([
                f'\n***Modify the stress tracks.\n',
                'Here\'s an example to add and remove stress tracks***',
                '```css\n.d c stress title 4 Ammo\n.d c stress title delete Ammo\n',
                '.d c stress title FATE /* also use FAE or Core */```'
            ]) if can_edit else '',
            'manage_conditions': ''.join([
                f'\n***Modify the conditions tracks.\n',
                'Here\'s an example to add and remove consequence tracks***',
                '```css\n.d c consequences title 2 Injured\n',
                '.d c consequences title delete Injured\n',
                '.d c consequences title FATE /* also use FAE or Core */```'
            ]) if can_edit else '',
            'go_back_to_parent': ''.join([
                f'\n\n***You can GO BACK to the parent character, aspect, or stunt***',
                '```css\n.d c parent\n.d c p```'
            ])
        }
        dialog_string = ''
        if dialog_text == 'all':
            if not char:
                dialog_string += dialog.get('create_character', '')
            dialog_string += dialog.get('rename_delete', '')
            dialog_string += dialog.get('add_more_info', '')
            dialog_string += dialog.get('add_skills', '')
            dialog_string += dialog.get('add_aspects_and_stunts', '')
            dialog_string += dialog.get('manage_stress', '')
            dialog_string += dialog.get('manage_conditions', '')
            dialog_string += dialog.get('copy_and_share')
        elif char.category == 'Character':
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            elif char.npc:
                dialog_string += dialog.get('active_character', '')
            else:
                dialog_string += dialog.get('active_character', '')
                if not char.high_concept or not char.trouble:
                    dialog_string += dialog.get('rename_delete', '')
                    dialog_string += dialog.get('add_more_info', '')
                elif not char.skills:                    
                    dialog_string += dialog.get('add_skills', '')
                elif char.skills:  
                    dialog_string += dialog.get('add_aspects_and_stunts', '')
                    dialog_string += dialog.get('manage_stress', '')
                    dialog_string += dialog.get('manage_conditions', '')
                    dialog_string += dialog.get('copy_and_share')
        else:
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_character', '')
                dialog_string += dialog.get('rename_delete', '')
                dialog_string += dialog.get('go_back_to_parent', '')
                dialog_string += dialog.get('add_aspects_and_stunts', '')
                dialog_string += dialog.get('manage_stress', '')
                dialog_string += dialog.get('manage_conditions', '')
        return dialog_string

    def new_character(self, args):
        """Create a new Character by name
        
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
            if not self.char:
                return [
                    'No active character or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.dialog('active_character') + '\n')
            return messages
        if len(args) == 1 and args[0].lower() == 'short':
            return [self.dialog('active_character_short')]
        char_name = ' '.join(args)
        if len(args) > 1 and args[1] == 'rename':
            char_name = ' '.join(args[2:])
            if not self.char:
                return [
                    'No active character or name provided\n\n',
                    self.dialog('all')
                ]
            else:
                char = Character().find(self.user, char_name, self.guild.name)
                if char:
                    return [f'Cannot rename to _{char_name}_. Character already exists']
                else:
                    self.char.name = char_name
                    char_svc.save(self.char, self.user)
                    messages.append(self.dialog(''))
        else:
            def selector(selection):
                self.char = selection
                self.user.set_active_character(self.char)
                char_svc.save_user(self.user)
                return [self.dialog('')]

            def formatter(item, item_num, page_num, page_size):
                return f'_CHARACTER #{((page_num-1)*page_size)+item_num+1}_\n{item.get_short_string()}'

            def creator(**params):
                char = Character().get_or_create(**params)
                if self.sc:
                    scene_svc.player(('p', char.name), self.channel, self.sc, self.user)
                return char

            messages.extend(Dialog({
                'svc': char_svc,
                'user': self.user,
                'title': 'Character List',
                'command': 'new c ' + ('npc ' if self.npc else '' ) + ' '.join(args),
                'type': 'select',
                'type_name': 'CHARACTER',
                'getter': {
                    'method': Character.get_by_page,
                    'params': {'params': {'name__icontains': char_name, 'guild': self.guild.name, 'category': 'Character', 'archived': False, 'npc': self.npc}}
                },
                'formatter': formatter,
                'cancel': self.canceler,
                'select': selector,
                'confirm': {
                    'method': creator,
                    'params': {'user': self.user, 'name': char_name, 'guild': self.guild.name, 'npc': self.npc}
                }
            }).open())
        return messages
    
    def select(self, args):
        """Select an existing Character by name
        
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
            if not self.char:
                return [
                    'No active character or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.char.get_string())
            return messages
        if len(args) == 1 and args[0].lower() == 'short':
            return [self.dialog('active_character_short')]
        if len(args) == 1 and self.char:
            return [self.dialog('')]
        char_name = ' '.join(args[1:])
        def selector(selection):
            self.char = selection
            self.user.set_active_character(self.char)
            char_svc.save_user(self.user)
            return [self.dialog('active_character')]

        def formatter(item, item_num, page_num, page_size):
            return f'_CHARACTER #{((page_num-1)*page_size)+item_num+1}_\n{item.get_short_string(self.user)}'

        messages.extend(Dialog({
            'svc': char_svc,
            'user': self.user,
            'title': 'Character List',
            'command': 'c ' + ' '.join(args),
            'type': 'select',
            'type_name': 'CHARACTER',
            'getter': {
                'method': Character.get_by_page,
                'params': {'params': {'name__icontains': char_name, 'guild': self.guild.name, 'npc': self.npc, 'archived': False}}
            },
            'formatter': formatter,
            'cancel': self.canceler,
            'select': selector
        }).open())
        return messages

    def character_list(self, args):
        """Display a dialog for viewing and selecting Characters
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        def selector(selection):
            self.char = selection
            self.user.set_active_character(self.char)
            char_svc.save_user(self.user)
            return [self.dialog('active_character')]

        def formatter(item, item_num, page_num, page_size):
            return f'_CHARACTER #{((page_num-1)*page_size)+item_num+1}_\n{item.get_short_string(self.user)}'

        messages.extend(Dialog({
            'svc': char_svc,
            'user': self.user,
            'title': 'Character List',
            'command': 'c ' + ('npc ' if self.npc else '' ) + (' '.join(args)),
            'type': 'view',
            'getter': {
                'method': Character.get_by_page,
                'params': {'params': {'guild': self.guild.name, 'category': 'Character', 'archived': False}}
            },
            'formatter': formatter,
            'cancel': self.canceler,
            'select': selector
        }).open())
        return messages

    def copy_character(self, args):
        """Copy a character from one guild to another (must have membershihp to both guilds)
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        search = ''
        if not self.char:
            raise Exception('No active character to copy')
        if not self.can_edit and not self.can_copy:
            raise Exception('You do not have permission to copy this character')
        if self.char.category != 'Character':
            raise Exception(f'You may only copy characters. ***{self.char.name}*** is {p.an(self.char.category)}.')
        guilds = [g['guild'] for g in Character().get_guilds() if g['guild'] and g['guild'].lower() not in self.guild.name.lower()]
        if self.can_copy and len(args) == 1:
            if str(self.char.user.id) == str(self.user.id):
                raise Exception(f'You cannot copy your own character within the same guild')
            user = self.user
            guild = self.guild.name
            messages.append(f'***{self.char.name}*** copied\n')
        else:
            if not guilds:
                raise Exception('You may not copy until you have created a character on another server')
            guild_list = f'***Guilds:***\n' + '\n'.join([f'    ***{g}***' for g in guilds])
            guild_commands = '\n'.join([f'.d c copy to {g}' for g in guilds[0:5]])
            guild_commands_str = f'\n\nTry one of these:```css\n{guild_commands}```'
            incorrect_syntax = f'Copy character syntax inccorect{guild_commands_str}'
            if len(args) == 1:
                raise Exception(incorrect_syntax)
            if len(args) == 2 or (len(args) == 3 and args[1].lower() != 'to'):
                raise Exception(incorrect_syntax)
            search = ' '.join(args[2:])
            guild = next((g for g in guilds if search.lower() in g.lower()), None)
            if not guild:
                raise Exception(f'_{search}_ not found in guilds\n\n{guild_list}')
            user = User().find(self.user.name, guild)
            if not user:
                raise Exception(f'You may not copy until you have created a character in ***{guild}***')
            existing = Character().find(user, self.char.name, guild, None, 'Character')
            if existing:
                raise Exception(f'***{self.char.name}*** is already a character in ***{guild}***')
            messages.append(f'***{self.char.name}*** copied to ***{guild}***\n')
        children = Character().get_by_parent(self.char)
        char = copy.deepcopy(self.char)
        char.id = None
        char.user = user.id
        char.guild = guild
        char_svc.save(char, user)
        for child in children:
            new_child = copy.deepcopy(child)
            new_child.id = None
            new_child.user = user.id
            new_child.parent_id = str(char.id)
            new_child.guild = guild
            char_svc.save(new_child, user)
        return messages

    def delete_character(self, args):
        """Delete (archive) the current active Character
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if not self.char:
            return ['No active character for deletion']
        if not self.can_edit:
            raise Exception('You do not have permission to delete this character')

        # Handle alternate syntax for deleting character properties
        if len(args) > 0:
            if args[0].lower() in ('d', 'delete') and len(args) > 1:
                args = args[1:]
            if args[0] in ['approaches','approach','app']:
                if len(args) < 2:
                    raise Exception(f'Syntax error:```css\n.d delete {args[0]} "NAME"```')
                args = ('approach', 'delete') + args[1:]
                return self.approach(args)
            if args[0] in ['skills','skill','sks','sk']:
                if len(args) < 2:
                    raise Exception(f'Syntax error:```css\n.d delete {args[0]} "NAME"```')
                args = ('skill', 'delete') + args[1:]
                return self.skill(args)
            if args[0] in ['aspects','aspect','a']:
                if len(args) < 2:
                    raise Exception(f'Syntax error:```css\n.d delete {args[0]} "NAME"```')
                args = ('aspect', 'delete') + args[1:]
                return self.aspect(args)
            if args[0] in ['stunts','stunt','s']:
                if len(args) < 2:
                    raise Exception(f'Syntax error:```css\n.d delete {args[0]} "NAME"```')
                args = ('stunt', 'delete') + args[1:]
                return self.stunt(args)
            if args[0] in ['counters','counter','count','tickers','ticker','tick']:
                args = ('count', 'delete') + tuple([a for a in args[1:] if a not in ['delete']])
                return self.counter(args)
            if args[0] in ['stresses','stress','st']:
                if len(args) < 2:
                    raise Exception(f'Syntax error:```css\n.d delete {args[0]} "NAME"\n.d delete {args[0]} title "NAME"```')
                args = ('stress', 'title', 'delete') + tuple([a for a in args[1:] if a not in ['delete', 'title']])
                return self.stress(args)
            if args[0] in ['consequences','consequence','con']:
                if len(args) < 2:
                    raise Exception(f'Syntax error:```css\n.d delete {args[0]} "NAME"\n.d delete {args[0]} title "NAME"```')
                args = ('consequence', 'title', 'delete') + tuple([a for a in args[1:] if a not in ['delete', 'title']])
                return self.consequence(args)

        def getter(item, page_num=0, page_size=5):
            return [item]

        def formatter(item, item_num=None, page_num=None, page_size=None):
            return f'Are you sure you want to delete this CHARACTER?\n\n{(item[0] if isinstance(item, list) else item).get_short_string()}' 

        def deleter(item):
            search = item.name
            item.archive(self.user)
            self.user.active_character = None
            char_svc.save_user(self.user)
            messages.append(''.join([
                f'***{search}*** removed\n\n',
                'You can restore this character at any time:',
                f'```css\n.d c restore {search}```'
            ]))
            parent_id = str(item.parent_id) if hasattr(item, 'parent_id') and item.parent_id else ''
            if parent_id:
                return char_svc.get_parent_by_id(Character.filter, self.user, parent_id)
            return None

        messages.extend(Dialog({
            'svc': char_svc,
            'user': self.user,
            'title': 'Remove Character',
            'command': 'c ' + ('npc ' if self.npc else '' ) + (' '.join(args)),
            'type': 'confirm',
            'type_name': 'Character',
            'getter': {
                'method': getter,
                'params': {'item': self.char}
            },
            'formatter': formatter,
            'cancel': self.canceler,
            'confirm': {
                'method': deleter,
                'params': {'item': self.char}
            }
        }).open())
        return messages

    def restore_character(self, args):
        """Restore a Character by name
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        char_name = ' '.join(args[1:])
        params = {'name': char_name, 'guild': self.guild.name, 'archived': True}
        if not self.user.role or self.user.role and self.user.role not in ['Admin', 'Game Master']:
            params['user'] = self.user.id

        def formatter(item, item_num=None, page_num=None, page_size=None):
            return f'{item.get_short_string()}'

        def selector(item):
            current_chars = []
            current_chars.extend(Character.filter(name=item.name, guild=self.guild.name, archived=False).all())
            if current_chars:
                Exception(''.join([
                    f'Cannot restore {char_name} while characters with that name already exist.\n\n',
                    f'Try deleting and retoring one of them.',
                    f'```css\n.d c delete {char_name}\n',
                    f'.d c restore {char_name}```'
                ]))
            self.char = item
            self.char.restore(self.user)
            self.user.set_active_character(self.char)
            messages.append(f'***{self.char.name}*** restored.\n')
            return [self.dialog('active_character')]

        messages.extend(Dialog({
            'svc': char_svc,
            'user': self.user,
            'title': 'Restore Character',
            'command': 'c ' + ('npc ' if self.npc else '' ) + (' '.join(args)),
            'type': 'select',
            'type_name': 'Character',
            'getter': {
                'method': Character.get_by_page,
                'params': {'params': params}
            },
            'formatter': formatter,
            'cancel': self.canceler,
            'select': selector
        }).open())
        return messages

    def description(self, args):
        """Add/edit the description for a Character
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if len(args) == 1:
            messages.append('No description provided')
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
        elif not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        else:
            description = TextUtils.value_with_quotes(args[1:])
            self.char.description = description
            char_svc.save(self.char, self.user)
            messages.append(f'Description updated to _{description}_\n')
            messages.append(self.dialog('active_character_short'))
        return messages

    def high_concept(self, args):
        """Add/edit the High Concept for in the character sheet
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if len(args) == 2 or (len(args) == 1 and args[1].lower() != 'concept'):
            messages.append('No high concept provided')
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
        elif not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        else:
            hc = ''
            if args[1].lower() == 'concept':
                hc = TextUtils.value_with_quotes(args[2:])
            else:
                hc = TextUtils.value_with_quotes(args[1:])
            self.char.high_concept = hc
            char_svc.save(self.char, self.user)
            messages.append(f'High Concept updated to _{hc}_\n')
            messages.append(self.dialog(''))
        return messages

    def trouble(self, args):
        """Add/edit the Trouble in the character sheet
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        if len(args) == 1:
            messages.append('No trouble provided')
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
        else:
            trouble = TextUtils.value_with_quotes(args[1:])
            self.char.trouble = trouble
            char_svc.save(self.char, self.user)
            messages.append(f'Trouble updated to _{trouble}_\n')
            messages.append(self.dialog(''))
        return messages

    def fate(self, args):
        """Add, remove, or refresh Fate Points and Refresh
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.char:
            return ['You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```']
        elif not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        elif args[1].lower() == 'none':
            self.char.refresh = None
            self.char.fate_points = None
        elif args[1].lower() in ['refresh', 'r']:
            if not self.char.refresh:
                self.char.refresh = 3
            refresh = int(args[2]) if len(args) == 3 and args[2].isdigit() else self.char.refresh
            self.char.refresh = refresh
            self.char.fate_points = self.char.refresh
        elif args[1] == '+':
            if not self.char.fate_points:
                self.char.fate_points = 0
            points = int(args[2]) if len(args) == 3 and args[2].isdigit() else 1
            self.char.fate_points += points if self.char.fate_points < 5 else 0
        elif args[1] == '-':
            if not self.char.fate_points:
                self.char.fate_points = 2
            points = int(args[2]) if len(args) == 3 and args[2].isdigit() else 1
            self.char.fate_points -= points if self.char.fate_points < 5 else 0
        char_svc.save(self.char, self.user)
        return [f'Fate Points: {self.char.get_string_fate()}'] if self.char.get_string_fate() else ['Fate points not used by this character']

    def custom(self, args):
        """Add/edit custom fields in the character sheet
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.char:
            raise Exception('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        messages = []
        if len(args) == 1:
            raise Exception('No custom name provided. Try this: ```css\n.d c custom "CUSTOM NAME"\n/* EXAMPLE:\n.d c custom Home World */```')
        if len(args) == 2:
            raise Exception('No custom property information provided. Try this: ```css\n.d c custom "CUSTOM NAME" "CUSTOM PROPERTY INFORMATION"\n/* EXAMPLE:\n.d c custom "Home" "Earth (alternate history)" */```')
        if args[1] in ['delete', 'd']:
            custom_properties = copy.deepcopy(self.char.custom_properties) if self.char.custom_properties else {}
            display_name = TextUtils.clean(args[2])
            property_name = display_name.lower().replace(' ', '_')
            if property_name not in custom_properties:
                raise Exception(f'***{self.char.name}*** does not have a custom property named {display_name}')
            custom_properties.pop(property_name, None)
        else:
            display_name = TextUtils.clean(args[1])
            property_name = display_name.lower().replace(' ', '_')
            property_value = TextUtils.value_with_quotes(args[2:])
            custom_properties = copy.deepcopy(self.char.custom_properties) if self.char.custom_properties else {}
            custom_properties[property_name] = {
                'display_name': display_name,
                'property_value': property_value
            }
        self.char.custom_properties = custom_properties
        char_svc.save(self.char, self.user)
        messages.append(self.dialog(''))
        return messages

    def share(self, args):
        """Allow other users to view and copy your characters and npcs
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.char:
            raise Exception('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        messages = []
        shared = copy.deepcopy(self.char.shared) if self.char.shared else {}
        if len(args) == 1:
            raise Exception('No share settings specified. Try this: ```css\n.d c share anyone\n.d c share copy\n.d c share revoke```')
        if 'anyone' in ' '.join(args[1:]):
            messages.append(f'Sharing enabled for ***{self.char.name}***\n')
            shared['anyone'] = True
        if 'copy' in ' '.join(args[1:]):
            messages.append(f'Copying enabled for ***{self.char.name}***\n')
            shared['copy'] = True
        if args[1] in ['revoke', 'r']:
            messages.append(f'Sharing revoked for ***{self.char.name}***\n')
            shared = None
        self.char.shared = shared
        char_svc.save(self.char, self.user)
        messages.append(self.dialog(''))
        return messages

    def shared(self, args):
        """View and copy characters and npcs shared by others
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        params = {'shared__exists': True, 'archived': False}
        char_name = ' '.join(args[1:])
        if char_name:
            params['name__icontains'] = char_name

        def selector(selection):
            self.char = selection
            self.user.set_active_character(self.char)
            char_svc.save_user(self.user)
            self.args = ('copy',)
            self.can_copy = str(self.char.user.id) != str(self.user.id)
            messages.extend(self.copy_character(self.args))
            return [self.dialog('active_character')]

        def formatter(item, item_num, page_num, page_size):
            return f'_CHARACTER #{((page_num-1)*page_size)+item_num+1}_\n{item.get_short_sharing_string(self.user)}'

        messages.extend(Dialog({
            'svc': char_svc,
            'user': self.user,
            'title': 'Shared Characters',
            'command': 'c ' + ' '.join(args),
            'type': 'select',
            'type_name': 'CHARACTER',
            'getter': {
                'method': Character.get_by_page,
                'params': {'params': params}
            },
            'formatter': formatter,
            'cancel': self.canceler,
            'select': selector
        }).open())
        return messages

    def image(self, args):
        """Add/edit an embedded image for the character
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.char:
            raise Exception('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        messages = []
        if len(args) == 1:
            raise Exception(''.join([
                'No image url provided. Try this: ```css\n.d c image IMAGE_URL```\n',
                '***How to host an image on Google Drive:***\n',
                '* Upload to your Drive Folder and select your uploaded file.\n',
                '* Click the Share button and click \'Anyone with link\' and then \'Copy link\'\n',
                '* Take the id portion of your link (highlighted in bold below)\n',
                '*     drive.google.com/file/d/ ***1DALW-DtsdPg47cj4kybi6ng9DkiVdtaf*** /view?usp=sharing\n',
                '* Make a new link as follows with your id from above:\n',
                '* http://drive.google.com/uc?export=view&id=1DALW-DtsdPg47cj4kybi6ng9DkiVdtaf\n',
                '* Use this as the IMAGE_URL'
            ]))
        if args[1] in ['delete', 'd']:
            self.char.image_url = None
        else:
            self.char.image_url = args[1]
        char_svc.save(self.char, self.user)
        messages.append(self.dialog(''))
        return messages

    def approach(self, args):
        """Add/edit approaches or custom approaches in the character sheet
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if args[1].lower() == 'help':
            app_str = '\n        '.join(APPROACHES)
            messages.append(f'**Approaches:**\n        {app_str}')
        elif len(args) < 3:
            messages.append('Approach syntax: ```css\n.d approach "APPROACH NAME" BONUS [..."APPROACH NAME" BONUS]```')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
            elif not self.can_edit:
                raise Exception('You do not have permission to edit this character')
            else:
                if args[1].lower() in ['delete','d']:
                    skill = [a for a in APPROACHES if len(args[2]) == 2 and args[2][0:2].lower() == a[0:2].lower() or args[2].lower() == a.lower()]
                    skill = skill[0].split(' - ')[0] if skill else ' '.join(args[2:]).title()
                    if [s for s in self.char.skills if skill.lower() == s.lower()]:
                        new_skills = {}
                        for key in self.char.skills:
                            if key.lower() != skill.lower():
                                new_skills[key] = self.char.skills[key]
                        self.char.skills = new_skills
                        char_svc.save(self.char, self.user)
                        messages.append(f'Removed {skill} approach')
                    else:
                        messages.append(f'_{skill}_ not found in approaches')
                else:
                    indices = [0] + [i for i in range(1, len(args)) if args[i].replace('+','').replace('-','').isdigit()]
                    if len(indices) == 1:
                        raise Exception('Approach syntax: ```css\n.d approach "APPROACH NAME" BONUS [..."APPROACH NAME" BONUS]```')
                    for i in range(1, len(indices)):
                        abbr = ' '.join(args[(indices[i-1]+1):indices[i]])
                        val = args[indices[i]]
                        skill = [s for s in APPROACHES if abbr[0:2].lower() == s[0:2].lower()]
                        skill = skill[0].split(' - ')[0] if skill else abbr.title()
                        self.char.skills[skill] = val
                        messages.append(f'Updated {skill} to {val}')
                    self.char.use_approaches = True
                    char_svc.save(self.char, self.user)
                messages.append(self.char.get_string_skills() + '\n')
        return messages

    def skill(self, args):
        """Add/edit skills or custom skills in the character sheet
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if args[1].lower() == 'help':
            sk_str = '\n        '.join(SKILLS)
            messages.append(f'**Skills:**\n        {sk_str}')
        elif len(args) < 3:
            raise Exception('Skill syntax: ```css\n.d skill "SKILL NAME" BONUS [..."SKILL NAME" BONUS]```')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
            elif not self.can_edit:
                raise Exception('You do not have permission to edit this character')
            else:
                if args[1].lower() in ['delete','d']:
                    skill = [s for s in SKILLS if len(args[2]) == 2 and args[2][0:2].lower() == s[0:2].lower() or args[2].lower() == s.lower()]
                    skill = skill[0].split(' - ')[0] if skill else ' '.join(args[2:]).title()
                    if [s for s in self.char.skills if skill.lower() == s.lower()]:
                        new_skills = {}
                        for key in self.char.skills:
                            if key.lower() != skill.lower():
                                new_skills[key] = self.char.skills[key]
                        self.char.skills = new_skills
                        char_svc.save(self.char, self.user)
                        messages.append(f'Removed {skill} skill')
                    else:
                        messages.append(f'_{skill}_ not found in skill')
                else:
                    indices = [0] + [i for i in range(1, len(args)) if args[i].replace('+','').replace('-','').isdigit()]
                    if len(indices) == 1:
                        raise Exception('Skill syntax: ```css\n.d skill "SKILL NAME" BONUS [..."SKILL NAME" BONUS]```')
                    for i in range(1, len(indices)):
                        abbr = ' '.join(args[(indices[i-1]+1):indices[i]])
                        val = args[indices[i]]
                        skill = [s for s in SKILLS if abbr[0:2].lower() == s[0:2].lower()]
                        skill = skill[0].split(' - ')[0] if skill else abbr.title()
                        self.char.skills[skill] = val
                        messages.append(f'Updated {skill} to {val}')
                    self.char.use_approaches = False
                    char_svc.save(self.char, self.user)            
                messages.append(self.char.get_string_skills() + '\n')
        return messages

    def aspect(self, args):
        """Add/edit an aspect in the character sheet or edit it as a character
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []

        # Validate syntax and permissions
        if len(args) == 1:
            if not self.asp:
                return ['You don\'t have an active aspect.\nTry this: ```css\n.d c a "ASPECT NAME"```']
            messages.append(f'{self.asp.get_string(self.char)}')
            return messages
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```']
        elif not self.can_edit:
            raise Exception('You do not have permission to edit this character')

        # Handle aspect 'list' subcomand
        elif args[1].lower() == 'list':
            return [self.char.get_string_aspects(self.user)]

        # Handle aspect 'delete' subcomand
        elif args[1].lower() in ['delete','d']:
            aspect = ' '.join(args[2:])
            for a in Character().get_by_parent(self.char, aspect, 'Aspect'):
                aspect = str(a.name)
                a.reverse_archive(self.user)
                a.archived = True
                char_svc.save(a, self.user)
            messages.append(f'"{aspect}" removed from aspects')
            messages.append(self.char.get_string_aspects(self.user))
        
        # Handle aspect 'type' subcomand
        elif args[1].lower() in ['type','t']:
            if not self.asp:
                return ['You don\'t have an active aspect.\nTry this: ```css\n.d c a "ASPECT NAME"```']
            self.asp.type_name = ' '.join(args[2:])
            char_svc.save(self.asp, self.user)
            messages.append(f'Set the ***{self.asp.name}*** aspect with type _{self.asp.type_name}_')
        
        # Handle aspect Fate Fractal option to edit it as a character
        elif args[1].lower() in ['character', 'char', 'c']:
            if not self.asp:
                return ['You don\'t have an active aspect.\nTry this: ```css\n.d c a "ASPECT NAME"```']
            self.user.active_character = str(self.asp.id)
            char_svc.save_user(self.user)
            self.char.active_aspect = str(self.asp.id)
            self.char.active_character = str(self.asp.id)
            char_svc.save(self.char, self.user)
            command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args[1:], guild=self.guild, user=self.user, char=self.asp, channel=self.channel)
            messages.extend(command.run())
        
        # Save the aspect as a character with this character as a parent
        # This alows editing an aspect as a character
        else:
            is_boost = False
            freeinvokes = 0
            if args[1].lower() == 'boost':
                is_boost = True
                aspect = ' '.join(args[2:])
            elif args[1].lower() == 'freeinvoke':
                if len(args) < 3:
                    raise Exception('Here\'s how to create an aspect with a free invoke:```css\n.d c aspect freeinvoke "Aspect Name```Create an aspect with 2 free invokes:```css\n.d c aspect freeinvoke 2 "Aspect Name"```')
                if args[2].isdigit():
                    freeinvokes = int(args[2])
                    aspect = ' '.join(args[3:])
                else:
                    freeinvokes = 1
                    aspect = ' '.join(args[2:])
            else:
                with_invokes = len(args) > 4 and 'invoke' in args[-1].lower() and args[-2].isdigit() and args[-3].lower() == 'with'
                invokes = len(args) > 3 and 'invoke' in args[-1].lower() and args[-2].isdigit() and args[-3].lower() != 'with'
                freeinvokes = int(args[-2]) if with_invokes or invokes else 0
                aspect = ' '.join(args[1:-3]) if with_invokes else ' '.join(args[1:])
                aspect = ' '.join(args[1:-2]) if invokes else aspect
            self.asp = Character().get_or_create(self.user, aspect, self.guild.name, self.char, 'Aspect')
            if is_boost:
                self.asp.is_boost = True
                char_svc.save(self.asp, self.user)
            if freeinvokes:
                cmd = CharacterCommand(self.parent, self.ctx, ('counter', 'add', str(freeinvokes), 'Invokes'), self.guild, self.user, self.channel, self.asp)
                cmd.run()
            self.char.active_aspect = str(self.asp.id)
            char_svc.save(self.char, self.user)
            messages.append(self.char.get_string_aspects(self.user) + '\n')
            messages.append(self.dialog('edit_active_aspect'))
        return messages

    def stunt(self, args):
        """Add/edit a stunt in the character sheet or edit it as a character
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []

        # Validate stunt subcomand syntax and permisions
        if len(args) == 1:
            if not self.stu:
                return ['You don\'t have an active stunt.\nTry this: ```css\n.d c a "STUNT NAME"```']
            messages.append(f'{self.stu.get_string(self.char)}')
            return messages
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```']
        elif not self.can_edit:
            raise Exception('You do not have permission to edit this character')

        # Handle stunt 'list' subcommand
        elif args[1].lower() == 'list':
            return [self.char.get_string_stunts(self.user)]
        
        # Handle stunt 'delete'subcommand
        elif args[1].lower() in ['delete','d']:
            stunt = ' '.join(args[2:])
            for s in Character().get_by_parent(self.char, stunt, 'Stunt'):
                stunt = str(s.name)
                s.reverse_archive(self.user)
                s.archived = True
                char_svc.save(s, self.user)
            messages.append(f'"{stunt}" removed from stunts')
            messages.append(self.char.get_string_stunts(self.user))

        # Handle stunt Fate Fractal option to edit it as a character
        elif args[1].lower() in ['character', 'char', 'c']:
            self.user.active_character = str(self.stu.id)
            char_svc.save_user(self.user)
            self.char.active_stunt = str(self.stu.id)
            self.char.active_character = str(self.stu.id)
            char_svc.save(self.char, self.user)
            command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args[1:], guild=self.guild, user=self.user, channel=self.channel, char=self.stu)
            messages.extend(command.run())
        
        # Handle aspect 'type' subcomand
        elif args[1].lower() in ['type','t']:
            if not self.stu:
                return ['You don\'t have an active stunt.\nTry this: ```css\n.d c s STUNT_NAME```']
            self.stu.type_name = ' '.join(args[2:])
            char_svc.save(self.stu, self.user)
            messages.append(f'Set the ***{self.stu.name}*** stunt with type _{self.stu.type_name}_')
        
        # Save the stunt as a character with this character as a parent
        # This alows editing a stunt as a character
        else:
            stunt = ' '.join(args[1:])
            self.stu = Character().get_or_create(self.user, stunt, self.guild.name, self.char, 'Stunt')
            self.char.active_stunt = str(self.stu.id)
            char_svc.save(self.char, self.user)
            messages.append(self.char.get_string_stunts(self.user) + '\n')
            messages.append(self.dialog('edit_active_stunt'))
        return messages

    def get_available_ticks(self, char, counter_key):
        """Calculate the availble stress for a given type
        
        Parameters
        ----------
        char : Character
            Character to inspect
        counter_key : str
            Name of the countery key

        Returns
        -------
        int - the number of available counter ticks
        """

        return sum([1 for c in char.counters[counter_key]['ticks'] if c == O]) if char.counters and counter_key in char.counters else 0

    def counter(self, args, check_user=None):
        """Add/edit counters track
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands
        check_user : boolean
            Check for counter command errors on this user

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if len(args) == 1:
            messages.append(COUNTERS_HELP)
            return messages
        if args[1].lower() == 'help':
            messages.append(COUNTERS_HELP)
            return messages
        modified = None
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')

        # Handle adding/editing counters
        if args[1] in ['add','edit']:
            if len(args) < 4 or (len(args) > 2 and not args[2].isdigit()):
                raise Exception(f'Incorrect syntax for counter.\nTry this: ```css\n.d c counter {args[1]} 3 "Strikes"```')
            modified = copy.deepcopy(self.char.counters) if self.char.counters else {}
            name = ' '.join(args[3:])
            key = name.replace(' ','_').replace('__','_').lower()
            modified[key] = {
                'name': name.replace('  ',' '),
                'ticks': [O for i in range(0, int(args[2]))]
            }

        # Handle deleting counters
        elif args[1] in ['delete']:
            modified = copy.deepcopy(self.char.counters) if self.char.counters else {}
            name = ' '.join(args[2:])
            key = name.replace(' ','_').replace('__','_').lower()
            if key not in modified:
                messages.append(f'_{name}_ is not a counter')
                return messages
            modified = {}
            for c in self.char.counters:
                if key != c:
                    modified[key] = self.char.counters[c]
            if not check_user:
                messages.append(f'Removed **_{name}_** counter')

        # Handle ticking counters
        else:
            if len(args) < 2:
                messages.append(f'Incorrect syntax for ticking a counter.\nTry this: ```css\n.d c tick "Strikes"\n.d c tick 2 "Strikes"```')
                return messages
            if args[1].isdigit():
                name = ' '.join(args[2:])
                ticks = int(args[1])
            else:
                name = ' '.join(args[1:])
                ticks = 1
            key = name.replace(' ','_').replace('__','_').lower()
            modified = copy.deepcopy(self.char.counters) if self.char.counters and key in self.char.counters else {}
            if not modified:
                messages.append(f'_{name}_ is not a counter')
                return messages
            available = self.get_available_ticks(self.char, key) 
            if not available or available < ticks:
                messages.append(f'Cannot tick for {ticks} {name} ({available} available)')
                return messages
            for i in range(0,len(modified[key]['ticks'])):
                if ticks > 0 and modified[key]['ticks'][i] == O:
                    ticks -= 1
                    modified[key]['ticks'][i] = X

        if check_user:
            return messages
        else:
            self.char.counters = modified
            messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_counters()}')
            char_svc.save(self.char, self.user)
        return messages

    def get_available_stress(self, stress_type):
        """Calculate the availble stress for a given type
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        int - the number of available stress track marks available
        """

        return sum([1 * (int(s[0]) if s[0].isdigit() else 1) for s in self.char.stress[stress_type] if s[1] == O]) if self.char.stress else 0

    def stress(self, args, check_user=None):
        """Add/edit stress or customize a stress track
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands
        check_user : boolean
            Check for stress command errors on this user

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if len(args) == 1:
            messages.append(STRESS_HELP)
            return messages
        if args[1].lower() == 'help':
            messages.append(STRESS_HELP)
            return messages
        modified = None
        stress_titles = self.char.stress_titles if self.char.stress_titles else STRESS_TITLES
        stress_categories = self.char.stress_categories if self.char.stress_categories else []
        stress_checks = []
        [stress_checks.append(t[0:2].lower()) for t in stress_titles]
        [stress_checks.append(t.lower()) for t in stress_titles]
        stress_check_types = ' or '.join([f'({t[0:2 ].lower()}){t[2:].lower()}' for t in stress_titles])
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
            return messages
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        if len(args) == 1:
            messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_stress()}')
            return messages

        # Handle stress title setup option
        if args[1] in ['title', 't']:
            if len(args) == 2:
                messages.append('No stress title provided')
                return messages
            titles = []
            if self.char.stress_titles:
                titles = copy.deepcopy(self.char.stress_titles)
            elif not self.char.npc and self.char.category == 'Character' :
                titles = copy.deepcopy(SETUP.stress_titles)
            if args[2] in ['delete', 'd']:
                if not titles:
                    messages.append('You have not defined any custom stress titles')
                    return messages
                title = ' '.join(args[3:])
                indeces = [i for i in range(0, len(titles)) if title.lower() in titles[i].lower()]
                if not indeces:
                    messages.append(f'_{title}_ not found in custom stress titles')
                    return messages
                else:
                    stress = copy.deepcopy(self.char.stress)
                    modified = [stress[i] for i in range(0, len(stress)) if title.lower() not in titles[i].lower()]
                    titles = [t for t in titles if title.lower() not in t.lower()]
                    self.char.stress_titles = titles if titles else None
                    messages.append(f'_{title}_ removed from stress titles')
                    self.char.stress = modified
                    messages.append(f'{self.char.get_string_stress()}')
            else:
                total = args[2]
                title = ' '.join(args[3:])
                if total.lower() == "none":
                    self.char.stress = None
                    self.char.stress_titles = None
                    messages.append(f'{self.char.get_string()}')
                elif total.lower() == "fate":
                    self.char.stress = STRESS
                    self.char.stress_titles = SETUP.stress_titles
                elif total.lower() == "fae":
                    self.char.stress = SETUP.stress_FAE
                    self.char.stress_titles = SETUP.stress_titles_FAE
                elif total.lower() == "core":
                    self.char.stress = SETUP.stress_Core
                    self.char.stress_titles = SETUP.stress_titles_Core
                else:
                    if not total.isdigit():
                        messages.append('Stress shift must be a positive integer')
                        return messages
                    stress_boxes = []
                    [stress_boxes.append(['1', O]) for i in range(0, int(total))]
                    matches = [t for t in titles if title.lower() in t.lower()]
                    modified = copy.deepcopy(self.char.stress) if self.char.stress_titles and self.char.stress else ([] if self.char.npc or self.char.category != 'Character' else STRESS)
                    if matches:
                        for i in range(0, len(titles)):
                            if title.lower() in titles[i].lower():
                                modified[i] = stress_boxes
                    else:
                        titles.append(title)
                        self.char.stress_titles = titles
                        modified.append(stress_boxes)
                        messages.append(f'_{title}_ added to stress titles')
                    self.char.stress = modified
                messages.append(f'{self.char.get_string_stress()}')
        elif args[1] in ['refresh', 'r']:
            modified = copy.deepcopy(self.char.stress)
            if len(args) == 3:
                if args[2].lower() not in stress_checks:
                    messages.append(f'{args[2].lower()} is not a valid stress type for ***{self.char.name}*** - {stress_check_types}')
                    return messages
                else:
                    stress_type_str = args[2].lower()
                    stress_type = [i for i in range(0, len(stress_titles)) if stress_type_str in [stress_titles[i].lower()[0:2], stress_titles[i].lower()]][0]
                    stress_type_name = stress_titles[stress_type]
                    for s in range(0, len(self.char.stress[stress_type])):
                        modified[stress_type][s][1] = O
                    messages.append(f'Refreshed all of ***{self.char.name}\'s*** _{stress_type_name}_ stress')
                    self.char.stress = modified
                    messages.append(f'{self.char.get_string_stress()}')
            else:
                for i in range(0, len(self.char.stress)):
                    for s in range(0, len(self.char.stress[i])):
                        modified[i][s][1] = O
                messages.append(f'Refreshed all of ***{self.char.name}\'s*** stress')
                self.char.stress = modified
                messages.append(f'{self.char.get_string_stress()}')
        elif args[1] in ['delete', 'd']:
            if len(args) == 2:
                messages.append(f'No stress type provided - {stress_check_types}')
                return messages
            if args[2].lower() not in stress_checks:
                messages.append(f'{args[2].lower()} is not a valid stress type for ***{self.char.name}*** - {stress_check_types}')
                return messages
            if len(args) == 3:
                args = args + ('1',)
            if len(args) == 4:
                shift = args[3]
                if not shift.isdigit():
                    messages.append('Stress shift must be a positive integer')
                    return messages
                shift_int = int(shift)
                stress_type_str = args[2].lower()
                stress_type = [i for i in range(0, len(stress_titles)) if stress_type_str in [stress_titles[i].lower()[0:2], stress_titles[i].lower()]][0]
                stress_type_name = stress_titles[stress_type]
                available = self.get_available_stress(stress_type)
                if available == len(self.char.stress[stress_type]):
                    messages.append(f'***{self.char.name}*** has no _{stress_type_name}_ stress to remove')
                    return messages
                modified = copy.deepcopy(self.char.stress)
                for s in range(len(self.char.stress[stress_type])-1,-1,-1):
                    if shift_int > 0 and self.char.stress[stress_type][s][1] == X:
                        shift_int -= 1
                        modified[stress_type][s][1] = O
                messages.append(f'Removed {shift} from ***{self.char.name}\'s*** _{stress_type_name}_ stress')
                self.char.stress = modified
                messages.append(f'{self.char.get_string_stress()}')
        else:
            if len(args) == 2:
                args = args + ('1',)
            if args[1].lower() not in stress_checks:
                messages.append(f'{args[1].lower()} is not a valid stress type for ***{self.char.name}*** - {stress_check_types}')
                return messages
            shift = args[1] if args[1].isdigit() else args[2]
            if not shift.isdigit():
                messages.append('Stress shift must be a positive integer')
                return messages
            stress_type_str = args[1].lower()
            stress_type = [i for i in range(0, len(stress_titles)) if stress_type_str in [stress_titles[i].lower()[0:2], stress_titles[i].lower()]][0]
            stress_type_name = stress_titles[stress_type]
            shift_int = int(shift)
            available = self.get_available_stress(stress_type)
            if shift_int > available:
                messages.append(f'***{self.char.name}*** cannot absorb {shift} {stress_type_name} stress ({available} available)')
                return messages
            modified = copy.deepcopy(self.char.stress)
            for s in range(0,len(self.char.stress[stress_type])):
                if shift_int > 0 and self.char.stress[stress_type][s][1] == O:
                    shift_int -= 1
                    modified[stress_type][s][1] = X
            if not check_user:
                messages.append(f'***{self.char.name}*** absorbed {shift} {stress_type_name} stress')
                self.char.stress = modified
                messages.extend(self.absorb_shifts(int(shift)))
                messages.append(f'{self.char.get_string_stress()}')
        if check_user:
            return messages
        else:
            char_svc.save(self.char, self.user)
        return messages

    def consequence(self, args):
        """Add/edit consequences and conditions or customize a consequences or conditions track
        
        Parameters
        ----------
        args : list(str)
            List of strings with subcommands

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if args[1].lower() == 'help':
            messages.append(CONSEQUENCES_HELP)
            return messages
        modified = None
        consequences = copy.deepcopy(self.char.consequences) if self.char.consequences else CONSEQUENCES
        consequences_titles = copy.deepcopy(self.char.consequences_titles) if self.char.consequences_titles else CONSEQUENCES_TITLES
        use_consequences = len([c for c in consequences_titles if c in ['Mild', 'Moderate', 'Severe']]) == 3 and len(consequences_titles) == 3
        consequences_shifts = copy.deepcopy(self.char.consequences_shifts) if self.char.consequences_shifts else CONSEQUENCES_SHIFTS
        consequences_name = 'Consequence' if use_consequences else 'Condition'
        consequences_checks = []
        [consequences_checks.append(t[0:2].lower()) for t in consequences_titles]
        [consequences_checks.append(t.lower()) for t in consequences_titles]
        consequences_check_types = ' or '.join([f'({t[0:2].lower()}){t[2:].lower()}' for t in consequences_titles])
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d new c "CHARACTER NAME"```')
            return messages
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        if len(args) == 1:
            messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_consequences()}')
            return messages
        if args[1] in ['title', 't']:
            if len(args) == 2:
                messages.append(f'No Condition title provided')
                return messages
            if args[2] in ['delete', 'd']:
                if not self.char.consequences_titles:
                    messages.append('You have not defined any Condition titles')
                    return messages
                title = ' '.join(args[3:])
                indeces = [i for i in range(0, len(consequences_titles)) if title.lower() in consequences_titles[i].lower()]
                if not indeces:
                    messages.append(f'_{title}_ not found in Condition titles')
                    return messages
                else:
                    modified_consequences = []
                    modified_titles = []
                    modified_shifts = []
                    for i in range(0, len(consequences_titles)):
                        if title.lower() not in consequences_titles[i].lower():
                            modified_consequences.append(consequences[i])
                            modified_titles.append(consequences_titles[i])
                            modified_shifts.append(consequences_shifts[i])
                    self.char.consequences = modified_consequences
                    self.char.consequences_titles = modified_titles if modified_titles else None
                    self.char.consequences_shifts = modified_shifts if modified_shifts else None
                    messages.append(f'_{title}_ removed from Conditions titles')
            else:
                total = args[2]
                title = ' '.join(args[3:])
                if total == "None":
                    self.char.consequences = None
                    self.char.consequences_titles = None
                    self.char.consequences_shifts = None
                    messages.append(f'{self.char.get_string()}')
                elif total == "FATE":
                    self.char.consequences = CONSEQUENCES
                    self.char.consequences_titles = None
                    self.char.consequences_shifts = None
                else:
                    if not total.isdigit():
                        messages.append('Stress shift must be a positive integer')
                        return messages
                    if not self.char.consequences_titles:
                        consequences = []
                        consequences_titles = []
                        consequences_shifts = []
                    matches = [i for i in range(0, len(consequences_titles)) if title.lower() in consequences_titles[i].lower()]
                    if matches:
                        for i in range(0, len(consequences_titles)):
                            if title.lower() in consequences_titles[i].lower():
                                consequences[i] = [total, O]
                                consequences_titles[i] = title
                                consequences_shifts[i] = total
                        messages.append(f'Updated the _{title} ({total})_ Conditions title')
                    else:
                        consequences.append([total, O])
                        consequences_titles.append(title)
                        consequences_shifts.append(total)
                        messages.append(f'_{title} ({total})_ added to Conditions titles')
                    self.char.consequences = consequences
                    self.char.consequences_titles = consequences_titles
                    self.char.consequences_shifts = consequences_shifts
        elif args[1] in ['delete', 'd']:
            if len(args) == 2:
                messages.append(f'No severity provided - {consequences_check_types}')
                return messages
            if args[2].lower() not in consequences_checks:
                messages.append(f'{args[2].lower()} is not a valid severity - {consequences_check_types}')
                return messages
            severity_str = args[2].lower()
            severity = [i for i in range(0, len(consequences_titles)) if 1 if severity_str in [consequences_titles[i].lower()[0:2], consequences_titles[i].lower()]][0]
            severity_shift = consequences_shifts[severity]
            severity_name = consequences_titles[severity]
            if not self.char.consequences or self.char.consequences and self.char.consequences[severity][1] == O:
                messages.append(f'***{self.char.name}*** does not currently have a _{severity_name}_ {consequences_name}')
                return messages
            previous = copy.deepcopy(self.char.consequences)
            modified = copy.deepcopy(self.char.consequences)
            modified[severity] = [severity_shift, O]
            self.char.consequences = modified
            aspect = previous[severity][2] if use_consequences else severity_name
            messages.append(f'Removed ***{self.char.name}\'s*** _{severity_name}_ from {consequences_name} ("{aspect}")')
            messages.extend(self.aspect(['a', 'delete', aspect]))
        else:
            if len(args) == 2 and use_consequences:
                messages.append('Missing Consequence aspect')
                return messages
            if args[1].lower() not in consequences_checks:
                messages.append(f'{args[1].lower()} is not a valid severity - {consequences_check_types}')
                return messages
            severity_str = args[1].lower()
            severity = [i for i in range(0, len(consequences_titles)) if 1 if severity_str in [consequences_titles[i].lower()[0:2], consequences_titles[i].lower()]][0]
            severity_shift = consequences_shifts[severity]
            severity_name = consequences_titles[severity]
            if self.char.consequences[severity][1] == X:
                messages.append(f'***{self.char.name}*** already has a _{severity_name}_ {consequences_name} ("{self.char.consequences[severity][2]}")')
                return messages
            aspect = severity_name if not use_consequences else ' '.join(args[2:])
            modified = copy.deepcopy(self.char.consequences)
            if use_consequences:
                modified[severity] = [severity_shift, X, aspect]
            else:
                modified[severity] = [severity_shift, X]
            messages.append(f'***{self.char.name}*** absorbed {severity_shift} shift for a {severity_name} {consequences_name} "{aspect}"')
            messages.extend(self.aspect(['a', aspect]))
            self.char.consequences = modified
            # If the character is being targeted, then absorb any available shifts from the attack roll
            messages.extend(self.absorb_shifts(int(severity_shift)))
            # If the character is being targeted, then the consequence aspect should grant a free invoke
            messages.extend(self.add_free_invokes())
        messages.append(f'{self.char.get_string_consequences()}')
        char_svc.save(self.char, self.user)
        return messages

    def absorb_shifts(self, shift_int):
        """Absorb shifts from an attack
        
        Parameters
        ----------
        shift_int : int
            Number of shifts to absorb

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        targeted_by = Character.filter(active_target=str(self.char.id)).first()
        if targeted_by and targeted_by.last_roll and targeted_by.last_roll.get('shifts_remaining', 0) > 0:
            last_roll = copy.deepcopy(targeted_by.last_roll)
            shifts_remaining = last_roll['shifts_remaining']
            shifts_remaining = shifts_remaining - shift_int if shifts_remaining >= shift_int else 0
            last_roll['shifts_remaining'] = shifts_remaining
            targeted_by.last_roll = last_roll
            char_svc.save(targeted_by, self.user)
            messages.append(f'{targeted_by.active_action} from ***{targeted_by.name}*** has {p.no("shift", shifts_remaining)} left to absorb.')
        return messages

    def add_free_invokes(self):
        """Add free invokes on consequence aspects from an attack

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        targeted_by = Character.filter(active_target=str(self.char.id)).first()
        if targeted_by and targeted_by.last_roll:
            messages.extend(self.aspect(['a', 'c', 'st', 't', '1', 'Invokes']))
        return messages