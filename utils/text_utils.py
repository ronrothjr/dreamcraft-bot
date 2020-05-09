# text_utils.py
import re

class TextUtils(object):
    @staticmethod
    def clean(str):
        return " ".join(re.findall("[a-zA-Z]+", str))