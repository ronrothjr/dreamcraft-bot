# scene_service

from models.channel import Channel
from models.scene import Scene
from models.character import Character
from models.user import User

class SceneService():
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
            'name': self.name,
            'n': self.name,
            'description': self.description,
            'desc': self.description,
            'aspect': self.aspect,
            'a': self.aspect,
            'character': self.character,
            'char': self.character,
            'c': self.character,
            'list': self.scene_list,
            'l': self.scene_list,
            'delete': self.delete_scene,
            'd': self.delete_scene
        }
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: self.name)
            # Execute the function
            messages = func()
        else:
            messages = [f'Unknown command: {self.command}']
        # Send messages
        return messages
    
    def name(self):
        if len(self.args) == 0:
            if not self.sc:
                return ['No active scene or name provided']
        else:
            scene_name = ' '.join(self.args[1:])
            self.sc = Scene().get_or_create(self.channel, scene_name)
            self.channel.set_active_scene(self.sc)
            if self.sc.name not in self.channel.scenes:
                self.channel.scenes.append(self.sc.name)
                self.channel.save()
        return ['Scene:' + self.sc.get_string(self.channel)]

    def scene_list(self):
        scenes = Scene().get_by_channel(self.channel)
        if len(scenes) == 0:
            return ['You don\'t have any scenes.\nTry this: ".d scene name {name}"']
        else:
            scenes_string = ''.join([s.get_string(self.channel) for s in scenes])
            return [f'___________________\nScenes:{scenes_string}']

    def description(self):
        if len(self.args) == 1:
            return ['No description provided']
        if not self.sc:
            return ['You don\'t have an active scene.\nTry this: ".d s name {name}"']
        else:
            description = ' '.join(self.args[1:])
            self.sc.description = description
            self.sc.save()
            return [
                f'Description updated to {description}',
                self.sc.get_string(self.channel)
            ]

    def aspect(self):
        if len(self.args) == 1:
            return ['No aspect provided']
        if not self.sc:
            return ['You don\'t have an active scene.\nTry this: ".d s name {name}"']
        elif self.args[1].lower() == 'list':
            return [self.sc.get_string_aspects()]
        elif self.args[1].lower() == 'delete' or self.args[1].lower() == 'd':
            aspect = ' '.join(self.args[2:])
            [self.sc.aspects.remove(s) for s in self.sc.aspects if aspect.lower() in s.lower()]
            self.sc.save()
            return [
                f'{aspect} removed from scene aspects',
                self.sc.get_string_aspects()
            ]
        else:
            aspect = ' '.join(self.args[1:])
            self.sc.aspects.append(aspect)
            self.sc.save()
            return [
                f'Added {aspect} to scene aspects',
                self.sc.get_string_aspects()
            ]

    def character(self):
        if len(self.args) == 1:
            return ['No character provided']
        if not self.sc:
            return ['You don\'t have an active scene.\nTry this: ".d s name {name}"']
        elif self.args[1].lower() == 'list' or self.args[1].lower() == 'l':
            return [self.sc.get_string_characters()]
        elif self.args[1].lower() == 'delete' or self.args[1].lower() == 'd':
            char = ' '.join(self.args[2:])
            [self.sc.characters.remove(s) for s in self.sc.characters if char.lower() in s.lower()]
            self.sc.save()
            return [
                f'{char} removed from scene characters',
                self.sc.get_string_characters()
            ]
        else:
            search = ' '.join(self.args[1:])
            char = Character().find(self.user, search, self.channel.guild)
            self.sc.characters.append(char.name)
            self.sc.save()
            return [
                f'Added {char.name} to scene characters',
                self.sc.get_string_characters()
            ]

    def delete_scene(self):
        if len(self.args) == 1:
            return ['No scene provided for deletion']
        search = ' '.join(self.args[1:])
        self.sc = Scene().find(self.channel, search)
        if not self.sc:
            return [f'{search} was not found. No changes made.']
        else:
            self.sc.delete()
            return [f'{search} removed']