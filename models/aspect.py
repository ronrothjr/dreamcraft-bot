# aspect.py
import datetime
from mongoengine import *

class Aspect(Document):

    name = StringField(required=True)
    parent_id = StringField(required=True)
    char_id = StringField()
    is_boost = BooleanField()
    stress = ListField(StringField())
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    def create_new(self, name, parent_id):
        self.name = name
        self.parent_id = parent_id
        self.created = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()
        self.save()
        return self

    def find(self, name, parent_id):
        filter = Aspect.objects(name=name, parent_id=parent_id)
        aspect = filter.first()
        return aspect

    def get_or_create(self, name, parent_id):
        aspect = self.find(name, str(parent_id))
        if aspect is None:
            aspect = self.create_new(name, str(parent_id))
        return aspect

    def get_by_id(self, id):
        aspect = Aspect.objects(id=id).first()
        return aspect

    def get_by_parent_id(self, parent_id, name=''):
        aspects = []
        if name:
            aspect = Aspect.objects(parent_id=str(parent_id), name__icontains=name).first()
            aspects = [aspect] if aspect else []
        else:
            aspects = Aspect.objects(parent_id=str(parent_id)).all()
        return aspects

    def get_string(self):
        return f'{self.name}'
        