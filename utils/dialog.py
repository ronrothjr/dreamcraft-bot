# dialof.py
import math

class Dialog(object):
    def __init__(self, params):
        self.svc = params.get('svc', None)
        self.title = params.get('title', None)
        self.type = params.get('type', None)
        self.type_name = params.get('type_name', None)
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
        select_question = self.get_select_str() if self.select else ''
        paging_question = ''
        items = None
        page_num = 1
        page_count = self.get_page_count()
        if self.user.command == self.command:
            answer = self.user.answer
            paging_question = self.user.question
            if page_count> 1 and answer and (answer in ['<<','<','>','>>'] or answer.isdigit()):
                page_num_str = paging_question[paging_question.find('Page ')+5:paging_question.find(' of ')]
                page_num = int(page_num_str)
                if answer.isdigit():
                    page_num = int(answer)
                    if page_num > page_count or page_num < 1:
                        raise Exception(f'Page number {page_num} does not exist')
                elif answer == '<<' and page_num > 1:
                    page_num = 1
                elif answer == '<' and page_num > 1:
                    page_num -= 1
                elif answer == '>' and page_num < page_count:
                    page_num += 1
                elif answer == '>>' and page_num < page_count:
                    page_num = page_count
                paging_question = self.get_page_str(page_num, page_count)
                items = list(self.get_list(page_num))
                question = f'{select_question}{paging_question}'
                self.set_user(self.command, question)
            elif '=' in answer and self.select:
                selection = answer[answer.find('=')+1:]
                if not selection.isdigit():
                    raise Exception('Your selection is invalid')
                item_num = int(selection)
                items = list(self.get_list(page_num))
                if item_num < 1 or item_num > len(items):
                    raise Exception('Your selection is invalid')
                self.set_user()
                return self.select(items[item_num-1])
            else:
                self.set_user()
                if self.cancel:
                    return self.cancel(tuple(answer.split(' ')))
                else:
                    return [f'***{self.command}*** command cancelled']
        else:
            items = self.get_list(page_num) if page_count else None
            paging_question = self.get_page_str(page_num, page_count) if page_count > 1 else ''
            question = f'{select_question}{paging_question}'
            self.set_user(self.command, question)
        if items:
            content = self.get_content(items)
            return [f'{content}\n{question}']
        else:
            return self.no_items(items)

    def set_user(self, command='', question='', answer=''):
        self.user.command = command
        self.user.question = question
        self.user.answer = answer
        self.svc.save_user(self.user)

    def no_items(self, items):
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
            return [content]
        else:
            return [f'You don\'t have anything in your {self.title}.']

    def get_page_count(self):
        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        data_params = {}
        for p in params:
            data_params[p] = params[p]
        data_params.update({'page_num': None})
        page_count = method(**data_params).count()
        return math.ceil(page_count/self.page_size) if page_count else None

    def get_page_str(self, page_num, page_count):
        return ''.join([
            f'Page {page_num} of {page_count} - Enter page number, **\'<<\'**, **\'<\'**, **\'>\'** or **\'>>\'**',
            '```css\n.d 1 /* to jump to a page */\n',
            '.d << /* to go to the first page */\n',
            '.d < /* to go to the previous page */\n',
            '.d > /* to go to the next page */\n',
            '.d >> /* to go to the last page */```'
        ])

    def get_select_str(self):
        return ''.join([
            f'SELECT a {self.type_name} by entering **\'=\'** followed by the {self.type_name} number:',
            '```css\n.d =2 /* select item 2 from the list */```' if self.type == 'select' else ''
        ])

    def get_list(self, page_num=1):
        method = self.getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = self.getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        data_params = {}
        for p in params:
            data_params[p] = params[p]
        data_params.update({'page_num': page_num, 'page_size': self.page_size})
        items = method(**data_params)
        return items

    def get_content(self, items):      
        items_string = '\n\n'.join([self.formatter(items[i], i) for i in range(0, len(items))])
        content = f'***{self.title}:***\n\n{items_string}\n'
        return content