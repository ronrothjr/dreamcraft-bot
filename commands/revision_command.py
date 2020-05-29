# revision_command.py
import traceback
import pytz
from config.setup import Setup
from models import User
from models import Revision
from services import RevisionService
from utils import T, Dialog

SETUP = Setup()
REVISION_HELP = SETUP.revision_help

revision_svc = RevisionService()

class RevisionCommand():
    def __init__(self, parent, ctx, args, guild, user, channel):
        self.parent = parent
        self.ctx = ctx
        self.args = args[1:] if args[0] in ['revision', 'rev'] else args
        self.command = self.args[0].lower() if len(self.args) > 0 else ''
        self.guild = guild
        self.user = user
        self.channel = channel
        self.can_edit = self.user.role == 'Admin' if self.user else False

    def run(self):
        try:
            switcher = {
                'help': self.help,
                'list': self.revision_list,
                'l': self.revision_list,
                'name': self.name,
                'n': self.name,
                'delete': self.delete_revision
            }
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: self.name)
                # Execute the function
                messages = func(self.args)
            else:
                self.args = ('list',) + self.args
                self.command = 'list'
                func = self.revision_list
                messages = func(self.args)
            # Send messages
            return messages
        except Exception as err:
            traceback.print_exc()
            return list(err.args)

    def help(self):
        return [REVISION_HELP]

    def name(self, args):
        messages = []
        rev_name = ' '.join(args[1:])
        if args[1] == 'rename':
            if len(args) < 4:
                raise Exception('syntax: ```css\n.d revision rename "ORIGINAL_NAME" "NEW_NAME"```')
            rev_name_orig = ' '.join(args[2])
            rev_name_new = ' '.join(args[3])
            revision_new = Revision().find(rev_name_new)
            if revision_new:
                raise Exception(f'Cannot rename to _{rev_name_new}_. Revision already exists')
            else:
                revision = Revision().find(rev_name_orig)
                if not rev_name_orig:
                    raise Exception(f'Cannot find original revision named _{rev_name_orig}_')
                revision.name = rev_name_new
                revision_svc.save(revision, self.user)
                messages.append(revision.get_string(self.user))
        else:
            if len(args) < 4:
                raise Exception('syntax: ```css\n.d revision name "NAME" "NUMBER" "TEXT"```')
            rev_name = args[1]
            rev_number = args[2]
            rev_text = args[3]
            params = {'name': rev_name, 'number': rev_number, 'text': rev_text}
            revision = Revision().get_or_create(**params)
            messages.append(revision.get_string(self.user))
        return messages

    def revision_list(self, args):
        messages = []
        def canceler(cancel_args):
            if cancel_args[0].lower() in ['revision','rev']:
                return RevisionCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
            else:
                self.parent.args = cancel_args
                self.parent.command = self.parent.args[0]
                return self.parent.get_messages()

        def formatter(item, item_num, page_num, page_size):
            return item.get_short_string(self.user)

        messages.extend(Dialog({
            'svc': revision_svc,
            'user': self.user,
            'title': 'Revision List',
            'command': 'revision ' + (' '.join(args)),
            'type': 'view',
            'type_name': 'REVISION',
            'page_size': 1,
            'getter': {
                'method': Revision.get_by_page,
                'params': {'params': {'archived': False}}
            },
            'formatter': formatter,
            'cancel': canceler
        }).open())
        return messages

    def delete_revision(self, args):
        return revision_svc.delete_revision(args, self.user)