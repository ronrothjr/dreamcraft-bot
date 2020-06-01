# engagement_command
import traceback
from commands import CharacterCommand
from models import Channel, Scenario, Scene, Zone, Engagement, Character, User, Log
from config.setup import Setup
from services import ScenarioService, EngagementService
from utils import Dialog, T

scenario_svc = ScenarioService()
engagement_svc = EngagementService()
SETUP = Setup()
ENGAGEMENT_HELP = SETUP.engagement_help

class EngagementCommand():
    """
    Handle 'engagement', 'engage', 'e' commands and subcommands

    Subcommands:
        help - display a set of instructions on CharacterCommand usage
        note - add a note to the character
        say - add dialog to the scene from the character
        story - display the character's story
        parent, p - return viewing and editing focus to the character's parent component
        name, n - display and create new engagements by name
        description, desc - add/edit the Description in the engeagement
        select - display existing engeagement
        character, char, c - edit the engagement as a character
        list, l - display a list of existing engagements
        players, player, p - add players to the engagement
        opposition, opp, o - add opposition to the engagement
        start - add a start time to the engagement
        end - add an end time to the engagement
        delete - remove an engagement (archive)
    """
    def __init__(self, parent, ctx, args, guild, user, channel):
        """
        Command handler for EngagementCommand

        Parameters
        ----------
        parent : DreamcraftHandler
            The handler for Dreamcraft Bot commands and subcommands
        ctx : object(Context)
            The Discord.Context object used to retrieve and send information to Discord users
        args : array(str)
            The arguments sent to the bot to parse and evaluate
        guild : Guild
            The guild object containing information about the server issuing commands
        user : User
            The user database object containing information about the user's current setttings, and dialogs
        channel : Channel
            The channel from which commands were issued

        Returns
        -------
        EngagementCommand - object for processing engagement commands and subcommands
        """

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
        self.engagement = Engagement().get_by_id(self.channel.active_engagement) if self.channel and self.channel.active_engagement else None
        self.can_edit = self.user.role == 'Game Master' if self.user and self.engagement else True
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        try:
            switcher = {
                'help': self.help,
                'name': self.name,
                'n': self.name,
                'select': self.select,
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
                'opposition': self.oppose,
                'oppose': self.oppose,
                'o': self.oppose,
                'list': self.engagement_list,
                'l': self.engagement_list,
                'delete': self.delete_engagement,
                'd': self.delete_engagement,
                'start': self.start,
                'end': self.end
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
        return [ENGAGEMENT_HELP]

    def check_engagement(self):
        if not self.sc:
            raise Exception('You don\'t have an active engagement. Try this:```css\n.d engagement ENGAGEMENT_NAME```')

    def search(self, args):
        params = {'name__icontains': ' '.join(args[0:]), 'guild': self.guild.name, 'channel_id': str(self.channel.id), 'archived': False}
        return engagement_svc.search(args, Engagement.filter, params)

    def note(self, args):
        if self.engagement:
            Log().create_new(str(self.engagement.id), f'Engagement: {self.engagement.name}', str(self.user.id), self.guild.name, 'Engagement', {'by': self.user.name, 'note': ' '.join(args[1:])}, 'created')
            return ['Log created']
        else:
            return ['No active engagement to log']

    def say(self, args):
        if not self.engagement:
            return ['No active engagement to log']
        else:
            note_text = ' '.join(args[1:])
            Log().create_new(str(self.engagement.id), f'Engagement: {self.engagement.name}', str(self.user.id), self.guild.name, 'Engagement', {'by': self.user.name, 'note': f'***Narrator*** says, "{note_text}"'}, 'created')
            return ['Log created']

    def story(self, args):
        messages =[]
        command = 'engagement ' + (' '.join(args))
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['engagement','engage','e']:
                self.args = cancel_args
                self.command = self.args[0]
                return self.run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()
        response = Dialog({
            'svc': engagement_svc,
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
                'parent_method': Engagement.get_by_page,
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

    def dialog(self, dialog_text, engagement=None):
        engagement, name, get_string, get_short_string = engagement_svc.get_engagement_info(engagement if engagement else self.engagement, self.channel, self.user)
        category = engagement.category if engagement else 'Engagement'
        dialog = {
            'create_engagement': ''.join([
                '**CREATE or ENGAGEMENT**```css\n',
                '.d engagement YOUR_ENGAGEMENT\'S_NAME```'
            ]),
            'active_engagement': ''.join([
                '***YOU ARE CURRENTLY EDITING...***\n' if self.can_edit else '',
                f':point_down:\n\n{get_string}'
            ]),
            'active_engagement_short': ''.join([
                '***YOU ARE CURRENTLY EDITING...:***\n' if self.can_edit else '',
                f':point_down:\n\n{get_short_string}'
            ]),
            'rename_delete': ''.join([
                f'\n\n_Is ***{name}*** not the {category.lower()} name you wanted?_',
                f'```css\n.d engagement rename NEW_NAME```_Want to remove ***{name}***?_',
                '```css\n.d engagement delete```'
            ]),
            'go_back_to_parent': ''.join([
                f'\n\n***You can GO BACK to the parent engagement, aspect, or stunt***',
                '```css\n.d engagement parent```'
            ])
        }
        dialog_string = ''
        if dialog_text == 'all':
            if not engagement:
                dialog_string += dialog.get('create_engagement', '')
            dialog_string += dialog.get('rename_delete', '')
        elif engagement.category == 'Engagement':
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_engagement', '')
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
        else:
            if dialog_text:
                dialog_string += dialog.get(dialog_text, '')
            else:
                dialog_string += dialog.get('active_engagement', '') if self.can_edit else ''
                dialog_string += dialog.get('rename_delete', '') if self.can_edit else ''
                dialog_string += dialog.get('go_back_to_parent', '') if self.can_edit else ''
        return dialog_string
    
    def name(self, args):
        if not self.sc:
            raise Exception('No active scene or name provided. Try this:```css\n.d scene SCENE_NAME```')
        messages = []
        if len(args) == 0:
            if not self.engagement:
                return [
                    'No active engagement or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.engagement.get_string(self.channel))
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_engagement_short')]
            if len(args) == 1 and self.engagement:
                return [self.dialog('')]
            engagement_type = args[1]
            if engagement_type == 'rename':
                engagement_name = ' '.join(args[2:])
                if not self.engagement:
                    return [
                        'No active engagement or name provided\n\n',
                        self.dialog('all')
                    ]
                else:
                    engagement = Engagement().find(self.guild.name, str(self.channel.id), str(self.sc.id), engagement_name)
                    if engagement:
                        return [f'Cannot rename to _{engagement_name}_. Engagement already exists']
                    else:
                        self.engagement.name = engagement_name
                        engagement_svc.save(self.engagement, self.user)
                        messages.append(self.dialog(''))
            else:
                if engagement_type not in ['conflict','contest','challenge']:
                    raise Exception('No engagement type (CONFLICT, CONTEST, CHALLENGE)')
                if len(args) > 2:
                    engagement_name = ' '.join(args[2:])
                else:
                    engagement_name = f'{engagement_type.title()} at {T.to(T.now())}'
                def canceler(cancel_args):
                    if cancel_args[0].lower() in ['engagement','engage','e']:
                        return EngagementCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                    else:
                        self.parent.args = cancel_args
                        self.parent.command = self.parent.args[0]
                        return self.parent.get_messages()

                def selector(selection):
                    self.engagement = selection
                    self.channel.set_active_engagement(self.engagement, self.user)
                    self.user.set_active_character(self.engagement.character)
                    engagement_svc.save_user(self.user)
                    return [self.dialog('')]

                def creator(**params):
                    item = Engagement().get_or_create(**params)
                    scenes = scenario_svc.get_scenes(self.scenario)
                    characters = scenario_svc.get_characters(scenes)
                    item.characters = [str(c.id) for c in characters]
                    item.type_name = engagement_type.title()
                    engagement_svc.save(item, self.user)
                    return item

                messages.extend(Dialog({
                    'svc': engagement_svc,
                    'user': self.user,
                    'title': 'Engagement List',
                    'command': 'engagement ' + ' '.join(args),
                    'type': 'select',
                    'type_name': 'ENGAGEMENT',
                    'getter': {
                        'method': Engagement.get_by_page,
                        'params': {'params': {'name__icontains': engagement_name, 'scene_id': str(self.sc.id), 'guild': self.guild.name, 'archived': False}}
                    },
                    'formatter': lambda item, item_num, page_num, page_size: f'_ENGAGEMENT #{item_num+1}_\n{item.get_short_string()}',
                    'cancel': canceler,
                    'select': selector,
                    'empty': {
                        'method': creator,
                        'params': {'user': self.user, 'name': engagement_name, 'scene': self.sc, 'channel': self.channel, 'guild': self.guild.name}
                    }
                }).open())
        return messages
    
    def select(self, args):
        messages = []
        if len(args) == 0:
            if not self.engagement:
                return [
                    'No active engagement or name provided\n\n',
                    self.dialog('all')
                ]
            messages.append(self.engagement.get_string(self.channel))
        else:
            if len(args) == 1 and args[0].lower() == 'short':
                return [self.dialog('active_engagement_short')]
            if len(args) == 1 and self.char:
                return [self.dialog('')]
            engagement_name = ' '.join(args[1:])
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['engagement','engage','e']:
                    return EngagementCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

            def selector(selection):
                self.engagement = selection
                self.channel.set_active_engagement(self.engagement, self.user)
                self.user.set_active_character(self.engagement)
                engagement_svc.save_user(self.user)
                return [self.dialog('')]

            messages.extend(Dialog({
                'svc': engagement_svc,
                'user': self.user,
                'title': 'Engagement List',
                'command': 's ' + ' '.join(args),
                'type': 'select',
                'type_name': 'ENGAGEMENT',
                'getter': {
                    'method': Engagement.get_by_page,
                    'params': {'params': {'name__icontains': engagement_name, 'scene_id': str(self.sc.id), 'guild': self.guild.name, 'archived': False}}
                },
                'formatter': lambda item, item_num, page_num, page_size: f'_ENGAGEMENT #{item_num+1}_\n{item.get_short_string()}',
                'cancel': canceler,
                'select': selector
            }).open())
        return messages

    def engagement_list(self, args):
        messages = []
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['engagement']:
                return EngagementCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        messages.extend(Dialog({
            'svc': engagement_svc,
            'user': self.user,
            'title': 'Engagement List',
            'command': 'engagement ' + (' '.join(args)),
            'type': 'view',
            'type_name': 'ENGAGEMENT',
            'getter': {
                'method': Engagement().get_by_scene,
                'params': {'scene': self.sc, 'archived': False}
            },
            'formatter': lambda item, item_num, page_num, page_size: f'{item.get_short_string(self.channel)}',
            'cancel': canceler
        }).open())
        return messages

    def description(self, args):
        if len(args) == 1:
            return ['No description provided']
        if not self.engagement:
            return ['You don\'t have an active engagement.\nTry this: ".d s name {name}"']
        else:
            description = ' '.join(args[1:])
            self.engagement.description = description
            self.engagement.updated_by = str(self.user.id)
            self.engagement.updated = T.now()
            self.engagement.save()
            return [
                f'Description updated to "{description}"',
                self.engagement.get_string(self.channel)
            ]

    def character(self, args):
        if self.user:
            self.user.active_character = str(self.engagement.character.id)
            self.user.updated_by = str(self.user.id)
            self.user.updated = T.now()
            self.user.save()
        command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=args, guild=self.guild, user=self.user, channel=self.channel, char=self.engagement.character)
        return command.run()

    def player(self, args):
        return engagement_svc.player(args, self.channel, self.engagement, self.user)

    def oppose(self, args):
        return engagement_svc.oppose(args, self.channel, self.engagement, self.user)

    def delete_engagement(self, args):
        return engagement_svc.delete_engagement(args, self.guild, self.channel, self.scene, self.engagement, self.user)

    def start(self, args):
        self.check_engagement()
        if self.engagement.started_on:
            raise Exception(f'***{self.engagement.name}*** already began on {T.to(self.engagement.started_on, self.user)}')
        else:
            self.engagement.started_on = T.now()
            engagement_svc.save(self.engagement, self.user)
            return [self.dialog('')]

    def end(self, args):
        self.check_engagement()
        if len(args) > 1 and args[1] == 'delete':
            self.engagement.ended_on = None
            engagement_svc.save(self.engagement, self.user)
            return [self.dialog('')]
        else:
            if not self.engagement.started_on:
                raise Exception(f'***{self.engagement.name}*** has not yet started.')
            if self.engagement.ended_on:
                raise Exception(f'***{self.engagement.name}*** already ended on {T.to(self.engagement.ended_on, self.user)}')
            else:
                self.engagement.ended_on = T.now()
                engagement_svc.save(self.engagement, self.user)
                return [self.dialog('')]