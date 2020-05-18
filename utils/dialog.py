# dialof.py
import math
import copy

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
        paging_question = ''
        items = None
        page_num = 1
        page_count = self.get_page_count()
        select_question = self.get_select_str() if self.select and page_count and page_count > 0 else ''
        if self.user.command == self.command:
            answer = self.user.answer
            paging_question = self.user.question
            if page_count> 0 and answer and (answer in ['<<','<','>','>>'] or answer.isdigit()):
                page_num_str = paging_question[paging_question.find('Page ')+5:paging_question.find(' of ')]
                page_num = int(page_num_str)
                if answer.isdigit():
                    new_page_num = int(answer)
                    if new_page_num > page_count or new_page_num < 1:
                        raise Exception(f'Page number {page_num} does not exist')
                else:
                    options = {'<<': 1, '<': page_num - 1, '>': page_num + 1, '>>': page_count}
                    new_page_num = options.get(answer, None)
                if new_page_num and new_page_num > 0 and new_page_num <= page_count:
                    page_num = new_page_num
                paging_question = self.get_page_str(page_num, page_count)
                items = list(self.get_list(page_num))
                question = f'{select_question}{paging_question}'
                self.set_dialog(self.command, question)
            elif '=' in answer and self.select:
                selection = answer[answer.find('=')+1:]
                if not selection.isdigit():
                    raise Exception('Your selection is invalid')
                item_num = int(selection)
                items = list(self.get_list(page_num))
                if item_num < 1 or item_num > len(items):
                    raise Exception('Your selection is invalid')
                self.set_dialog()
                return self.select(items[item_num-1])
            else:
                self.set_dialog()
                if self.cancel:
                    return self.cancel(tuple(answer.split(' ')))
                else:
                    return [f'***{self.command}*** command cancelled']
        else:
            items = list(self.get_list(page_num)) if page_count else None
            paging_question = self.get_page_str(page_num, page_count) if page_count and page_count > 1 else ''
            question = f'{select_question}{paging_question}'
            self.set_dialog(self.command if question else '', question)
        if items and len(items) == 1 and self.select:
            return self.select(items[0])
        elif items:
            content = self.get_content(items)
            return [f'{content}\n{question}']
        else:
            return self.no_items()

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
        data_params = {}
        for p in params:
            data_params[p] = params[p]
        data_params.update({'page_num': None})
        item_count = method(**data_params).count()
        return math.ceil(item_count/self.page_size) if item_count else None

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
        items = self.get_descendants(items, data_params, page_num)
        return items

    def get_descendants(self, items, params, page_num):
        parent_method = self.getter.get('parent_method', None)
        params = copy.deepcopy(self.getter.get('params', None))
        if parent_method is not null and params is not null and hasattr(item, 'parent_id'):
            parent_ids = []
            for item in items:
                parent_ids.extend(self.get_parent_ids(child))
            method = self.getter.get('method', None)
            parent_ids = []
            [parent_ids.extend(self.get_parent_ids(item)) for item in items if 'parent_id' in params]
            self.getter.get('method', None)
            params = [f'{self.data[d]}' for d in params if d == 'parent_id']
            params.update(parent_id__in=parend_ids)
            items = list(method(**params))
            items.sort(key=lambda i: i.created)
            offset = (page_num-1) * self.page_size
            items = items[offset:offset+self.page_size]
        return items

    def get_parent_ids(self, item):
        parent_ids = []
        if item and 'parent_id' in params:
            parent_method = self.getter.get('parent_method', None)
            got_attr = hasattr(item, 'category') and item.category in ['Character', 'Stunt', 'Aspect']
            got_parent_id = hasattr(item, 'parent_id') and item.parent_id
            child_items = parent_method({'parent_id': item.parent_id}, page_num=0)
            [parent_ids.append(str(child.id)) for child in child_items]
            parent_ids.extend(self.get_parent_ids(child)) for child in child_items
        return parent_ids

    def get_content(self, items):      
        items_string = '\n\n'.join([self.formatter(items[i], i) for i in range(0, len(items))])
        content = f'***{self.title}:***\n\n{items_string}\n'
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