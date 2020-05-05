# character_command.py
import datetime
from models import User, Character, Aspect
from config.setup import Setup

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
CHARACTER_HELP = SETUP.character_help

class CharacterCommand():
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'n'
        self.user = User().get_or_create(ctx.author.name, ctx.guild.name)
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None

    def run(self):
        switcher = {
            'help': self.help,
            'name': self.name,
            'n': self.name,
            'list': self.character_list,
            'l': self.character_list,
            'delete': self.delete_character,
            'd': self.delete_character,
            'description': self.description,
            'desc': self.description,
            'high': self.high_concept,
            'hc': self.high_concept,
            'trouble': self.trouble,
            't': self.trouble,
            'fate': self.fate,
            'f': self.fate,
            'aspect': self.aspect,
            'a': self.aspect,
            'boost': self.aspect,
            'b': self.aspect,
            'approach': self.approach,
            'app': self.approach,
            'skill': self.skill,
            'sk': self.skill,
            'stunt': self.stunt,
            's': self.stunt
        }
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: self.name)
            # Execute the function
            messages = func()
        else:
            self.args = ('n',) + self.args
            self.command = 'n'
            func = self.name
            # Execute the function
            messages = func()
        # Send messages
        return messages

    def help(self):
        return [CHARACTER_HELP]

    def name(self):
        if len(self.args) == 0:
            if not self.char:
                return ['No active character or name provided']
        else:
            char_name = ' '.join(self.args[1:])
            self.char = Character().get_or_create(self.user, char_name, self.ctx.guild.name)
            self.user.set_active_character(self.char)
        return [self.char.get_string(self.user)]

    def character_list(self):
        characters = Character().get_by_user(self.user)
        if len(characters) == 0:
            return ['You don\'t have any characters.\nTry this: ".d c n Name"']
        else:
            return [f'{c.get_short_string(self.user)}\n' for c in characters]

    def delete_character(self):
        if len(self.args) == 1:
            return ['No character provided for deletion']
        search = ' '.join(self.args[1:])
        self.char = Character().find(self.user, search, self.ctx.guild.name)
        if not self.char:
            return [f'{search} was not found. No changes made.\nTry this: ".d c n Name"']
        else:
            search = self.char.name
            [a.delete() for a in Aspect().get_by_parent_id(self.char.id)]
            self.char.delete()
            return [f'{search} removed']

    def description(self):
        if len(self.args) == 1:
            return ['No description provided']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        else:
            description = ' '.join(self.args[1:])
            self.char.description = description
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [
                f'Description updated to {description}',
                self.char.get_string_short(self.user)
            ]

    def high_concept(self):
        if len(self.args) == 2 or (len(self.args) == 1 and self.args[1].lower() != 'concept'):
            return ['No high concept provided']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        else:
            hc = ''
            if self.args[1].lower() == 'concept':
                hc = ' '.join(self.args[2:])
            else:
                hc = ' '.join(self.args[1:])
            self.char.high_concept = hc
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [
                f'High Concept updated to {hc}',
                self.char.get_string_short(self.user)
            ]

    def trouble(self):
        if len(self.args) == 1:
            return ['No trouble provided']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        else:
            trouble = ' '.join(self.args[1:])
            self.char.trouble = trouble
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [
                f'Trouble updated to {trouble}',
                self.char.get_short_string(self.user)
            ]

    def fate(self):
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        elif len(self.args) == 2 and (self.args[1] == 'refresh' or self.args[1] == 'r'):
            self.char.fate_points = self.char.refresh
        elif len(self.args) == 2 and self.args[1] == '+':
            self.char.fate_points += 1 if self.char.fate_points < 5 else 0
        elif len(self.args) == 2 and self.args[1] == '-':
            self.char.fate_points -= 1 if self.char.fate_points > 0 else 0
        if (not self.char.created):
            self.char.created = datetime.datetime.utcnow()
        self.char.updated = datetime.datetime.utcnow()
        self.char.save()
        return [f'Fate Points: {self.char.fate_points}']

    def aspect(self):
        if len(self.args) == 1:
            return ['No aspect provided']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name']
        elif self.args[1].lower() == 'list':
            aspects = Aspect().get_by_parent_id(self.char.id)
            return [self.char.get_string_aspects()]
        elif self.args[1].lower() == 'delete' or self.args[1].lower() == 'd':
            aspect = ' '.join(self.args[2:])
            [a.delete() for a in Aspect().get_by_parent_id(self.char.id, aspect)]
            aspects = ''.join([a.get_string() for a in Aspect().get_by_parent_id(self.char.id)])
            return [
                f'{aspect} removed from aspects',
                self.char.get_string_aspects()
            ]
        else:
            aspect = ' '.join(self.args[1:])
            Aspect().get_or_create(aspect, self.char.id)
            return [
                f'Added {aspect} to aspects',
                self.char.get_string_aspects()
            ]

    def approach(self):
        messages = []
        if self.args[1].lower() == 'help':
            app_str = '\n        '.join(APPROACHES)
            messages.append(f'**Approaches:**\n        {app_str}')
        elif len(self.args) != 3 and len(self.args) != 2:
            messages.append('Approach syntax: .d (app)roach {approach} {bonus}')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ".d c n Name"')
            else:
                if self.args[1].lower() == 'delete' or self.args[1].lower() == 'd':
                    skill = [s for s in APPROACHES if self.args[2][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else self.args[2]
                    if skill in self.char.skills:
                        new_skills = {}
                        for key in self.char.skills:
                            if key != skill:
                                new_skills[key] = self.char.skills[key]
                        self.char.skills = new_skills
                    if (not self.char.created):
                        self.char.created = datetime.datetime.utcnow()
                    self.char.updated = datetime.datetime.utcnow()
                    self.char.save()
                    messages.append(f'Removed {skill}') 
                else:
                    skill = [s for s in APPROACHES if self.args[1][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else self.args[1]
                    self.char.skills[skill] = self.args[2]
                    self.char.use_approaches = True
                    if (not self.char.created):
                        self.char.created = datetime.datetime.utcnow()
                    self.char.updated = datetime.datetime.utcnow()
                    self.char.save()
                    messages.append(f'Updated {skill} to {self.args[2]}')
                messages.append(self.char.get_string_skills())
        return messages

    def skill(self):
        messages = []
        if self.args[1].lower() == 'help':
            sk_str = '\n        '.join(SKILLS)
            messages.append(f'**Skills:**\n        {sk_str}')
        elif len(self.args) != 3 and len(self.args) != 2:
            messages.append('Skill syntax: .d (sk)ill {skill} {bonus}')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ".d c n Name"')
            else:
                if self.args[1].lower() == 'delete' or self.args[1].lower() == 'd':
                    skill = [s for s in SKILLS if self.args[2][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else self.args[2]
                    if skill in self.char.skills:
                        new_skills = {}
                        for key in self.char.skills:
                            if key != skill:
                                new_skills[key] = self.char.skills[key]
                        self.char.skills = new_skills
                    if (not self.char.created):
                        self.char.created = datetime.datetime.utcnow()
                    self.char.updated = datetime.datetime.utcnow()
                    self.char.save()
                    messages.append(f'Removed {skill} skill') 
                else:
                    skill = [s for s in SKILLS if self.args[1][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else self.args[1]
                    self.char.skills[skill] = self.args[2]
                    self.char.use_approaches = False
                    if (not self.char.created):
                        self.char.created = datetime.datetime.utcnow()
                    self.char.updated = datetime.datetime.utcnow()
                    self.char.save()
                    messages.append(f'Updated {skill} to {self.args[2]}')                
                messages.append(self.char.get_string_skills())
        return messages

    def stunt(self):
        messages = []
        if len(self.args) == 1:
            messages.append('No stunt provided')
        if not self.char:
            messages.append('You don\'t have an active character.\nTry this: ".d c n Name"')
        elif self.args[1].lower() == 'desc' or self.args[1].lower() == 'description':
            description = ' '.join(self.args[2:])
            stunt = f'{self.char.active_stunt} - {description}'
            self.char.stunts = [(f'{self.char.active_stunt} - {description}' if s.split(' - ')[0].lower() == self.char.active_stunt.lower() else s) for s in self.char.stunts]
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            messages.append(self.char.get_string_stunts())
        elif self.args[1].lower() == 'list':
            messages.append(self.char.get_string_stunts())
        elif self.args[1].lower() == 'delete' or self.args[1].lower() == 'd':
            stunt = ' '.join(self.args[2:])
            [self.char.stunts.remove(s) for s in self.char.stunts if stunt.lower() in s.split(' - ')[0].lower()]
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            messages.append(f'{stunt} removed from stunts')
            messages.append(self.char.get_string_stunts())
        else:
            stunt = ' '.join(self.args[1:])
            match = [s for s in self.char.stunts if s.split(' - ')[0].lower() == stunt.lower()]
            if match:
                self.char.active_stunt = stunt
                if (not self.char.created):
                    self.char.created = datetime.datetime.utcnow()
                self.char.updated = datetime.datetime.utcnow()
                self.char.save()
                messages.append(f'{self.char.name} already has that stunt')
            else:
                self.char.stunts.append(stunt)
                self.char.active_stunt = stunt
                if (not self.char.created):
                    self.char.created = datetime.datetime.utcnow()
                self.char.updated = datetime.datetime.utcnow()
                self.char.save()
                messages.append(f'Added {stunt} to stunts')
                messages.append(self.char.get_string_stunts())
        return messages
