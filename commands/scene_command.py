# scene_command
import datetime
from commands import CharacterCommand
from models.channel import Channel
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
        self.channel = Channel().get_or_create(self.ctx.channel.name, self.ctx.guild.name)
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.user = User().get_or_create(ctx.author.name, ctx.guild.name)
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
            'members': self.member,
            'member': self.member,
            'm': self.member,
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

    def help(self):
        return [SCENE_HELP]
    
    def name(self, args):
        if len(args) == 0:
            if not self.sc:
                return ['No active scene or name provided']
            else:
                scene_args = ['c']
                scene_args.extend(args[1:])
                return self.character(scene_args)
        else:
            scene_name = ' '.join(args[1:])
            self.sc = Scene().get_or_create(self.user, self.channel, scene_name)
            self.channel.set_active_scene(self.sc)
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
        command = CharacterCommand(self.ctx, args, self.sc.character)
        return command.run()

    def member(self, args):
        if len(args) == 1:
            return ['No characters added']
        if not self.sc:
            return ['You don\'t have an active scene.\nTry this: ".d s name {name}"']
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [self.sc.get_string_characters()]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            char = ' '.join(args[2:])
            [self.sc.characters.remove(s) for s in self.sc.characters if char.lower() in s.lower()]
            if (not self.sc.created):
                self.sc.created = datetime.datetime.utcnow()
            self.sc.updated = datetime.datetime.utcnow()
            self.sc.save()
            return [
                f'{char} removed from scene characters',
                self.sc.get_string_characters()
            ]
        else:
            search = ' '.join(args[1:])
            char = Character().find(self.user, search, self.channel.guild)
            self.sc.characters.append(char.name)
            if (not self.sc.created):
                self.sc.created = datetime.datetime.utcnow()
            self.sc.updated = datetime.datetime.utcnow()
            self.sc.save()
            return [
                f'Added {char.name} to scene characters',
                self.sc.get_string_characters()
            ]

    def delete_scene(self, args):
        if len(args) == 1:
            return ['No scene provided for deletion']
        search = ' '.join(args[1:])
        self.sc = Scene().find(self.channel, search)
        if not self.sc:
            return [f'{search} was not found. No changes made.']
        else:
            self.sc.delete()
            return [f'{search} removed']