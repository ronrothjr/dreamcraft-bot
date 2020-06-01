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
STRESS_HELP = SETUP.stress_help
CONSEQUENCES_HELP = SETUP.consequences_help
X = SETUP.x
O = SETUP.o
STRESS = SETUP.stress
STRESS_TITLES = SETUP.stress_titles
CONSEQUENCES = SETUP.consequences
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
        name, n - display and create new characters by name
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
        aspect, a - add/delete aspects
        boost, b - add aspects as a boost
        approach, app - add/edit approaches in the character sheet
        skill, sk - add/edit skills in the characater sheet
        stunt, s - add/delete stunts
        stress, st - add/edit stress tracks in the character sheet
        consequence, con - add/edit consequences and conditions in the character sheet
        custom - add/edit custom fields in the character sheet
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
        self.ctx = ctx
        self.args = args[1:] if args[0] in ['character', 'char', 'c'] else args
        self.npc = False
        if self.args and len(self.args) and self.args[0] and self.args[0].lower() == 'npc':
            self.npc = True
            self.args = self.args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'select'
        self.guild = guild
        self.user = user
        self.channel = channel
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.char = char if char else (Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None)
        self.can_edit = str(self.user.id) == str(self.char.user.id) or self.user.role == 'Game Master' if self.user and self.char else True
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
                'parent': self.parent,
                'p': self.get_parent,
                'name': self.name,
                'n': self.name,
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
                'aspect': self.aspect,
                'a': self.aspect,
                'boost': self.aspect,
                'b': self.aspect,
                'approach': self.approach,
                'app': self.approach,
                'skill': self.skill,
                'sk': self.skill,
                'stunt': self.stunt,
                's': self.stunt,
                'stress': self.stress,
                'st': self.stress,
                'consequence': self.consequence,
                'con': self.consequence,
                'custom': self.custom
            }
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: self.name)
                # Execute the function
                messages = func(self.args)
            else:
                match = self.search(self.args)
                if match:
                    self.args = ('select',) + self.args
                    self.command = 'select'
                    func = self.select
                else:
                    self.args = ('n',) + self.args
                    self.command = 'n'
                    func = self.name
                messages = func(self.args)
            # Send messages
            return messages
        except Exception as err:
            traceback.print_exc()
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

        if self.char:
            Log().create_new(str(self.char.id), f'Character: {self.char.name}', str(self.user.id), self.guild.name, 'Character', {'by': self.user.name, 'note': '"' + ' '.join(args[1:])} + '"', 'created')
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
            'svc': char_svc,
            'user': self.user,
            'title': 'Story',
            'type': 'view',
            'type_name': 'Story Log',
            'command': command,
            'getter': {
                'method': Log.get_by_page,
                'params': {
                    'params': {'parent_id': str(self.char.id)},
                    'sort': 'created'
                },
                'parent_method': Character.get_by_page,
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
            messages.extend(char_svc.get_parent_by_id(self.char, self.user, self.char.parent_id))
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
        char, name, get_string, get_short_string = char_svc.get_char_info(char, self.user)
        can_edit = str(self.user.id) == str(char.user.id) or self.user.role == 'Game Master' if self.user and char else True
        category = char.category if char else 'Character'
        dialog = {
            'create_character': ''.join([
                '**CREATE or SELECT A CHARACTER**```css\n',
                '.d character YOUR_CHARACTER\'S_NAME```'
            ]),
            'active_character': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n' if can_edit else '',
                f':point_down:\n\n{get_string}'
            ]),
            'rename_delete': ''.join([
                f'\n\n_Is ***{name}*** not the {category.lower()} name you wanted?_',
                f'```css\n.d c rename NEW_NAME```_Want to remove ***{name}***?_',
                '```css\n.d c delete```'
            ]) if can_edit else '',
            'active_character_short': ''.join([
                f'***THIS IS YOUR ACTIVE CHARACTER:***\n',
                f':point_down:\n\n{get_short_string}'
            ]),
            'add_more_info': ''.join([
                f'Add more information about ***{name}***',
                '```css\n.d c description CHARACTER_DESCRIPTION\n',
                '.d c high concept HIGH_CONCEPT\n.d c trouble TROUBLE```'
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
                '```css\n.d c aspect ASPECT_NAME\n',
                '.d c aspect delete ASPECT_NAME```',
                f'Give  ***{name}*** some cool stunts',
                '```css\n.d c stunt STUNT_NAME\n',
                '.d c stunt delete STUNT_NAME```'
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

    def name(self, args):
        """Display and create a new Character by name
        
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
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_character_short')]
            if len(args) == 1 and self.char:
                return [self.dialog('')]
            char_name = ' '.join(args[1:])
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
                def canceler(cancel_args):
                    if cancel_args[0].lower() in ['character','char','c']:
                        return CharacterCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                    else:
                        self.parent.args = cancel_args
                        self.parent.command = self.parent.args[0]
                        return self.parent.get_messages()

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
                    'command': 'c ' + ('npc ' if self.npc else '' ) + ' '.join(args),
                    'type': 'select',
                    'type_name': 'CHARACTER',
                    'getter': {
                        'method': Character.get_by_page,
                        'params': {'params': {'name__icontains': char_name, 'guild': self.guild.name, 'category': 'Character', 'archived': False, 'npc': self.npc}}
                    },
                    'formatter': formatter,
                    'cancel': canceler,
                    'select': selector,
                    'empty': {
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
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_character_short')]
            if len(args) == 1 and self.char:
                return [self.dialog('')]
            char_name = ' '.join(args[1:])
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['character','char','c']:
                    return CharacterCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

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
                    'params': {'params': {'user': self.user, 'name__icontains': char_name, 'guild': self.guild.name, 'npc': self.npc, 'archived': False}}
                },
                'formatter': formatter,
                'cancel': canceler,
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
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['character','char','c']:
                return CharacterCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

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
            'cancel': canceler,
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
            raise Exception('No active character for deletion')
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        if self.char.category != 'Character':
            category = ('an ' if self.char.category[0:1].lower() in ['a','e','i','o','u'] else 'a ') + self.char.category
            raise Exception(f'You may only copy characters. ***{self.char.name}*** is {category}.')
        guilds = [g['guild'] for g in Character().get_guilds() if g['guild'] and g['guild'].lower() not in self.guild.name.lower()]
        if not guilds:
            raise Exception('You may not copy until you have created a character on another server')
        guild_list = f'***Guilds:***\n' + '\n'.join([f'    ***{g}***' for g in guilds])
        guild_commands = '\n'.join([f'.d c copy to {g}' for g in guilds[0:5]])
        guild_commands_str = f'\nTry one of these:```css\n{guild_commands}```'
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
        messages.append(f'***{self.char.name}*** copied to ***{guild}***')
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
        search = ''
        if not self.char:
            return ['No active character for deletion']
        if not self.can_edit:
            raise Exception('You do not have permission to delete this character')
        search = self.char.name
        parent_id = str(self.char.parent_id) if self.char.parent_id else ''
        command = 'c ' + ('npc ' if self.npc else '' ) + ' '.join(args)
        question = ''.join([
            f'Are you sure you want to delete this {self.char.category}?\n\n{self.char.get_string()}',
            f'\n\nREPEAT THE COMMAND\n\n***OR***\n\nREPLY TO CONFIRM:',
            '```css\n.d YES /* to confirm the command */\n.d NO /* to reject the command */\n.d CANCEL /* to cancel the command */```'
        ])
        if self.user.command == command:
            answer = self.user.answer
            if answer:
                if answer.lower() in ['yes', 'y']:
                    search = self.char.name
                    self.char.reverse_archive(self.user)
                    self.char.archived = True
                    char_svc.save(self.char, self.user)
                    self.user.active_character = None
                    char_svc.save_user(self.user)
                    messages.append(''.join([
                        f'***{search}*** removed\n\n',
                        'You can restore this character at any time:',
                        f'```css\n.d c restore {search}```'
                    ]))
                elif answer.lower() in ['no', 'n', 'cancel', 'c']:
                    messages.append(f'Command ***"{command}"*** canceled')
                else:
                    raise Exception(f'Please answer the question regarding ***"{command}"***:\n\n{question}')
                self.user.command = ''
                self.user.question = ''
                self.user.answer = ''
                char_svc.save_user(self.user)
            else:
                Exception(f'No answer was received to command ***"{command}"***')
        else:
            self.user.command = command
            self.user.question = question
            self.user.answer = ''
            char_svc.save_user(self.user)
            messages.extend([question])
        if parent_id:
            messages.extend(char_svc.get_parent_by_id(self.char, self.user, parent_id))
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
        chars = []
        chars.extend(Character.filter(name=char_name, guild=self.guild.name, archived=True).all())
        if not chars:
            self.user.command = ''
            self.user.question = ''
            self.user.answer = ''
            char_svc.save_user(self.user)
            return [f'{char_name} was not found. No changes made.\nTry this: ```css\n.d c CHARACTER_NAME```']
        else:
            if chars and len(chars) > 1:
                prompt = ''. join ([
                    '\n\nSELECT A CHARACTER USING:```css\n',
                    '.d CHARACTER_NUMBER\n',
                    '/* EXAMPLE .d 2 */```\n',
                    'OR\n\n',
                    'YOU CAN CANCEL THE COMAND:',
                    '```css\n.d CANCEL```'
                ])
                selections = '\n\n'.join([f'CHARACTER {i + 1}\n{chars[i].get_short_string()}' for i in range(0, len(chars))])
                command = 'c ' + ('npc ' if self.npc else '' ) + ' '.join(args)
                if self.user.command != command:
                    question = f'{selections}{prompt}'
                    messages.append(question)
                    self.user.command = command
                    self.user.question = question
                    self.user.answer = ''
                    char_svc.save_user(self.user)
                else:
                    answer = self.user.answer
                    if answer.lower() in ['cancel','c']:
                        self.user.command = ''
                        self.user.question = ''
                        self.user.answer = ''
                        self.user.set_active_character(self.char)
                        char_svc.save_user(self.user)
                        messages.append('Comand canceled')
                    elif answer.isdigit():
                        char_num = int(answer)
                        if char_num > len(chars) or char_num < 1:
                            Exception(f'Character number {char_num} does not exist')
                        self.char = chars[int(answer)-1]
                        self.user.command = ''
                        self.user.question = ''
                        self.user.answer = ''
                        self.user.set_active_character(self.char)
                        char_svc.save_user(self.user)
                        current_chars = []
                        current_chars.extend(Character.filter(name=char_name, guild=self.guild.name, archived=False).all())
                        if current_chars:
                            Exception(''.join([
                                f'Cannot restore {char_name} while characters with that name already exist.\n\n',
                                f'Try deleting and retoring one of them.```css\n.d c delete {char_name}\n',
                                f'\n.d c restore {char_name}```'
                            ]))
                        if self.user.role in ['Admin', 'Game Master'] or str(self.user.id) == str(self.user.char.id):
                            self.char.archived = False
                            char_svc.save(self.char, self.user)
                        else:
                            raise Exception('You do not have permission to edit this character')
                        messages.append(self.dialog(''))
                    else:
                        raise Exception(prompt)
            else:
                self.char = chars[0]
                self.user.set_active_character(self.char)
                char_svc.save_user(self.user)
                if self.user.role in ['Admin', 'Game Master'] or str(self.user.id) == str(self.user.char.id):
                    self.char.archived = False
                    char_svc.save(self.char, self.user)
                else:
                    raise Exception('You do not have permission to edit this character')
                messages.append(self.dialog(''))
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
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
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
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
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
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
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
            return ['You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```']
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
            raise Exception('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        messages = []
        if len(args) == 1:
            raise Exception('No custom name provided. Try this: ```css\n.d c custom CUSTOM_NAME\n/* EXAMPLE:\n.d c custom Home World */```')
        if len(args) == 2:
            raise Exception('No custom property information provided. Try this: ```css\n.d c custom CUSTOM_NAME_ABBREVIATION CUSTOM_PROPERTY_INFORMATION\n/* EXAMPLE:\n.d c custom Home Earth (alternate history) */```')
        if args[1] in ['delete', 'd']:
            custom_properties = copy.deepcopy(self.char.custom_properties) if self.char.custom_properties else {}
            display_name = TextUtils.clean(args[2])
            property_name = display_name.lower().replace(' ', '_')
            if property_name not in custom_properties:
                raise Exception('***{self.char.name}*** does not have a custom property named {display_name}')
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
            raise Exception('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
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
            messages.append('Approach syntax: .d (app)roach {approach} {bonus}')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
            elif not self.can_edit:
                raise Exception('You do not have permission to edit this character')
            else:
                if args[1].lower() == 'delete' or args[1].lower() == 'd':
                    skill = [s for s in APPROACHES if args[2][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else args[2]
                    if skill in self.char.skills:
                        new_skills = {}
                        for key in self.char.skills:
                            if key != skill:
                                new_skills[key] = self.char.skills[key]
                        self.char.skills = new_skills
                    char_svc.save(self.char, self.user)
                    messages.append(f'Removed {skill}')
                else:
                    for i in range(1, len(args), 2):
                        abbr = args[i][0:2].lower()
                        val = args[i+1]
                        skill = [s for s in APPROACHES if abbr == s[0:2].lower()]
                        skill = skill[0].split(' - ')[0] if skill else args[i]
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
            messages.append('Skill syntax: .d (sk)ill {skill} {bonus}')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
            elif not self.can_edit:
                raise Exception('You do not have permission to edit this character')
            else:
                if args[1].lower() == 'delete' or args[1].lower() == 'd':
                    skill = [s for s in SKILLS if args[2][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else args[2]
                    if skill in self.char.skills:
                        new_skills = {}
                        for key in self.char.skills:
                            if key != skill:
                                new_skills[key] = self.char.skills[key]
                        self.char.skills = new_skills
                    char_svc.save(self.char, self.user)
                    messages.append(f'Removed {skill} skill') 
                else:
                    for i in range(1, len(args), 2):
                        abbr = args[i][0:2].lower()
                        val = args[i+1]
                        skill = [s for s in SKILLS if abbr == s[0:2].lower()]
                        skill = skill[0].split(' - ')[0] if skill else args[i]
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
        if len(args) == 1:
            if not self.asp:
                return ['You don\'t have an active aspect.\nTry this: ```css\n.d c a {aspect}```']
            messages.append(f'{self.asp.get_string(self.char)}')
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```']
        elif not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        elif args[1].lower() == 'list':
            return [self.char.get_string_aspects(self.user)]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            aspect = ' '.join(args[2:])
            for a in Character().get_by_parent(self.char, aspect, 'Aspect'):
                aspect = str(a.name)
                a.reverse_archive(self.user)
                a.archived = True
                char_svc.save(a, self.user)
            messages.append(f'"{aspect}" removed from aspects')
            messages.append(self.char.get_string_aspects(self.user))
        elif args[1].lower() in ['character', 'char', 'c']:
            if not self.asp:
                return ['You don\'t have an active aspect.\nTry this: ```css\n.d c a {aspect}```']
            self.user.active_character = str(self.asp.id)
            char_svc.save_user(self.user)
            self.char.active_aspect = str(self.asp.id)
            self.char.active_character = str(self.asp.id)
            char_svc.save(self.char, self.user)
            command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args[1:], guild=self.guild, user=self.user, char=self.asp, channel=self.channel)
            messages.extend(command.run())
        else:
            aspect = ' '.join(args[1:])
            self.asp = Character().get_or_create(self.user, aspect, self.guild.name, self.char, 'Aspect')
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
        if len(args) == 1:
            if not self.stu:
                return ['You don\'t have an active stunt.\nTry this: ```css\n.d c a {aspect}```']
            messages.append(f'{self.stu.get_string(self.char)}')
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```']
        elif not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        elif args[1].lower() == 'list':
            return [self.char.get_string_stunts(self.user)]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            stunt = ' '.join(args[2:])
            for s in Character().get_by_parent(self.char, stunt, 'Stunt'):
                stunt = str(s.name)
                s.reverse_archive(self.user)
                s.archived = True
                char_svc.save(s, self.user)
            messages.append(f'"{stunt}" removed from stunts')
            messages.append(self.char.get_string_stunts(self.user))
        elif args[1].lower() in ['character', 'char', 'c']:
            self.user.active_character = str(self.stu.id)
            char_svc.save_user(self.user)
            self.char.active_stunt = str(self.stu.id)
            self.char.active_character = str(self.stu.id)
            char_svc.save(self.char, self.user)
            command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args[1:], guild=self.guild, user=self.user, channel=self.channel, char=self.stu)
            messages.extend(command.run())
        else:
            stunt = ' '.join(args[1:])
            self.stu = Character().get_or_create(self.user, stunt, self.guild.name, self.char, 'Stunt')
            self.char.active_stunt = str(self.stu.id)
            self.char.active_character = str(self.stu.id)
            char_svc.save(self.char, self.user)
            messages.append(self.char.get_string_stunts(self.user) + '\n')
            messages.append(self.dialog('edit_active_stunt'))
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

        return sum([1 for s in self.char.stress[stress_type] if s[1] == O]) if self.char.stress else 0

    def stress(self, args, check_user=None):
        """Add/edit stress or customize a stress track
        
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
            messages.append(STRESS_HELP)
            return messages
        if args[1].lower() == 'help':
            messages.append(STRESS_HELP)
            return messages
        modified = None
        stress_titles = self.char.stress_titles if self.char.stress_titles else STRESS_TITLES
        stress_checks = []
        [stress_checks.append(t[0:2].lower()) for t in stress_titles]
        [stress_checks.append(t.lower()) for t in stress_titles]
        stress_check_types = ' or '.join([f'({t[0:2 ].lower()}){t[2:].lower()}' for t in stress_titles])
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
            return messages
        if not self.can_edit:
            raise Exception('You do not have permission to edit this character')
        if len(args) == 1:
            messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_stress()}')
            return messages
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
            shift = args[2]
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
        consequences_shifts = copy.deepcopy(self.char.consequences_shifts) if self.char.consequences_shifts else CONSEQUENCES_SHIFTS
        consequences_name = 'Condition' if self.char.consequences_titles else 'Consequence'
        consequences_checks = []
        [consequences_checks.append(t[0:2].lower()) for t in consequences_titles]
        [consequences_checks.append(t.lower()) for t in consequences_titles]
        consequences_check_types = ' or '.join([f'({t[0:2].lower()}){t[2:].lower()}' for t in consequences_titles])
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ```css\n.d c CHARACTER_NAME```')
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
            if self.char.consequences[severity][1] == O:
                messages.append(f'***{self.char.name}*** does not currently have a _{severity_name}_ {consequences_name}')
                return messages
            previous = copy.deepcopy(self.char.consequences)
            modified = copy.deepcopy(self.char.consequences)
            modified[severity] = [severity_shift, O]
            self.char.consequences = modified
            aspect = severity_name if self.char.consequences_titles else previous[severity][2]
            messages.append(f'Removed ***{self.char.name}\'s*** _{severity_name}_ from {consequences_name} ("{aspect}")')
            messages.extend(self.aspect(['a', 'd', aspect]))
        else:
            if len(args) == 2 and not self.char.consequences_titles:
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
            aspect = severity_name if self.char.consequences else ' '.join(args[2:])
            modified = copy.deepcopy(self.char.consequences)
            if self.char.consequences_titles:
                modified[severity] = [severity_shift, X]
            else:
                modified[severity] = [severity_shift, X, aspect]
            messages.append(f'***{self.char.name}*** absorbed {severity_shift} shift for a {severity_name} {consequences_name} "{aspect}"')
            messages.extend(self.aspect(['a', aspect]))
            self.char.consequences = modified
            messages.extend(self.absorb_shifts(int(severity_shift)))
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