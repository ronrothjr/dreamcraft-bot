# scene_command
import traceback
import datetime
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Character, User, Log
from config.setup import Setup
from services import SceneService, ScenarioService
from utils import Dialog

scene_svc = SceneService()
scenario_svc = ScenarioService()
SETUP = Setup()
SCENE_HELP = SETUP.scene_help

class SceneCommand():
    def __init__(self, parent, ctx, args, guild, user, channel):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.guild = guild
        self.user = user
        self.command = self.args[0].lower() if len(self.args) > 0 else 'n'
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.can_edit = self.user.role == 'Game Master' if self.user and self.sc else True
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        try:
            switcher = {
                'help': self.help,
                'note': self.note,
                'say': self.say,
                'story': self.story,
                'name': self.name,
                'n': self.name,
                '=': self.select,
                'description': self.description,
                'desc': self.description,
                'character': self.character,
                'char': self.character,
                'c': self.character,
                'players': self.player,
                'player': self.player,
                'p': self.player,
                'list': self.scene_list,
                'l': self.scene_list,
                'delete': self.delete_scene,
                'd': self.delete_scene
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
        return [SCENE_HELP]

    def search(self, args):
        params = {'name__icontains': ' '.join(args[0:]), 'guild': self.guild.name, 'channel_id': str(self.channel.id), 'archived': False}
        return scene_svc.search(args, Scene.filter, params)

    def note(self, args):
        if self.sc:
            Log().create_new(str(self.sc.id), f'Scene: {self.sc.name}', str(self.user.id), self.guild.name, 'Scene', {'by': self.user.name, 'note': ' '.join(args[1:])}, 'created')
            return ['Log created']
        else:
            return ['No active scene to log']

    def say(self, args):
        if not self.sc:
            return ['No active scene to log']
        else:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.sc.id), f'Scene: {self.sc.name}', str(self.user.id), self.guild.name, 'Scene', {'by': self.user.name, 'note': f'***Narrator*** says, "{note_text}"'}, 'created')
            return ['Log created']

    def story(self, args):
        messages =[]
        command = 'scene ' + (' '.join(args))
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['scene','s']:
                self.args = cancel_args
                self.command = self.args[0]
                return self.run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()
        response = Dialog({
            'svc': scene_svc,
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
                'parent_method': Scene.get_by_page,
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
        sc, name, get_string, get_short_string = scene_svc.get_scene_info(self.sc, self.channel, self.user)
        category = sc.category if sc else 'Scene'
        dialog = {
            'create_scene': ''.join([
                '**CREATE or SCENE**```css\n',
                '.d scene YOUR_SCENE\'S_NAME```'
            ]),
            'active_scene': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n',
                f':point_down:\n\n{get_string}'
            ]),
            'active_scene_short': ''.join([
                f'***YOU ARE CURRENTLY EDITING...:***\n',
                f':point_down:\n\n{get_short_string}'
            ]),
            'rename_delete': ''.join([
                f'\n\n_Is ***{name}*** not the {category.lower()} name you wanted?_',
                f'```css\n.d scene rename NEW_NAME```_Want to remove ***{name}***?_',
                '```css\n.d scene delete```'
            ]),
            'go_back_to_parent': ''.join([
                f'\n\n***You can GO BACK to the parent scene, aspect, or stunt***',
                '```css\n.d scene parent```'
            ])
        }
        dialog_string = ''
        if dialog_text == 'all':
            if not sc:
                dialog_string += dialog.get('create_scene', '')
            dialog_string += dialog.get('rename_delete', '')
        elif sc.category == 'Scene':
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_scene', '')
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
        else:
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_scene', '') if self.can_edit else ''
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
                dialog_string += dialog.get('go_back_to_parent', '') if self.can_edit else ''
        return dialog_string
    
    def name(self, args):
        if not self.scenario:
            raise Exception('No active scenario or name provided. Try this:```css\n.d scenario SCENARIO_NAME```')
        messages = []
        if len(args) == 0:
            if not self.sc:
                return [
                    'No active scene or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.sc.get_string(self.channel, self.user))
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_scene_short')]
            if len(args) == 1 and self.sc:
                return [self.dialog('')]
            scene_name = ' '.join(args[1:])
            if len(args) > 1 and args[1] == 'rename':
                scene_name = ' '.join(args[2:])
                if not self.sc:
                    return [
                        'No active scene or name provided\n\n',
                        self.dialog('all')
                    ]
                else:
                    scene = Scene().find(self.user, scene_name, self.guild.name)
                    if scene:
                        return [f'Cannot rename to _{scene_name}_. Scene already exists']
                    else:
                        self.sc.name = scene_name
                        scene_svc.save(self.sc, self.user)
                        messages.append(self.dialog(''))
            else:
                def canceler(cancel_args):
                    if cancel_args[0].lower() in ['scene','s']:
                        return SceneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                    else:
                        self.parent.args = cancel_args
                        self.parent.command = self.parent.args[0]
                        return self.parent.get_messages()

                def selector(selection):
                    self.sc = selection
                    self.channel.set_active_scene(self.sc, self.user)
                    return [self.dialog('')]

                def creator(**params):
                    item = Scene().get_or_create(**params)
                    scenes = scenario_svc.get_scenes(self.scenario)
                    characters = scenario_svc.get_characters(scenes)
                    item.characters = [str(c.id) for c in characters]
                    scene_svc.save(item, self.user)
                    return item

                messages.extend(Dialog({
                    'svc': scene_svc,
                    'user': self.user,
                    'title': 'Scene List',
                    'command': 'scene ' + ' '.join(args),
                    'type': 'select',
                    'type_name': 'SCENE',
                    'getter': {
                        'method': Scene.get_by_page,
                        'params': {'params': {'name__icontains': scene_name, 'channel_id': str(self.channel.id), 'guild': self.guild.name, 'archived': False}}
                    },
                    'formatter': lambda item, item_num, page_num, page_size: f'_SCENE #{item_num+1}_\n{item.get_short_string()}',
                    'cancel': canceler,
                    'select': selector,
                    'empty': {
                        'method': creator,
                        'params': {'user': self.user, 'name': scene_name, 'scenario': self.scenario, 'channel': self.channel, 'guild': self.guild.name}
                    }
                }).open())
        return messages

    def select(self, args):
        messages = []
        if len(args) == 0:
            if not self.sc:
                return [
                    'No active scene or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.sc.get_string())
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_scene_short')]
            if len(args) == 1 and self.char:
                return [self.dialog('')]
            sc_name = ' '.join(args[1:])
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['scene','s']:
                    return SceneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

            def selector(selection):
                self.sc = selection
                self.channel.set_active_scene(self.sc, self.user)
                return [self.dialog('')]

            messages.extend(Dialog({
                'svc': scene_svc,
                'user': self.user,
                'title': 'Scene List',
                'command': 's ' + ' '.join(args),
                'type': 'select',
                'type_name': 'SCENE',
                'getter': {
                    'method': Scene.get_by_page,
                    'params': {'params': {'name__icontains': sc_name, 'scenario_id': str(self.scenario.id), 'guild': self.guild.name, 'archived': False}}
                },
                'formatter': lambda item, item_num, page_num, page_size: f'_SCENE #{item_num+1}_\n{item.get_short_string()}',
                'cancel': canceler,
                'select': selector
            }).open())
        return messages

    def scene_list(self, args):
        messages = []
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['scene']:
                return SceneCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        messages.extend(Dialog({
            'svc': scene_svc,
            'user': self.user,
            'title': 'Scene List',
            'command': 'scene ' + (' '.join(args)),
            'type': 'view',
            'getter': {
                'method': Scene().get_by_scenario,
                'params': {'scenario': self.scenario, 'archived': False}
            },
            'formatter': lambda item, item_num, page_num, page_size: f'{item.get_short_string(self.channel)}',
            'cancel': canceler
        }).open())
        return messages

    def description(self, args):
        if len(args) == 1:
            raise Exception('No description provided')
        if not self.sc:
            raise Exception('You don\'t have an active scene. Try this:```css\n.d scene SCENE_NAME```')
        else:
            description = ' '.join(args[1:])
            self.sc.description = description
            if (not self.sc.created):
                self.sc.created = datetime.datetime.utcnow()
            self.sc.updated_by = str(self.user.id)
            self.sc.updated = datetime.datetime.utcnow()
            self.sc.save()
            return [
                f'Description updated to "{description}"',
                self.sc.get_string(self.channel)
            ]

    def character(self, args):
        if self.user:
            self.user.active_character = str(self.sc.character.id)
            if (not self.user.created):
                self.user.created = datetime.datetime.utcnow()
            self.channel.updated_by = str(self.user.id)
            self.user.updated = datetime.datetime.utcnow()
            self.user.save()
        command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args, guild=self.guild, user=self.user, channel=self.channel, char=self.sc.character)
        return command.run()

    def player(self, args):
        return scene_svc.player(args, self.channel, self.sc, self.user)

    def delete_scene(self, args):
        return scene_svc.delete_scene(args, self.guild, self.channel, self.scenario, self.sc, self.user)