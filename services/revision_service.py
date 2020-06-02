# revision_service.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

from models import Revision
from utils import T
from services.base_service import BaseService

class RevisionService(BaseService):

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
