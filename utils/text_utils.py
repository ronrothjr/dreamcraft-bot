# text_utils.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import re

class TextUtils(object):
    @staticmethod
    def clean(str):
        return " ".join(re.findall("[a-zA-Z]+", str))

    @staticmethod
    def value_with_quotes(args):
        return ' '.join([('\\"' + arg + '\\"' if ' ' in arg else arg) for arg in args])