# session_command
import traceback
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Session, Character, User, Log
from config.setup import Setup
from services import SessionService
from utils import Dialog, T

session_svc = SessionService()
SETUP = Setup()
SESSION_HELP = SETUP.session_help

class SessionCommand():
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
        self.session = Session().get_by_id(self.channel.active_session) if self.channel and self.channel.active_session else None
        self.can_edit = self.user.role == 'Game Master' if self.user and self.session else True
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
                'list': self.session_list,
                'l': self.session_list,
                'delete': self.delete_session,
                'd': self.delete_session,
                'start': self.start,
                'end': self.end
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
        return [SESSION_HELP]

    def check_session(self):
        if not self.session:
            raise Exception('You don\'t have an active session. Try this:```css\n.d session SESSION_NAME```')

    def search(self, args):
        params = {'name__icontains': ' '.join(args[0:]), 'guild': self.guild.name, 'channel_id': str(self.channel.id), 'archived': False}
        return session_svc.search(args, Session.filter, params)

    def note(self, args):
        if self.session:
            Log().create_new(str(self.session.id), f'Session: {self.session.name}', str(self.user.id), self.guild.name, 'Session', {'by': self.user.name, 'note': ' '.join(args[1:])}, 'created')
            return ['Log created']
        else:
            return ['No active session to log']

    def say(self, args):
        if not self.session:
            return ['No active session to log']
        else:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.session.id), f'Session: {self.session.name}', str(self.user.id), self.guild.name, 'Session', {'by': self.user.name, 'note': f'***Narrator*** says, "{note_text}"'}, 'created')
            return ['Log created']

    def story(self, args):
        messages =[]
        command = 'session ' + (' '.join(args))
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['session']:
                self.args = cancel_args
                self.command = self.args[0]
                return self.run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()
        response = Dialog({
            'svc': session_svc,
            'user': self.user,
            'title': 'Story',
            'type': 'view',
            'type_name': 'Story Log',
            'command': command,
            'getter': {
                'method': Log.get_by_page,
                'params': {
                    'params': {'parent_id': str(self.session.id)},
                    'sort': 'created'
                },
                'parent_method': Session.get_by_page,
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

    def dialog(self, dialog_text, session=None):
        session, name, get_string, get_short_string = session_svc.get_session_info(self.session, self.channel, self.user)
        category = session.category if session else 'Session'
        dialog = {
            'create_session': ''.join([
                '**CREATE or SESSION**```css\n',
                '.d session YOUR_SESSION\'S_NAME```'
            ]),
            'active_session': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n' if self.can_edit else '',
                f':point_down:\n\n{get_string}'
            ]),
            'active_session_short': ''.join([
                '***YOU ARE CURRENTLY EDITING...:***\n' if self.can_edit else '',
                f':point_down:\n\n{get_short_string}'
            ]),
            'rename_delete': ''.join([
                f'\n\n_Is ***{name}*** not the {category.lower()} name you wanted?_',
                f'```css\n.d session rename NEW_NAME```_Want to remove ***{name}***?_',
                '```css\n.d session delete```'
            ]),
            'go_back_to_parent': ''.join([
                f'\n\n***You can GO BACK to the parent session, aspect, or stunt***',
                '```css\n.d session parent```'
            ])
        }
        dialog_string = ''
        if dialog_text == 'all':
            if not session:
                dialog_string += dialog.get('create_session', '')
            dialog_string += dialog.get('rename_delete', '')
        elif session.category == 'Session':
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_session', '')
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
        else:
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_session', '') if self.can_edit else ''
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
                dialog_string += dialog.get('go_back_to_parent', '') if self.can_edit else ''
        return dialog_string
    
    def name(self, args):
        self.check_session()
        messages = []
        if len(args) == 0:
            if not self.session:
                return [
                    'No active session or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.session.get_string(self.channel, self.user))
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_session_short')]
            if len(args) == 1 and self.session:
                return [self.dialog('')]
            session_name = ' '.join(args[1:])
            if len(args) > 1 and args[1] == 'rename':
                session_name = ' '.join(args[2:])
                if not self.session:
                    return [
                        'No active session or name provided\n\n',
                        self.dialog('all')
                    ]
                else:
                    session = Session().find(self.guild.name, str(self.channel.id), session_name)
                    if session:
                        return [f'Cannot rename to _{session_name}_. Session already exists']
                    else:
                        self.session.name = session_name
                        session_svc.save(self.session, self.user)
                        messages.append(self.dialog(''))
            else:
                def canceler(cancel_args):
                    if cancel_args[0].lower() in ['session','s']:
                        return SessionCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                    else:
                        self.parent.args = cancel_args
                        self.parent.command = self.parent.args[0]
                        return self.parent.get_messages()

                def selector(selection):
                    self.session = selection
                    self.channel.set_active_session(self.session, self.user)
                    return [self.dialog('')]

                def creator(**params):
                    item = Session().get_or_create(**params)
                    sessions = sessionenario_svc.get_sessions(self.sessionenario)
                    characters = sessionenario_svc.get_characters(sessions)
                    item.characters = [str(c.id) for c in characters]
                    session_svc.save(item, self.user)
                    return item

                messages.extend(Dialog({
                    'svc': session_svc,
                    'user': self.user,
                    'title': 'Session List',
                    'command': 'session ' + ' '.join(args),
                    'type': 'select',
                    'type_name': 'SESSION',
                    'getter': {
                        'method': Session.get_by_page,
                        'params': {'params': {'name__icontains': session_name, 'channel_id': str(self.channel.id), 'guild': self.guild.name, 'archived': False}}
                    },
                    'formatter': lambda item, item_num, page_num, page_size: f'_SESSION #{item_num+1}_\n{item.get_short_string()}',
                    'cancel': canceler,
                    'select': selector,
                    'empty': {
                        'method': creator,
                        'params': {'user': self.user, 'name': session_name, 'channel': self.channel, 'guild': self.guild.name}
                    }
                }).open())
        return messages

    def select(self, args):
        messages = []
        if len(args) == 0:
            if not self.session:
                return [
                    'No active session or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.session.get_string())
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_session_short')]
            if len(args) == 1 and self.char:
                return [self.dialog('')]
            session_name = ' '.join(args[1:])
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['session']:
                    return SessionCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

            def selector(selection):
                self.session = selection
                self.channel.set_active_session(self.session, self.user)
                return [self.dialog('')]

            messages.extend(Dialog({
                'svc': session_svc,
                'user': self.user,
                'title': 'Session List',
                'command': 's ' + ' '.join(args),
                'type': 'select',
                'type_name': 'SESSION',
                'getter': {
                    'method': Session.get_by_page,
                    'params': {'params': {'name__icontains': session_name, 'channel_id': str(self.channel.id), 'guild': self.guild.name, 'archived': False}}
                },
                'formatter': lambda item, item_num, page_num, page_size: f'_SESSION #{item_num+1}_\n{item.get_short_string()}',
                'cancel': canceler,
                'select': selector
            }).open())
        return messages

    def session_list(self, args):
        messages = []
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['session']:
                return SessionCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        messages.extend(Dialog({
            'svc': session_svc,
            'user': self.user,
            'title': 'Session List',
            'command': 'session ' + (' '.join(args)),
            'type': 'view',
            'getter': {
                'method': Session().get_by_channel,
                'params': {'channel': self.channel, 'archived': False}
            },
            'formatter': lambda item, item_num, page_num, page_size: f'{item.get_short_string(self.channel)}',
            'cancel': canceler
        }).open())
        return messages

    def description(self, args):
        if len(args) == 1:
            raise Exception('No description provided')
        self.check_session()
        description = ' '.join(args[1:])
        self.sc.description = description
        self.sc.updated_by = str(self.user.id)
        self.sc.updated = T.now()
        self.sc.save()
        return [
            f'Description updated to "{description}"',
            self.session.get_string(self.channel)
        ]

    def character(self, args):
        self.check_session()
        if self.user:
            self.user.active_character = str(self.session.character.id)
            self.channel.updated_by = str(self.user.id)
            self.user.updated = T.now()
            self.user.save()
        command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args, guild=self.guild, user=self.user, channel=self.channel, char=self.session.character)
        return command.run()

    def player(self, args):
        return session_svc.player(args, self.channel, self.session, self.user)

    def delete_session(self, args):
        return session_svc.delete_session(args, self.guild, self.channel, self.session, self.user)

    def start(self, args):
        self.check_session()
        if self.session.started_on:
            raise Exception(f'***{self.session.name}*** already began on {T.to(self.session.started_on, self.user)}')
        else:
            self.session.started_on = T.now()
            session_svc.save(self.session, self.user)
            return [self.dialog('')]

    def end(self, args):
        self.check_session()
        if len(args) > 1 and args[1] == 'delete':
            self.session.ended_on = None
            session_svc.save(self.session, self.user)
            return [self.dialog('')]
        else:
            if not self.session.started_on:
                raise Exception(f'***{self.session.name}*** has not yet started.')
            if self.session.ended_on:
                raise Exception(f'***{self.session.name}*** already ended on {T.to(self.session.ended_on, self.user)}')
            else:
                self.session.ended_on = T.now()
                session_svc.save(self.session, self.user)
                return [self.dialog('')]
        
