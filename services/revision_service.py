# revision_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from models import Revision
from utils import T

class RevisionService():
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

    def delete_revision(self, args, user):
        messages = []
        search = ''
        if len(args) <= 1:
            raise Exception('Revision delte syntax\n```css\n.d revision delete "NAME"```')
        if len(args) > 1:
            search = ' '.join(args[2:])
            revision = Revision().find(search)
        if not revision:
            return [f'"{search}"" was not found. No changes made.']
        else:
            search = str(revision.name)
            revision.archived = True
            self.save(revision, user)
            messages.append(f'***{search}*** removed')
            return messages
