# scene_command
import traceback
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Engagement, Character, User, Log
from config.setup import Setup
from services import SceneService, ZoneService, ScenarioService
from utils import Dialog, T

scene_svc = SceneService()
zone_svc = ZoneService()
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
        self.zone = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
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
                'select': self.select,
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
                'd': self.delete_scene,
                'start': self.start,
                'end': self.end,
                'enter': self.enter,
                'move': self.move,
                'exit': self.exit
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

    def check_scene(self):
        if not self.sc:
            raise Exception('You don\'t have an active scene. Try this:```css\n.d scene SCENE_NAME```')

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
            'formatter': lambda log, num, page_num, page_size: log.get_string(self.user), # if log.category == 'Log' else log.get_string()
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
                '***YOU ARE CURRENTLY EDITING...***\n' if self.can_edit else '',
                f':point_down:\n\n{get_string}'
            ]),
            'active_scene_short': ''.join([
                '***YOU ARE CURRENTLY EDITING...:***\n' if self.can_edit else '',
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
        self.check_scene()
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
                    scene = Scene().find(self.guild.name, str(self.channel.id), str(self.scenario.id), scene_name)
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
                        'params': {'params': {'name__icontains': scene_name, 'scenario_id': str(self.scenario.id), 'guild': self.guild.name, 'archived': False}}
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
        self.check_scene()
        description = ' '.join(args[1:])
        self.sc.description = description
        self.sc.updated_by = str(self.user.id)
        self.sc.updated = T.now()
        self.sc.save()
        return [
            f'Description updated to "{description}"',
            self.sc.get_string(self.channel)
        ]

    def character(self, args):
        self.check_scene()
        if self.user:
            self.user.active_character = str(self.sc.character.id)
            self.channel.updated_by = str(self.user.id)
            self.user.updated = T.now()
            self.user.save()
        command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args, guild=self.guild, user=self.user, channel=self.channel, char=self.sc.character)
        return command.run()

    def player(self, args):
        return scene_svc.player(args, self.channel, self.sc, self.user)

    def delete_scene(self, args):
        return scene_svc.delete_scene(args, self.guild, self.channel, self.scenario, self.sc, self.user)

    def start(self, args):
        self.check_scene()
        if self.sc.started_on:
            raise Exception(f'***{self.sc.name}*** already began on {T.to(self.sc.started_on, self.user)}')
        else:
            self.sc.started_on = T.now()
            scene_svc.save(self.sc, self.user)
            return [self.dialog('')]

    def end(self, args):
        self.check_scene()
        if len(args) > 1 and args[1] == 'delete':
            self.sc.ended_on = None
            scene_svc.save(self.sc, self.user)
            return [self.dialog('')]
        else:
            if not self.sc.started_on:
                raise Exception(f'***{self.sc.name}*** has not yet started.')
            if self.sc.ended_on:
                raise Exception(f'***{self.sc.name}*** already ended on {T.to(self.sc.ended_on, self.user)}')
            else:
                self.sc.ended_on = T.now()
                scene_svc.save(self.sc, self.user)
                return [self.dialog('')]

    def enter(self, args):
        self.check_scene()
        if not self.char:
            raise Exception(f'You have no active character.```css\n.d c CHARACTER_NAME```')      
        if not self.sc.started_on:
            raise Exception(f'***{self.sc.name}*** has not yet started. You may not enter.')
        if self.sc.ended_on:
            raise Exception(f'***{self.sc.name}*** has already ended. You missed it.')
        messages = self.player(('p', self.char.name))
        self.note(('note', f'***{self.char.name}*** enters the _({self.sc.name})_ scene'))
        return messages

    def move(self, args):
        messages = []
        self.check_scene()
        if not self.char or  (self.char and self.char.category != 'Character'):
            raise Exception(f'You have no active character.```css\n.d c CHARACTER_NAME```')    
        if len(args) == 1:
            raise Exception('No zone name provided.')
        zones = list(Zone.filter(scene_id=str(self.sc.id), archived=False))
        if not zones:
            raise Exception('There are no zones to move into.')
        if args[1] == 'to':
            zone_name = ' '.join(args[2:])
        else:
            zone_name = ' '.join(args[1:])
        zone = [z for z in zones if zone_name.lower() in z.character.name.lower()]
        if not zone:
            raise Exception(f'***{zone_name}*** not found in ***{self.sc.name}***')
        if len(zone) > 1:
            zones_string = '\n'.join([f'.d s move {z.name}' for z in zones])
            raise Exception(f'Which zone do you want?***```css\n{zones_string}```')
        if str(self.char.id) in zone[0].characters:
            raise Exception(f'***{self.char.name}*** is already in _{zone[0].name}_.')
        leaving = [z for z in zones if str(self.char.id) in z.characters]
        for l in leaving:
            messages.extend(zone_svc.player(('p', 'delete', self.char.name), self.channel, l, self.user))
            self.note(('note', f'***{self.char.name}*** exits the _{l.name}_ zone')
        )
        messages.extend(zone_svc.player(('p', self.char.name), self.channel, zone[0], self.user))
        self.note(('note', f'***{self.char.name}*** enters the _{zone[0].name}_ zone')
    )
        return messages

    def exit(self, args):
        self.check_scene()
        if not self.char and not self.char.category == 'Character':
            raise Exception(f'You have no active character.```css\n.d c CHARACTER_NAME```')      
        if not self.sc.started_on:
            raise Exception(f'***{self.sc.name}*** has not yet started. You may not enter.')
        if self.sc.ended_on:
            raise Exception(f'***{self.sc.name}*** has already ended. You missed it.')
        messages = self.player(('p', 'delete', self.char.name))
        self.note(('note', f'***{self.char.name}*** exits the _{self.sc.name}_ scene'))
        return messages
        