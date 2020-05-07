# stunt.py
import datetime
from mongoengine import *

class Stunt(Document):

    name = StringField(required=True)
    description = StringField()
    parent_id = StringField(required=True)
    char_id = StringField()
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
        filter = Stunt.objects(name=name, parent_id=parent_id)
        stunt = filter.first()
        return stunt

    def get_or_create(self, name, parent):
        stunt = self.find(name, str(parent.id))
        if stunt is None:
            stunt = self.create_new(name, str(parent.id))
        return stunt

    def get_by_id(self, id):
        stunt = Stunt.objects(id=id).first()
        return stunt

    def get_by_parent(self, parent, name=''):
        stunts = []
        if name:
            stunt = Stunt.objects(parent_id=str(parent.id), name__icontains=name).first()
            stunts = [stunt] if stunt else []
        else:
            stunts = Stunt.objects(parent_id=str(parent.id)).all()
        return stunts

    def get_string(self, char):
        active = ' _(Active)_' if str(self.id) == char.active_stunt else ''
        description = f' - {self.description}' if self.description else ''
        return f'{self.name}{active}{description}'
        