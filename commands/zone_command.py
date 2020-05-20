# zone_command
import traceback
import datetime
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Character, User, Log
from config.setup import Setup
from services.zone_service import ZoneService
from utils import Dialog

zone_svc = ZoneService()
SETUP = Setup()
ZONE_HELP = SETUP.zone_help

class ZoneCommand():
    def __init__(self, parent, ctx, args, guild=None, user=None):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.guild = guild
        self.user = user
        self.command = self.args[0].lower() if len(self.args) > 0 else 'n'
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        try:
            switcher = {
                'help': self.help,
                'name': self.name,
                'n': self.name,
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
        if self.sc:
            Log().create_new(str(self.sc.id), f'Zone: {self.sc.name}', str(self.user.id), self.guild.name, 'Zone', {'by': self.user.name, 'note': ' '.join(args[1:])}, 'created')
            return ['Log created']
        else:
            return ['No active zone to log']

    def say(self, args):
        if not self.sc:
            return ['No active zone to log']
        else:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.sc.id), f'Zone: {self.sc.name}', str(self.user.id), self.guild.name, 'Zone', {'by': self.user.name, 'note': f'***Narrator*** says, "{note_text}"'}, 'created')
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
            'formatter': lambda log, num, page_num, page_size: log.get_short_string(), # if log.category == 'Log' else log.get_string()
            'cancel': canceler,
            'page_size': 10
        }).open()
        messages.extend(response)
        return messages

    def dialog(self, dialog_text, sc=None):
        sc, name, get_string, get_short_string = zone_svc.get_zone_info(self.sc, self.channel)
        category = sc.category if sc else 'Zone'
        dialog = {
            'create_zone': ''.join([
                '**CREATE or ZONE**```css\n',
                '.d zone YOUR_ZONE\'S_NAME```'
            ]),
            'active_zone': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n',
                f':point_down:\n\n{get_string}'
            ]),
            'active_zone_short': ''.join([
                f'***YOU ARE CURRENTLY EDITING...:***\n',
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
            if not sc:
                dialog_string += dialog.get('create_zone', '')
            dialog_string += dialog.get('rename_delete', '')
        elif sc.category == 'Zone':
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
        if not self.scene:
            raise Exception('No active scene or name provided. Try this:```css\n.d scene SCENE_NAME```')
        messages = []
        if len(args) == 0:
            if not self.sc:
                return [
                    'No active zone or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.sc.get_string())
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_zone_short')]
            if len(args) == 1 and self.sc:
                return [self.dialog('')]
            zone_name = ' '.join(args[1:])
            if len(args) > 1 and args[1] == 'rename':
                zone_name = ' '.join(args[2:])
                if not self.sc:
                    return [
                        'No active zone or name provided\n\n',
                        self.dialog('all')
                    ]
                else:
                    zone = Zone().find(self.user, zone_name, self.guild.name)
                    if zone:
                        return [f'Cannot rename to _{zone_name}_. Zone already exists']
                    else:
                        self.sc.name = zone_name
                        zone_svc.save(self.sc, self.user)
                        messages.append(self.dialog(''))
            else:
                def canceler(cancel_args):
                    if cancel_args[0].lower() in ['zone','z']:
                        return ZoneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user).run()
                    else:
                        self.parent.args = cancel_args
                        self.parent.command = self.parent.args[0]
                        return self.parent.get_messages()

                def selector(selection):
                    self.sc = selection
                    self.channel.set_active_zone(self.sc, self.user)
                    self.user.set_active_character(self.sc.character)
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
                        'params': {'user': self.user, 'name': zone_name, 'scene': self.scene, 'channel': self.channel, 'guild': self.guild.name}
                    }
                }).open())
        return messages
    
    def select(self, args):
        messages = []
        if len(args) == 0:
            if not self.sc:
                return [
                    'No active zone or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.sc.get_string())
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_zone_short')]
            if len(args) == 1 and self.char:
                return [self.dialog('')]
            sc_name = ' '.join(args[1:])
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['zone','s']:
                    return ZoneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

            def selector(selection):
                self.char = selection
                self.user.set_active_character(self.sc)
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
                    'params': {'params': {'name__icontains': sc_name, 'scene_id': str(self.scene.id), 'guild': self.guild.name, 'archived': False}}
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
                return ZoneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user).run()
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
            'getter': {
                'method': Zone().get_by_scene,
                'params': {'scene': self.scene, 'archived': False}
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
            if (not self.zone.created):
                self.zone.created = datetime.datetime.utcnow()
            self.zone.updated_by = str(self.user.id)
            self.zone.updated = datetime.datetime.utcnow()
            self.zone.save()
            return [
                f'Description updated to "{description}"',
                self.zone.get_string(self.channel)
            ]

    def character(self, args):
        if self.user:
            self.user.active_character = str(self.zone.character.id)
            if (not self.user.created):
                self.user.created = datetime.datetime.utcnow()
            self.user.updated_by = str(self.user.id)
            self.user.updated = datetime.datetime.utcnow()
            self.user.save()
        command = CharacterCommand(self.parent, self.ctx, args, self.zone.character)
        return command.run()

    def player(self, args):
        if len(args) == 1:
            return ['No characters added']
        if not self.zone:
            return ['You don\'t have an active zone.\nTry this: ".d s name {name}"']
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [self.zone.get_string_characters(self.channel)]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            char = ' '.join(args[2:])
            [self.zone.characters.remove(s) for s in self.zone.characters if char.lower() in s.lower()]
            if (not self.zone.created):
                self.zone.created = datetime.datetime.utcnow()
            self.zone.updated_by = str(self.user.id)
            self.zone.updated = datetime.datetime.utcnow()
            self.zone.save()
            return [
                f'{char} removed from zone characters',
                self.zone.get_string_characters(self.channel)
            ]
        else:
            search = ' '.join(args[1:])
            char = Character().find(None, search, self.channel.guild)
            if char:
                self.zone.characters.append(str(char.id))
            else:
                return [f'***{search}*** not found. No character added to _{self.zone.name}_']
            if (not self.zone.created):
                self.zone.created = datetime.datetime.utcnow()
            self.zone.updated_by = str(self.user.id)
            self.zone.updated = datetime.datetime.utcnow()
            self.zone.save()
            return [
                f'Added {char.name} to zone characters',
                self.zone.get_string_characters(self.channel)
            ]

    def delete_zone(self, args):
        messages = []
        search = ''
        if len(args) == 1:
            if not self.zone:
                return ['No zone provided for deletion']
        else:
            search = ' '.join(args[1:])
            self.zone = Zone().find(self.guild.name, str(self.channel.id), str(self.sc.id), search)
        if not self.zone:
            return [f'{search} was not found. No changes made.']
        else:
            search = str(self.zone.name)
            zone_id = str(self.zone.zone_id) if self.zone.zone_id else ''
            channel_id = str(self.zone.channel_id) if self.zone.channel_id else ''
            self.zone.character.archive(self.user)
            self.zone.archived = True
            self.zone.updated_by = str(self.user.id)
            self.zone.updated = datetime.datetime.utcnow()
            self.zone.save()
            messages.append(f'***{search}*** removed')
            if zone_id:
                secenario = Zone().get_by_id(zone_id)
                messages.append(secenario.get_string(self.channel))
            elif channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages