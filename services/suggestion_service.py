# suggestion_service.py
from models import Suggestion
from utils import T

class SuggestionService():
    def search(self, args, method, params):
        if len(args) == 0:
            return None
        item = method(**params).first()
        if item:
            return item
        else:
            return None

    def save(self, item, user):
        if item:
            item.updated_by = str(user.id)
            item.updated = T.now()
            item.history_id = ''
            item.save()

    def save_user(self, user):
        if user:
            user.updated_by = str(user.id)
            user.updated = T.now()
            user.save()

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
