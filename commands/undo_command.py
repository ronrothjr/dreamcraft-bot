# undo_command
import datetime
import math
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Character, User, Log
from utils import Dialog, TextUtils
from config.setup import Setup
from services.character_service import CharacterService

char_svc = CharacterService()
SETUP = Setup()
UNDO_HELP = SETUP.undo_help

class UndoCommand():
    def __init__(self, parent, ctx, args):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'undo'
        self.guild = ctx.guild if ctx.guild else ctx.author
        self.user = User().get_or_create(ctx.author.name, self.guild.name)
        channel = 'private' if ctx.channel.type.name == 'private' else ctx.channel.name
        self.channel = Channel().get_or_create(channel, self.guild.name, self.user)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        switcher = {
            'help': self.help,
            'list': self.undo_list,
            'last': self.last,
            'next': self.next
        }
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: self.name)
            # Execute the function
            messages = func(self.args)
        else:
            self.args = ('help',) + self.args
            self.command = 'help'
            func = self.help
            # Execute the function
            messages = func(self.args)
        # Send messages
        return messages

    def help(self, args):
        return [UNDO_HELP]

    def set_dialog(self, command='', question='', answer=''):
        self.user.command = command
        self.user.question = question
        self.user.answer = answer
        char_svc.save_user(self.user)

    def undo_list(self, args):
        messages =[]
        command = 'undo ' + (' '.join(args))
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['redo','undo']:
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
            'title': 'Undo List',
            'type': 'view',
            'type_name': 'Undo History',
            'command': command,
            'user': self.user,
            'getter': {
                'method': Log.get_by_page,
                'params': {
                    'params': {'user_id': str(self.user.id)}
                }
            },
            'formatter': lambda undo, num: f'_Undo #{num+1}_\n{undo.get_string()}',
            'cancel': canceler
        }).open()
        messages.extend(response)
        return messages

    def get_undo(self, undo):
        switcher = {
            'Character': Character,
            'Stunt': Character,
            'Aspect': Character,
            'Channel': Channel,
            'Scenario': Scenario,
            'Scene': Scene,
            'Zone': Zone
        }
        model = switcher.get(undo.category, None)
        if not model:
            raise Exception(f'Could not find data module for {undo.category}')
        exclude = ['created', 'updated', 'created_by', 'updated_by']
        changes = {d: undo.data[d] for d in undo.data if d not in exclude or undo.action == 'created'}
        undo_changes_str = [f'_{c}:_ {changes[c]}' for c in changes]
        item = model().get_by_id(undo.parent_id)
        if not item:
            item = model()
        return changes, item, undo_changes_str

    def last(self, args):
        messages = []
        undos = None
        if self.user.history_id:
            current_history = Log.get_by_id(self.user.history_id)
            if current_history:
                undos = list(Log.filter(updated__lt=current_history.updated).order_by('-created').all())
        if not undos:
            undos = list(Log.get_by_page({'user_id': str(self.user.id)}))
        if not undos:
            raise Exception('You have no undo history')
        undo = undos[0]
        changes, item, undo_changes_str = self.get_undo(undo)
        command = 'undo ' + ' '.join(args)
        question = ''.join([
            f'Are you sure you want to undo changes to this {undo.category}?\n\n{item.get_string()}\n\n',
            f'***Changes to Undo:***\n' + '\n'.join(undo_changes_str),
            '```css\n.d YES /* to confirm the command */\n.d NO /* to reject the command */\n.d CANCEL /* to cancel the command */```'
        ])
        if self.user.command == command:
            answer = self.user.answer
            if answer:
                if answer.lower() in ['yes', 'y']:
                    messages.append(self.undo_changes(undo))
                elif answer.lower() in ['no', 'n', 'cancel', 'c']:
                    messages.append(f'Command ***"{command}"*** canceled')
                else:
                    raise Exception(f'Please answer the question regarding ***"{command}"***:\n\n{question}')
                self.set_dialog()
            else:
                Exception(f'No answer was received to command ***"{command}"***')
        else:
            self.set_dialog(command, question)
            messages.extend([question])
        return messages

    def undo_changes(self, undo):
        changes, item, undo_changes_str = self.get_undo(undo)
        undos = list(Log.get_by_page(params={'parent_id': undo.parent_id, 'updated__lt': undo.updated}, page_num=0))
        if undo.action == 'created':
            history = Log.get_by_page(params={'updated__lt': undo.updated}, page_num=0).first()
            item.history_id = str(history.id)
            item.updated_by = str(self.user.id)
            item.save()
            response = f'{undo.category} {TextUtils.clean(item.name)} has been archived:\n\n{item.get_string()}'
            item.archive(self.user)
            return response
        elif changes and undos:
            for c in changes:
                prop = c.split ('__')
                match = next(filter(lambda u: c in u.data, undos), None)
                if match and str(match.id) != str(undo.id):
                    if len(prop) > 1:
                        # Get dictionary
                        attr = getattr(item, prop[0])
                        # Set key value in dictionary
                        attr[prop[1]] = match.data[c]
                        setattr(item, prop[0], attr)
                    else:
                        setattr(item, c, match.data[c])
                else:
                    if len(prop) > 1:
                        # Get dictionary
                        attr = getattr(item, prop[0])
                        # Remove prop from dictionary
                        attr = {k: attr[k] for k in attr if k != prop[1]}
                        setattr(item, prop[0], attr)
                    else:
                        setattr(item, c, None)
            item.history_id = str(undos[0].id)
            item.updated_by = str(self.user.id)
            item.save()
            return f'{undo.category} {TextUtils.clean(item.name)} has been undone:\n\n{item.get_string()}'

    def next(self, args):
        messages = []
        redo = None
        if not self.user.history_id:
            raise Exception('You cannot redo the next undo history. You are up to date.')
        current_history = Log.get_by_id(self.user.history_id)
        if current_history:
            redo = Log.filter(updated__gt=current_history.updated).order_by('created').first()
        if not redo:
            raise Exception('Cannot find next undo history')
        changes, item, undo_changes_str = self.get_undo(redo)
        command = 'redo ' + ' '.join(args)
        item_string = f'***New {redo.category}***' if redo.action == 'created' else item.get_string()
        question = ''.join([
            f'Are you sure you want to redo changes to this {redo.category}?\n\n{item_string}\n\n',
            f'***Changes to Redo:***\n' + '\n'.join(undo_changes_str),
            '```css\n.d YES /* to confirm the command */\n.d NO /* to reject the command */\n.d CANCEL /* to cancel the command */```'
        ])
        if self.user.command == command:
            answer = self.user.answer
            if answer:
                if answer.lower() in ['yes', 'y']:
                    messages.append(self.redo_changes(redo))
                elif answer.lower() in ['no', 'n', 'cancel', 'c']:
                    messages.append(f'Command ***"{command}"*** canceled')
                else:
                    raise Exception(f'Please answer the question regarding ***"{command}"***:\n\n{question}')
                self.set_dialog()
                char_svc.save_user(self.user)
            else:
                Exception(f'No answer was received to command ***"{command}"***')
        else:
            self.set_dialog(command, question)
            messages.extend([question])
        return messages

    def redo_changes(self, redo):
        changes, item, undo_changes_str = self.get_undo(redo)
        history = Log.get_by_page(params={'updated__lt': redo.updated}, page_num=0).first()
        item.history_id = str(history.id)
        item.updated_by = str(self.user.id)
        if redo.action == 'created':
            item.save()
            response = f'{redo.category} {TextUtils.clean(item.name)} has been deleted:\n\n{item.get_string()}'
            item.archive(self.user)
            return response
        elif changes and item:
            for c in changes:
                if '__' in c:
                    nest = c.split ('__')
                    attr = getattr(item, nest[0])
                    attr[nest[1]] = changes[c]
                    setattr(item, nest[0], attr)
                else:
                    setattr(item, c, changes[c])
            item.save()
            action = 'restored' if redo.action == 'created' else 'updated'
            return f'{redo.category} {TextUtils.clean(item.name)} has been {action}:\n\n{item.get_string()}'
