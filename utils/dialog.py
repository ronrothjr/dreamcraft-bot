# dialog.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import math
import copy
import inflect
p = inflect.engine()

class Dialog(object):
    """
    Provide a dialog interface for diplaying questions, lists, paging, and selection instructions

    Stores the following attributes in the User object:
        command - the command that started the dialog which is used to trap the response
        question - the question displayed to the user (also used to store the state of the dialog)
        answer - the response entered by the user
    A typical dialog example for displaying and interacting with a list:
    ```
        def character_list(self, args):
            messages = []
            def canceler(cancel_args):
                if cancel_args[0].lower() in ['character','char','c']:
                    return CharacterCommand(parent=self.parent, ctx=self.ctx, args=cancel_args, guild=self.guild, user=self.user, channel=self.channel).run()
                else:
                    self.parent.args = cancel_args
                    self.parent.command = self.parent.args[0]
                    return self.parent.get_messages()

            def selector(selection):
                self.char = selection
                self.user.set_active_character(self.char)
                char_svc.save_user(self.user)
                return [self.dialog('active_character')]

            def formatter(item, item_num, page_num, page_size):
                return f'_CHARACTER #{((page_num-1)*page_size)+item_num+1}_\n{item.get_short_string(self.user)}'

            messages.extend(Dialog({
                'svc': char_svc,
                'user': self.user,
                'title': 'Character List',
                'command': 'c ' + ('npc ' if self.npc else '' ) + (' '.join(args)),
                'type': 'view',
                'type_name': 'CHARCTER',
                'getter': {
                    'method': Character.get_by_page,
                    'params': {'params': {'guild': self.guild.name, 'category': 'Character', 'archived': False}}
                },
                'formatter': formatter,
                'cancel': canceler,
                    'select': selector
            }).open())
            return messages
    ```
    """

    def __init__(self, params):
        """Constructor for Dialog class

        Parameters
        ----------
        params : dict
            Dictionary object containing the following keys:
                svc : BaseService
                    A service for common database model operations
                title : str
                    The title for the dialog display
                type : str
                    Defines the function of the dailog: view or select
                type_name : str, optional
                    The name of the item being selected or views, defaults to 'ITEM'
                command : str
                    The command arguments stored for identifying responses
                user : User
                    The user that started the dialog
                getter : dict
                    Dictionary containing the parameters for retrieving information for display within the dialog
                select : method, optional
                    Callback method for receiving the selected object
                cancel : method, optional
                    Callback for receiving input that exits the dialog
                confirm : method, optional
                    Callback for receiving input to handle input when dialog receives a 'y' or 'yes' confirmation
                page_size : int
                    Number of items to be displayed per page

        Returns
        -------
        Dialog - a class to provide an interface for information with user question/answer
        """

        self.svc = params.get('svc', None)
        self.title = params.get('title', None)
        self.type = params.get('type', None)
        self.type_name = params.get('type_name', 'ITEM')
        self.command = params.get('command', None)
        self.user = params.get('user', None)
        self.getter = params.get('getter', None)
        self.formatter = params.get('formatter', None)
        self.select = params.get('select', None)
        self.cancel = params.get('cancel', None)
        self.confirm = params.get('confirm', None)
        self.page_size = params.get('page_size', 5)

    def open(self):
        """Open the dialog or handle dialog response"""

        question = ''
        paging_question = ''
        self.items = None
        self.page_num = 1
        self.page_count = self.get_page_count()
        select_question = self.get_select_str()
        # Determine if the user has provided an answer to the dialog
        if self.user.command == self.command:
            answer = self.user.answer
            paging_question = self.user.question

            # Handle navigation responses
            if self.page_count > 0 and answer and (answer in ['<<','<','>','>>'] or answer.isdigit()):
                page_num_str = paging_question[paging_question.find('Page ')+5:paging_question.find(' of ')]
                self.page_num = int(page_num_str)
                if answer.isdigit():
                    new_page_num = int(answer)
                    if new_page_num > self.page_count or new_page_num < 1:
                        raise Exception(f'Page number {new_page_num} does not exist')
                else:
                    options = {'<<': 1, '<': self.page_num - 1, '>': self.page_num + 1, '>>': self.page_count}
                    new_page_num = options.get(answer, None)
                if new_page_num and new_page_num > 0 and new_page_num <= self.page_count:
                    self.page_num = new_page_num
                paging_question = self.get_page_str()
                self.items = list(self.get_list())
                question = f'{select_question}{paging_question}'
                self.set_dialog(self.command, question)
            
            # Handle selection response
            elif '=' in answer and self.select:
                selection = answer[answer.find('=')+1:]
                if not selection.isdigit():
                    raise Exception('Your selection is invalid')
                item_num = int(selection)
                self.items = list(self.get_entire_list())
                if item_num < 1 or item_num > len(self.items):
                    raise Exception('Your selection is invalid')
                self.set_dialog()
                return self.select(self.items[item_num-1])

            # Handle confirmation response
            elif answer.lower() in ['yes','y']:
                self.set_dialog()
                return self.confirmation()

            # Handle cancel response
            else:
                self.set_dialog()
                if self.cancel:
                    return self.cancel(tuple(answer.split(' ')))
                else:
                    return [f'***{self.command}*** command cancelled']

        # If this is the first pass through the dialog, get item information for display
        else:
            self.items = list(self.get_list()) if self.page_count else None

        # If this is a selection list and there is only one item, select the first item
        if self.items and self.item_count == 1 and self.select:
            return self.select(self.items[0])

        # Else, display the item information with the question response
        else:
            paging_question = self.get_page_str() if self.page_count and self.page_count > 0 else ''
            question = f'{select_question}{paging_question}'
            self.set_dialog(self.command if question else '', question)
            content = self.get_content(self.items) if self.items else ''
            return [f'{content}\n{question}' if content or question else f'No {p.plural(self.type_name).upper()} found']

    def set_dialog(self, command='', question='', answer=''):
        """Set the dialog information in the user documetn"""

        self.user.command = command
        self.user.question = question
        self.user.answer = answer
        self.svc.save_user(self.user)

    def get_page_count(self):
        """Get the total number of pages for the items to be displayed"""

        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        self.items = method(**params, page_num=0)
        if not isinstance(self.items, list):
            self.items = list(self.items)
        self.item_count = len(self.items)
        return math.ceil(self.item_count/self.page_size) if self.item_count else 0

    def get_page_str(self):
        """Get the instructions for paging through items"""

        page_str = ''
        if self.page_count == 1:
            page_str = f'\nPage {self.page_num} of {self.page_count} ({self.item_count} total)'
        elif self.page_count > 1:
            page_str = ''.join([
            f'\nPage {self.page_num} of {self.page_count} ({self.item_count} total) - Enter page number, **\'<<\'**, **\'<\'**, **\'>\'** or **\'>>\'**',
            '```css\n.d 1 /* to jump to a page */\n',
            '.d << /* to go to the first page */\n',
            '.d < /* to go to the previous page */\n',
            '.d > /* to go to the next page */\n',
            '.d >> /* to go to the last page */```'
        ])
        return page_str

    def get_select_str(self):
        """Get the instructions for selecting items"""

        select_str = ''
        if self.type.lower() == 'confirm':
            select_str = ''.join([
                f'\n\n{self.formatter(self.items)}',
                f'\n\nREPLY TO CONFIRM:',
                '```css\n.d yes /* to confirm the command */```'
            ])
        elif self.page_count:
            select_str = ''.join([
                f'\nSELECT a {p.an(self.type_name)} by entering **\'=\'** followed by the {self.type_name} number:',
                '```css\n.d =2 /* select item 2 from the list */```'
            ]) if self.type == 'select' else ''
        elif self.confirm:
            name = self.confirm['params']['name']
            select_str = ''.join([
                f'Create a new {self.type_name} named ***{name}***?',
                f'```css\n.d yes /* to confirm the command */```'
            ])
        return select_str

    def get_list(self):
        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        self.items = method(**params, page_num=self.page_num, page_size=self.page_size)
        return self.items

    def get_entire_list(self):
        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        self.items = method(**params, page_num=0)
        return self.items

    def get_content(self, items):
        content = ''
        if items:
            items_string = '\n\n'.join([self.formatter(items[i], i, self.page_num, self.page_size) for i in range(0, len(items))])
            content = f'***{self.title}:***\n\n{items_string}'
        return content

    def confirmation(self):
        if self.confirm:
            method = self.confirm['method']
            if not method:
                raise Exception('No confirm method supplied')
            params = self.confirm['params']
            if not params:
                raise Exception('No confirm params supplied')
            item = method(**params)
            if self.select:
                content = self.select(item)
            elif item:
                content = [item.get_string()]
            else:
                content = []
            return content
        else:
            return [f'You don\'t have anything in your {self.title}.']
