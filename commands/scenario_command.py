# scenario_command
import traceback
import datetime
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Character, User, Log
from config.setup import Setup
from services.character_service import CharacterService
from utils import Dialog

char_svc = CharacterService()
SETUP = Setup()
SCENARIO_HELP = SETUP.scenario_help

class ScenarioCommand():
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
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        try:
            switcher = {
                'help': self.help,
                'name': self.name,
                'n': self.name,
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
                'list': self.scenario_list,
                'l': self.scenario_list,
                'delete': self.delete_scenario,
                'd': self.delete_scenario
            }
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: self.name)
                # Execute the function
                messages = func(self.args)
            else:
                if self.scenario and self.char and str(self.char.id) == str(self.scenario.character.id):
                    self.args = ('c',) + self.args
                    self.command = 'c'
                    func = self.name
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
        return [SCENARIO_HELP]

    def note(self, args):
        Log().create_new(str(self.scenario.id), f'Scenario: {self.scenario.name}', str(self.user.id), self.guild.name, 'Log', {'by': self.user.name, 'note': ' '.join(args[1:])}, 'created')
        return ['Log created']

    def story(self, args):
        messages =[]
        command = 'log ' + (' '.join(args))
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
                'parent_method': Character.get_by_page,
                'params': {
                    'params': {'parent_id': str(self.scenario.id), 'category__in': ['Log','Scenario','Character']},
                    'sort': 'created'
                },
                'parent_method': Character.get_by_page,
                'parent_params': {
                    'params': {'category__in': ['Character','Aspect','Stunt']},
                    'sort': 'created'
                }
            },
            'formatter': lambda log, num: log.get_short_string() if log.category == 'Log' else log.get_string(),
            'cancel': canceler,
            'page_size': 10
        }).open()
        messages.extend(response)
        return messages
    
    def name(self, args):
        if len(args) == 0:
            if not self.scenario:
                return ['No active scenario or name provided']
            else:
                scenario_args = ['c']
                scenario_args.extend(args[1:])
                return self.character(scenario_args)
        else:
            scenario_name = ' '.join(args[1:])
            self.scenario = Scenario().get_or_create(self.user, self.guild.name, self.channel, scenario_name)
            self.channel.set_active_scenario(self.scenario, self.user)
            if self.user:
                self.user.active_character = str(self.scenario.character.id)
                if (not self.user.created):
                    self.user.created = datetime.datetime.utcnow()
                self.user.updated_by = str(self.user.id)
                self.user.updated = datetime.datetime.utcnow()
                self.user.save()
        return [self.scenario.get_string(self.channel)]

    def scenario_list(self, args):
        scenarios = Scenario().get_by_channel(self.channel)
        if len(scenarios) == 0:
            return ['You don\'t have any scenarios.\nTry this: ".d scenario name {name}"']
        else:
            scenarios_string = ''.join([s.get_string(self.channel) for s in scenarios])
            return [f'Scenarios:{scenarios_string}\n        ']

    def description(self, args):
        if len(args) == 1:
            return ['No description provided']
        if not self.scenario:
            return ['You don\'t have an active scenario.\nTry this: ".d s name {name}"']
        else:
            description = ' '.join(args[1:])
            self.scenario.description = description
            if (not self.scenario.created):
                self.scenario.created = datetime.datetime.utcnow()
            self.scenario.updated_by = str(self.user.id)
            self.scenario.updated = datetime.datetime.utcnow()
            self.scenario.save()
            return [
                f'Description updated to "{description}"',
                self.scenario.get_string(self.channel)
            ]

    def character(self, args):
        if self.user:
            self.user.active_character = str(self.scenario.character.id)
            if (not self.user.created):
                self.user.created = datetime.datetime.utcnow()
            self.user.updated_by = str(self.user.id)
            self.user.updated = datetime.datetime.utcnow()
            self.user.save()
        command = CharacterCommand(self.parent, self.ctx, args, self.scenario.character)
        return command.run()

    def player(self, args):
        if len(args) == 1:
            return ['No characters added']
        if not self.scenario:
            return ['You don\'t have an active scenario.\nTry this: ".d s name {name}"']
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [self.scenario.get_string_characters(self.channel)]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            char = ' '.join(args[2:])
            [self.scenario.characters.remove(s) for s in self.scenario.characters if char.lower() in s.lower()]
            if (not self.scenario.created):
                self.scenario.created = datetime.datetime.utcnow()
            self.scenario.updated_by = str(self.user.id)
            self.scenario.updated = datetime.datetime.utcnow()
            self.scenario.save()
            return [
                f'{char} removed from scenario characters',
                self.scenario.get_string_characters(self.channel)
            ]
        else:
            search = ' '.join(args[1:])
            char = Character().find(None, search, self.channel.guild)
            if char:
                self.scenario.characters.append(str(char.id))
            else:
                return [f'***{search}*** not found. No character added to _{self.scenario.name}_']
            if (not self.scenario.created):
                self.scenario.created = datetime.datetime.utcnow()
            self.scenario.updated_by = str(self.user.id)
            self.scenario.updated = datetime.datetime.utcnow()
            self.scenario.save()
            return [
                f'Added {char.name} to scenario characters',
                self.scenario.get_string_characters(self.channel)
            ]

    def delete_scenario(self, args):
        messages = []
        search = ''
        if len(args) == 1:
            if not self.scenario:
                return ['No scenario provided for deletion']
        else:
            search = ' '.join(args[1:])
            self.scenarioenario = Scenario().find(self.guild.name, str(self.channel.id), search)
        if not self.scenario:
            return [f'{search} was not found. No changes made.']
        else:
            search = str(self.scenario.name)
            channel_id = str(self.scenario.channel_id) if self.scenario.channel_id else ''
            self.scenario.character.archive(self.user)
            self.scenario.archived = True
            self.scenario.updated_by = str(self.user.id)
            self.scenario.updated = datetime.datetime.utcnow()
            self.scenario.save()
            messages.append(f'***{search}*** removed')
            if channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages