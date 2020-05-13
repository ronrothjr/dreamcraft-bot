# scene_command
import datetime
from commands import CharacterCommand
from models.channel import Channel
from models.scenario import Scenario
from models.scene import Scene
from models.character import Character
from models.user import User
from config.setup import Setup

SETUP = Setup()
SCENE_HELP = SETUP.scene_help

class SceneCommand():
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'n'
        self.guild = ctx.guild if ctx.guild else ctx.author
        self.channel = Channel().get_or_create(self.ctx.channel.name, self.guild.name)
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.user = User().get_or_create(ctx.author.name, self.guild.name)
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        switcher = {
            'help': self.help,
            'name': self.name,
            'n': self.name,
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
            self.args = ('n',) + self.args
            self.command = 'n'
            func = self.name
            # Execute the function
            messages = func(self.args)
        # Send messages
        return messages

    def help(self, args):
        return [SCENE_HELP]
    
    def name(self, args):
        if len(args) == 0:
            if not self.scenario:
                return ['No active scenario or name provided;\ntry this: ".d scenario name {name}"']
            if not self.sc:
                return ['No active scene or name provided']
            else:
                scene_args = ['c']
                scene_args.extend(args[1:])
                return self.character(scene_args)
        else:
            scene_name = ' '.join(args[1:])
            self.sc = Scene().get_or_create(self.user, self.channel, self.scenario, scene_name)
            self.channel.set_active_scene(self.sc)
            if self.user:
                self.user.active_character = str(self.sc.character.id)
                if (not self.user.created):
                    self.user.created = datetime.datetime.utcnow()
                self.user.updated = datetime.datetime.utcnow()
                self.user.save()
        return [self.sc.get_string(self.channel)]

    def scene_list(self, args):
        scenes = Scene().get_by_channel(self.channel)
        if len(scenes) == 0:
            return ['You don\'t have any scenes.\nTry this: ".d scene name {name}"']
        else:
            scenes_string = ''.join([s.get_string(self.channel) for s in scenes])
            return [f'Scenes:{scenes_string}\n        ']

    def description(self, args):
        if len(args) == 1:
            return ['No description provided']
        if not self.sc:
            return ['You don\'t have an active scene.\nTry this: ".d s name {name}"']
        else:
            description = ' '.join(args[1:])
            self.sc.description = description
            if (not self.sc.created):
                self.sc.created = datetime.datetime.utcnow()
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
            self.user.updated = datetime.datetime.utcnow()
            self.user.save()
        command = CharacterCommand(self.ctx, args, self.sc.character)
        return command.run()

    def player(self, args):
        if len(args) == 1:
            return ['No characters added']
        if not self.sc:
            return ['You don\'t have an active scene.\nTry this: ".d s name {name}"']
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [self.sc.get_string_characters(self.channel)]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            char = ' '.join(args[2:])
            [self.sc.characters.remove(s) for s in self.sc.characters if char.lower() in s.lower()]
            if (not self.sc.created):
                self.sc.created = datetime.datetime.utcnow()
            self.sc.updated = datetime.datetime.utcnow()
            self.sc.save()
            return [
                f'{char} removed from scene characters',
                self.sc.get_string_characters(self.channel)
            ]
        else:
            search = ' '.join(args[1:])
            char = Character().find(None, search, self.channel.guild)
            if char:
                self.sc.characters.append(str(char.id))
            else:
                return [f'***{search}*** not found. No character added to _{self.sc.name}_']
            if (not self.sc.created):
                self.sc.created = datetime.datetime.utcnow()
            self.sc.updated = datetime.datetime.utcnow()
            self.sc.save()
            return [
                f'Added {char.name} to scene characters',
                self.sc.get_string_characters(self.channel)
            ]

    def delete_scene(self, args):
        messages = []
        search = ''
        if len(args) == 1:
            if not self.sc:
                return ['No scene provided for deletion']
        else:
            search = ' '.join(args[1:])
            self.sc = Scene().find(str(self.channel.id), str(self.scenario.id), search)
        if not self.sc:
            return [f'{search} was not found. No changes made.']
        else:
            search = str(self.sc.name)
            scenario_id = str(self.sc.scenario_id) if self.sc.scenario_id else ''
            channel_id = str(self.sc.channel_id) if self.sc.channel_id else ''
            self.sc.character.reverse_delete()
            self.sc.character.delete()
            self.sc.delete()
            messages.append(f'***{search}*** removed')
            if scenario_id:
                secenario = Scenario().get_by_id(scenario_id)
                messages.append(secenario.get_string(self.channel))
            elif channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages