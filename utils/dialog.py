# dialog.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import math
import copy
import inflect
p = inflect.engine()

class Dialog(object):
    def __init__(self, params):
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
        self.empty = params.get('empty', None)
        self.page_size = params.get('page_size', 5)

    def open(self):
        question = ''
        paging_question = ''
        items = None
        self.page_num = 1
        self.page_count = self.get_page_count()
        select_question = self.get_select_str()
        if self.user.command == self.command:
            answer = self.user.answer
            paging_question = self.user.question
            if self.page_count > 0 and answer and (answer in ['<<','<','>','>>'] or answer.isdigit()):
                page_num_str = paging_question[paging_question.find('Page ')+5:paging_question.find(' of ')]
                self.page_num = int(page_num_str)
                if answer.isdigit():
                    new_page_num = int(answer)
                    if new_page_num > self.page_count or new_page_num < 1:
                        raise Exception(f'Page number {self.page_num} does not exist')
                else:
                    options = {'<<': 1, '<': self.page_num - 1, '>': self.page_num + 1, '>>': self.page_count}
                    new_page_num = options.get(answer, None)
                if new_page_num and new_page_num > 0 and new_page_num <= self.page_count:
                    self.page_num = new_page_num
                paging_question = self.get_page_str()
                items = list(self.get_list())
                question = f'{select_question}{paging_question}'
                self.set_dialog(self.command, question)
            elif '=' in answer and self.select:
                selection = answer[answer.find('=')+1:]
                if not selection.isdigit():
                    raise Exception('Your selection is invalid')
                item_num = int(selection)
                items = list(self.get_entire_list())
                if item_num < 1 or item_num > len(items):
                    raise Exception('Your selection is invalid')
                self.set_dialog()
                return self.select(items[item_num-1])
            elif answer.lower() in ['yes','y']:
                return self.no_items()
            else:
                self.set_dialog()
                if self.cancel:
                    return self.cancel(tuple(answer.split(' ')))
                else:
                    return [f'***{self.command}*** command cancelled']
        else:
            items = list(self.get_list()) if self.page_count else None
        # If this is a selection list and there is only one item, select the first item
        if items and self.item_count == 1 and self.select:
            return self.select(items[0])
        else:
            paging_question = self.get_page_str() if self.page_count and self.page_count > 0 else ''
            question = f'{select_question}{paging_question}'
            self.set_dialog(self.command if question else '', question)
            content = self.get_content(items) if items else ''
            return [f'{content}\n{question}' if content or question else f'No {p.plural(self.type_name).upper()} found']

    def set_dialog(self, command='', question='', answer=''):
        self.user.command = command
        self.user.question = question
        self.user.answer = answer
        self.svc.save_user(self.user)

    def get_page_count(self):
        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        self.item_count = method(**params, page_num=0).count()
        return math.ceil(self.item_count/self.page_size) if self.item_count else 0

    def get_page_str(self):
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
        select_str = ''
        if self.page_count:
            select_str = ''.join([
                f'\nSELECT a {p.an(self.type_name)} by entering **\'=\'** followed by the {self.type_name} number:',
                '```css\n.d =2 /* select item 2 from the list */```'
            ]) if self.type == 'select' else ''
        elif self.empty:
            name = self.empty['params']['name']
            select_str = ''.join([
                f'Create a new {self.type_name} named ***{name}***?',
                f'```css\n.d YES /* to confirm the command */\n.d NO /* to reject the command */```'
            ])
        return select_str

    def get_list(self):
        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        items = method(**params, page_num=self.page_num, page_size=self.page_size)
        return items

    def get_entire_list(self):
        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        items = method(**params, page_num=0)
        return items

    def get_content(self, items):
        content = ''
        if items:
            items_string = '\n\n'.join([self.formatter(items[i], i, self.page_num, self.page_size) for i in range(0, len(items))])
            content = f'***{self.title}:***\n\n{items_string}'
        return content

    def no_items(self):
        if self.empty:
            method = self.empty['method']
            if not method:
                raise Exception('No empty method supplied')
            params = self.empty['params']
            if not params:
                raise Exception('No empty params supplied')
            item = method(**params)
            if self.select:
                content = self.select(item)
            else:
                content = [item.get_string()]
            return content
        else:
            return [f'You don\'t have anything in your {self.title}.']
