# suggestion_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from models import Suggestion
from utils import T
from services.base_service import BaseService

class SuggestionService(BaseService):

    def delete_suggestion(self, args, user):
        messages = []
        search = ''
        if len(args) <= 1:
            raise Exception('Suggestion delte syntax\n```css\n.d suggestion delete "NAME"```')
        if len(args) > 1:
            search = ' '.join(args[1:])
            suggestion = Suggestion().find(search)
        if not suggestion:
            return [f'_"{search}"_ was not found. No changes made.']
        else:
            search = str(suggestion.text)
            suggestion.archived = True
            self.save(suggestion, user)
            messages.append(f'***{search}*** removed')
            return messages
