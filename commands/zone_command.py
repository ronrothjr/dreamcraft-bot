# zone_command
import datetime
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Character, User
from config.setup import Setup
from services.character_service import CharacterService

char_svc = CharacterService()
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
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
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

    def help(self, args):
        return [ZONE_HELP]
    
    def name(self, args):
        if len(args) == 0:
            if not self.sc:
                return ['No active scene or name provided;\ntry this: ".d scene name {name}"']
            if not self.zone:
                return ['No active zone or name provided']
            else:
                zone_args = ['c']
                zone_args.extend(args[1:])
                return self.character(zone_args)
        else:
            zone_name = ' '.join(args[1:])
            self.zone = Zone().get_or_create(self.user, self.guild.name, self.channel, self.sc, zone_name)
            self.channel.set_active_zone(self.zone, self.user)
            if self.user:
                self.user.active_character = str(self.zone.character.id)
                if (not self.user.created):
                    self.user.created = datetime.datetime.utcnow()
                self.user.updated_by = str(self.user.id)
                self.user.updated = datetime.datetime.utcnow()
                self.user.save()
        return [self.zone.get_string(self.channel)]

    def zone_list(self, args):
        zones = Zone().get_by_channel(self.channel)
        if len(zones) == 0:
            return ['You don\'t have any zones.\nTry this: ".d zone name {name}"']
        else:
            zones_string = ''.join([s.get_string(self.channel) for s in zones])
            return [f'Zones:{zones_string}\n        ']

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
            scene_id = str(self.zone.scene_id) if self.zone.scene_id else ''
            channel_id = str(self.zone.channel_id) if self.zone.channel_id else ''
            self.zone.character.reverse_archive(self.user)
            self.zone.character.archived = True
            char_svc.save(self.zone.character, self.user)
            self.zone.archived = True
            self.zone.updated_by = str(self.user.id)
            self.zone.updated = datetime.datetime.utcnow()
            self.zone.save()
            messages.append(f'***{search}*** removed')
            if scene_id:
                secenario = Scene().get_by_id(scene_id)
                messages.append(secenario.get_string(self.channel))
            elif channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages