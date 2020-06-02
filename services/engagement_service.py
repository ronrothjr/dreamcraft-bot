# engagement_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from bson.objectid import ObjectId
from models import User, Channel, Character, Engagement
from utils import TextUtils, T
from services.base_service import BaseService

class EngagementService(BaseService):

    def player(self, args, channel, engagement, user):
        messages = []
        if len(args) == 1:
            raise Exception('No characters added')
        if not engagement:
            raise Exception('You don\'t have an active engagement. Try this:```css\n.d engagement ENGAGEMENT_NAME```')
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [engagement.get_string_characters(channel)]
        elif args[1].lower() in ['delete','d']:
            for char_name in args[2:]:
                char = Character().find(user=user, name=char_name, guild=channel.guild, category='Character')
                [engagement.characters.remove(s) for s in engagement.characters if char and str(char.id) == s]
                messages.append(f'***{char.name}*** removed from _{engagement.name}_ characters' if char else f'**{char_name}** was not found')
            self.save(engagement, user)
            messages.append(engagement.get_string_characters(user))
            return messages
        else:
            for char_name in args[1:]:
                char = Character().find(None, char_name, channel.guild)
                if char:
                    if str(char.id) in engagement.characters:
                        messages.append(f'***{char.name}*** is already in _{engagement.name}_ characters')
                    else:
                        engagement.characters.append(str(char.id))
                        messages.append(f'Added ***{char.name}*** to _{engagement.name}_ engagement characters')
                else:
                    messages.append(f'***{char_name}*** not found. No character added to _{engagement.name}_ characters')
            self.save(engagement, user)
            messages.append(engagement.get_string_characters(user))
            return messages

    def oppose(self, args, channel, engagement, user):
        messages = []
        if len(args) == 1:
            raise Exception('No opposition added')
        if not engagement:
            raise Exception('You don\'t have an active engagement. Try this:```css\n.d engagement ENGAGEMENT_NAME```')
        elif args[1].lower() == 'list' or args[1].lower() == 'l':
            return [engagement.get_string_opposition(channel)]
        elif args[1].lower() in ['delete','d']:
            for char_name in args[2:]:
                char = Character().find(user=user, name=char_name, guild=channel.guild, category='Character')
                [engagement.opposition.remove(s) for s in engagement.opposition if char and str(char.id) == s]
                messages.append(f'***{char.name}*** removed from the opposition in _{engagement.name}_' if char else f'**{char_name}** was not found')
            self.save(engagement, user)
            messages.append(engagement.get_string_opposition(user))
            return messages
        else:
            for char_name in args[1:]:
                char = Character().find(None, char_name, channel.guild)
                if char:
                    if str(char.id) in engagement.opposition:
                        messages.append(f'***{char.name}*** is already in the opposition in the _{engagement.name}_ engagement')
                    else:
                        engagement.opposition.append(str(char.id))
                        messages.append(f'Added ***{char.name}*** to the opposition in the _{engagement.name}_ engagement')
                else:
                    messages.append(f'***{char_name}*** not found. No opposition added to _{engagement.name}_')
            self.save(engagement, user)
            messages.append(engagement.get_string_opposition(user))
            return messages

    def delete_engagement(self, args, guild, channel, scene, engagement, user):
        messages = []
        search = ''
        if len(args) == 1:
            if not engagement:
                raise Exception('No engagement provided for deletion')
        else:
            search = ' '.join(args[1:])
            engagement = Engagement().find(guild.name, str(channel.id), str(scene.id), search)
        if not engagement:
            return [f'{search} was not found. No changes made.']
        else:
            search = str(engagement.name)
            channel_id = str(engagement.channel_id) if engagement.channel_id else ''
            engagement.character.archive(user)
            engagement.archived = True
            self.save(engagement, user)
            messages.append(f'***{search}*** removed')
            if channel_id:
                channel = Channel().get_by_id(channel_id)
                messages.append(channel.get_string())
            return messages
