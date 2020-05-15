# pager.py
import math

class Pager(object):
    def __init__(self, char_svc):
        self.char_svc = char_svc

    def manage_paging(self, title, command, user, data_getter, formatter, page_size=5):
        question = ''
        page_num = 1
        page_count = self.get_page_count(user, data_getter, page_size)
        if not page_count:
            raise Exception(f'You don\'t have anything in your {title}.')
        if user.command == command:
            answer = user.answer
            question = user.question
            if answer and (answer in ['<<','<','>','>>'] or answer.isdigit()):
                page_num_str = question[question.find('Page ')+5:question.find(' of ')]
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
                question = self.get_page_str(page_num, page_count)
                user.question = question
                user.answer = ''
                self.char_svc.save_user(user)
            else:
                user.command = ''
                user.question = ''
                user.answer = ''
                self.char_svc.save_user(user)
                return tuple(answer.split(' ')), None
        else:
            question = self.get_page_str(page_num, page_count)
            user.command = command
            user.question = question
            user.answer = ''
            self.char_svc.save_user(user)
        page_content = self.get_content(title, data_getter, formatter, page_num, page_size)
        return None, f'{page_content}\n{question}'

    def get_page_count(self, user, data_getter, page_size=5):
        method = data_getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = data_getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        data_params = {}
        for p in params:
            data_params[p] = params[p]
        data_params.update({'page_num': None})
        page_count = method(**data_params).count()
        return math.ceil(page_count/page_size) if page_count else None

    def get_page_str(self, page_num, page_count):
        return ''.join([
            f'Page {page_num} of {page_count} - Enter page number, **\'<<\'**, **\'<\'**, **\'>\'** or **\'>>\'**:',
            '```css\n.d 1 /* to jump to a page */\n',
            '.d << /* to go to the first page */\n',
            '.d < /* to go to the previous page */\n',
            '.d > /* to go to the next page */\n',
            '.d >> /* to go to the last page */```'
        ])

    def get_content(self, title, data_getter, formatter, page_num=1, page_size=5):
        method = data_getter.get('method', None)
        if not method:
            raise Exception('No data getter method supplied')
        params = data_getter.get('params', None)
        if not params:
            raise Exception('No data getter params supplied')
        data_params = {}
        for p in params:
            data_params[p] = params[p]
        data_params.update({'page_num': page_num, 'page_size': page_size})
        items_string = '\n'.join([formatter(item) for item in method(**data_params)])
        return f'***{title}:***\n\n{items_string}\n'