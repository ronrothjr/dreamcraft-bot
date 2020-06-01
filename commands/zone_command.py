# zone_command
import traceback
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Character, User, Log
from config.setup import Setup
from services.zone_service import ZoneService
from utils import Dialog, T

zone_svc = ZoneService()
SETUP = Setup()
ZONE_HELP = SETUP.zone_help

class ZoneCommand():
    """
    Handle 'zone', 'z' commands and subcommands

    Subcommands:
        help - display a set of instructions on ZoneCommand usage
        note - add a note to the zone
        say - add dialog to the zone from the zone
        story - display the zone's story
        name, n - display and create new zones by name
        description, desc - add/edit the Description in the zone
        select - display existing zone
        character, char, c - edit the zone as a character
        list, l - display a list of existing characters and NPCs
        players, player, p - add players to the zone
        delete - remove an zone (archive)
    """

    def __init__(self, parent, ctx, args, guild, user, channel):
        """
        Command handler for ZoneCommand

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
        ZoneCommand - object for processing zone commands and subcommands
        """
    
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:] if args[0] in ['zone', 'z'] else args
        self.guild = guild
        self.user = user
        self.command = self.args[0].lower() if len(self.args) > 0 else 'select'
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.can_edit = self.user.role == 'Game Master' if self.user and self.zone else True
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        try:
            switcher = {
                'help': self.help,
                'name': self.name,
                'n': self.name,
                'select': self.select,
                'say': self.say,
                'note': self.note,
                'story': self.story,
                'description': self.description,
                'desc': self.description,
                'character': self.character,
                'char': self.character,
                'c': self.character,
                'players': self.player,
                'player': self.player,
                'p': self.player,
                'list': self.zone_list,
                'l': self.zone_list,
                'delete': self.delete_zone,
                'd': self.delete_zone
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
                # Execute the function
                messages = func(self.args)
            # Send messages
            return messages
        except Exception as err:
            traceback.print_exc()
            return list(err.args)

    def help(self, args):
        return [ZONE_HELP]

    def search(self, args):
        params = {'name__icontains': ' '.join(args[0:]), 'guild': self.guild.name, 'channel_id': str(self.channel.id), 'archived': False}
        return zone_svc.search(args, Zone.filter, params)

    def note(self, args):
        if self.zone:
            Log().create_new(str(self.zone.id), f'Zone: {self.zone.name}', str(self.user.id), self.guild.name, 'Zone', {'by': self.user.name, 'note': ' '.join(args[1:])}, 'created')
            return ['Log created']
        else:
            return ['No active zone to log']

    def say(self, args):
        if not self.zone:
            return ['No active zone to log']
        else:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.zone.id), f'Zone: {self.zone.name}', str(self.user.id), self.guild.name, 'Zone', {'by': self.user.name, 'note': f'***Narrator*** says, "{note_text}"'}, 'created')
            return ['Log created']

    def story(self, args):
        messages =[]
        command = 'zone ' + (' '.join(args))
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['zone','s']:
                self.args = cancel_args
                self.command = self.args[0]
                return self.run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()
        response = Dialog({
            'svc': zone_svc,
            'user': self.user,
            'title': 'Story',
            'type': 'view',
            'type_name': 'Story Log',
            'command': command,
            'getter': {
                'method': Log.get_by_page,
                'params': {
                    'params': {'parent_id': str(self.sc.id)},
                    'sort': 'created'
                },
                'parent_method': Zone.get_by_page,
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

    def dialog(self, dialog_text, zone=None):
        zone, name, get_string, get_short_string = zone_svc.get_zone_info(zone if zone else self.zone, self.channel)
        category = zone.category if zone else 'Zone'
        dialog = {
            'create_zone': ''.join([
                '**CREATE or ZONE**```css\n',
                '.d zone YOUR_ZONE\'S_NAME```'
            ]),
            'active_zone': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n' if self.can_edit else '',
                f':point_down:\n\n{get_string}'
            ]),
            'active_zone_short': ''.join([
                '***YOU ARE CURRENTLY EDITING...:***\n' if self.can_edit else '',
                f':point_down:\n\n{get_short_string}'
            ]),
            'rename_delete': ''.join([
                f'\n\n_Is ***{name}*** not the {category.lower()} name you wanted?_',
                f'```css\n.d zone rename NEW_NAME```_Want to remove ***{name}***?_',
                '```css\n.d zone delete```'
            ]),
            'go_back_to_parent': ''.join([
                f'\n\n***You can GO BACK to the parent zone, aspect, or stunt***',
                '```css\n.d zone parent```'
            ])
        }
        dialog_string = ''
        if dialog_text == 'all':
            if not zone:
                dialog_string += dialog.get('create_zone', '')
            dialog_string += dialog.get('rename_delete', '')
        elif zone.category == 'Zone':
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_zone', '')
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
        else:
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_zone', '') if self.can_edit else ''
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
                dialog_string += dialog.get('go_back_to_parent', '') if self.can_edit else ''
        return dialog_string
    
    def name(self, args):
        if not self.sc:
            raise Exception('No active scene or name provided. Try this:```css\n.d scene SCENE_NAME```')
        messages = []
        if len(args) == 0:
            if not self.zone:
                return [
                    'No active zone or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.zone.get_string(self.channel))
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_zone_short')]
            if len(args) == 1 and self.zone:
                return [self.dialog('')]
            zone_name = ' '.join(args[1:])
            if len(args) > 1 and args[1] == 'rename':
                zone_name = ' '.join(args[2:])
                if not self.zone:
                    return [
                        'No active zone or name provided\n\n',
                        self.dialog('all')
                    ]
                else:
                    zone = Zone().find(self.guild.name, str(self.channel.id), str(self.sc.id), zone_name)
                    if zone:
                        return [f'Cannot rename to _{zone_name}_. Zone already exists']
                    else:
                        self.zone.name = zone_name
                        zone_svc.save(self.zone, self.user)
                        messages.append(self.dialog(''))
            else:
                def canceler(cancel_args):
                    if cancel_args[0].lower() in ['zone','z']:
                        return ZoneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                    else:
                        self.parent.args = cancel_args
                        self.parent.command = self.parent.args[0]
                        return self.parent.get_messages()

                def selector(selection):
                    self.zone = selection
                    self.channel.set_active_zone(self.zone, self.user)
                    self.user.set_active_character(self.zone.character)
                    zone_svc.save_user(self.user)
                    return [self.dialog('')]

                messages.extend(Dialog({
                    'svc': zone_svc,
                    'user': self.user,
                    'title': 'Zone List',
                    'command': 'zone ' + ' '.join(args),
                    'type': 'select',
                    'type_name': 'ZONE',
                    'getter': {
                        'method': Zone.get_by_page,
                        'params': {'params': {'name__icontains': zone_name, 'channel_id': str(self.channel.id), 'guild': self.guild.name, 'archived': False}}
                    },
                    'formatter': lambda item, item_num, page_num, page_size: f'_ZONE #{item_num+1}_\n{item.get_short_string()}',
                    'cancel': canceler,
                    'select': selector,
                    'empty': {
                        'method': Zone().get_or_create,
                        'params': {'user': self.user, 'name': zone_name, 'scene': self.sc, 'channel': self.channel, 'guild': self.guild.name}
                    }
                }).open())
        return messages
    
    def select(self, args):
        messages = []
        if len(args) == 0:
            if not self.zone:
                return [
                    'No active zone or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.zone.get_string(self.channel))
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_zone_short')]
            if len(args) == 1 and self.char:
                return [self.dialog('')]
            zone_name = ' '.join(args[1:])
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['zone','z']:
                    return ZoneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

            def selector(selection):
                self.zone = selection
                self.channel.set_active_zone(self.zone, self.user)
                self.user.set_active_character(self.zone)
                zone_svc.save_user(self.user)
                return [self.dialog('')]

            messages.extend(Dialog({
                'svc': zone_svc,
                'user': self.user,
                'title': 'Zone List',
                'command': 's ' + ' '.join(args),
                'type': 'select',
                'type_name': 'ZONE',
                'getter': {
                    'method': Zone.get_by_page,
                    'params': {'params': {'name__icontains': zone_name, 'scene_id': str(self.sc.id), 'guild': self.guild.name, 'archived': False}}
                },
                'formatter': lambda item, item_num, page_num, page_size: f'_ZONE #{item_num+1}_\n{item.get_short_string()}',
                'cancel': canceler,
                'select': selector
            }).open())
        return messages

    def zone_list(self, args):
        messages = []
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['zone']:
                return ZoneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        messages.extend(Dialog({
            'svc': zone_svc,
            'user': self.user,
            'title': 'Zone List',
            'command': 'zone ' + (' '.join(args)),
            'type': 'view',
            'type_name': 'ZONE',
            'getter': {
                'method': Zone().get_by_scene,
                'params': {'scene': self.sc, 'archived': False}
            },
            'formatter': lambda item, item_num, page_num, page_size: f'{item.get_short_string(self.channel)}',
            'cancel': canceler
        }).open())
        return messages

    def description(self, args):
        if len(args) == 1:
            return ['No description provided']
        if not self.zone:
            return ['You don\'t have an active zone.\nTry this: ".d s name {name}"']
        else:
            description = ' '.join(args[1:])
            self.zone.description = description
            self.zone.updated_by = str(self.user.id)
            self.zone.updated = T.now()
            self.zone.save()
            return [
                f'Description updated to "{description}"',
                self.zone.get_string(self.channel)
            ]

    def character(self, args):
        if self.user:
            self.user.active_character = str(self.zone.character.id)
            self.user.updated_by = str(self.user.id)
            self.user.updated = T.now()
            self.user.save()
        command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args, guild=self.guild, user=self.user, channel=self.channel, char=self.zone.character)
        return command.run()

    def player(self, args):
        return zone_svc.player(args, self.channel, self.zone, self.user)

    def delete_zone(self, args):
        return zone_svc.delete_zone(args, self.guild, self.channel, self.sc, self.zone, self.user)