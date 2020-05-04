# aspect.py
from mongoengine import *

class Aspect(Document):

    name = StringField(required=True)
    parent_id = StringField(required=True)
    is_boost = BooleanField()
    stress = ListField(StringField())

    def create_new(self, name, guild):
        self.name = name
        self.save()
        return self

    def find(self, name, guild):
        filter = Aspect.objects(name=name)
        user = filter.first()
        return user

    def get_or_create(self, name, guild):
        user = self.find(name, guild)
        if user is None:
            user = self.create_new(name, guild)
        return user

    def get_string(self):
        return f'Player: {self.name}'
        