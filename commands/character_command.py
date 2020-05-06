# character_command.py
import datetime
import copy
from models import User, Character, Aspect, Stunt
from config.setup import Setup

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
CHARACTER_HELP = SETUP.character_help
X = SETUP.x
O = SETUP.o
STRESS = SETUP.stress
CONSEQUENCES = SETUP.consequences
CONSEQUENCE_SHIFTS = SETUP.consequence_shifts

class CharacterCommand():
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args[1:]
        self.command = self.args[0].lower() if len(self.args) > 0 else 'n'
        self.user = User().get_or_create(ctx.author.name, ctx.guild.name)
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None
        self.asp = Aspect().get_by_id(self.char.active_aspect) if self.char and self.char.active_aspect else None
        self.stu = Stunt().get_by_id(self.char.active_stunt) if self.char and self.char.active_stunt else None

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
            's': self.stunt,
            'stress': self.stress,
            'st': self.stress,
            'consequence': self.consequence,
            'con': self.consequence
        }
        # Get the function from switcher dictionary
        if self.command in switcher:
            func = switcher.get(self.command, lambda: self.name)
            # Execute the function
            messages = func(self.args)
        else:
            self.args = ('n',) + self.args
            self.command = 'n'
            func = self.name
            # Execute the function
            messages = func(self.args)
        # Send messages
        return messages

    def help(self, args):
        return [CHARACTER_HELP]

    def name(self, args):
        if len(args) == 0:
            if not self.char:
                return ['No active character or name provided']
        else:
            char_name = ' '.join(args[1:])
            self.char = Character().get_or_create(self.user, char_name, self.ctx.guild.name)
            self.user.set_active_character(self.char)
        return [self.char.get_string(self.user)]

    def character_list(self, args):
        characters = Character().get_by_user(self.user)
        if len(characters) == 0:
            return ['You don\'t have any characters.\nTry this: ".d c n Name"']
        else:
            return [f'{c.get_short_string(self.user)}\n' for c in characters]

    def delete_character(self, args):
        if len(args) == 1:
            return ['No character provided for deletion']
        search = ' '.join(args[1:])
        self.char = Character().find(self.user, search, self.ctx.guild.name)
        if not self.char:
            return [f'{search} was not found. No changes made.\nTry this: ".d c n Name"']
        else:
            search = self.char.name
            [a.delete() for a in Aspect().get_by_parent_id(self.char.id)]
            [s.delete() for s in Stunt().get_by_parent_id(self.char.id)]
            self.char.delete()
            return [f'{search} removed']

    def description(self, args):
        if len(args) == 1:
            return ['No description provided']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        else:
            description = ' '.join(args[1:])
            self.char.description = description
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [
                f'Description updated to {description}',
                self.char.get_string_short(self.user)
            ]

    def high_concept(self, args):
        if len(args) == 2 or (len(args) == 1 and args[1].lower() != 'concept'):
            return ['No high concept provided']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        else:
            hc = ''
            if args[1].lower() == 'concept':
                hc = ' '.join(args[2:])
            else:
                hc = ' '.join(args[1:])
            self.char.high_concept = hc
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [
                f'High Concept updated to {hc}',
                self.char.get_string_short(self.user)
            ]

    def trouble(self, args):
        if len(args) == 1:
            return ['No trouble provided']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        else:
            trouble = ' '.join(args[1:])
            self.char.trouble = trouble
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [
                f'Trouble updated to {trouble}',
                self.char.get_short_string(self.user)
            ]

    def fate(self, args):
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        elif len(args) == 2 and (args[1] == 'refresh' or args[1] == 'r'):
            self.char.fate_points = self.char.refresh
        elif len(args) == 2 and args[1] == '+':
            self.char.fate_points += 1 if self.char.fate_points < 5 else 0
        elif len(args) == 2 and args[1] == '-':
            self.char.fate_points -= 1 if self.char.fate_points > 0 else 0
        if (not self.char.created):
            self.char.created = datetime.datetime.utcnow()
        self.char.updated = datetime.datetime.utcnow()
        self.char.save()
        return [f'Fate Points: {self.char.fate_points}']

    def aspect(self, args):
        if len(args) == 1:
            if not self.asp:
                return ['You don\'t have an active aspect.\nTry this: ".d c a {aspect}"']
            return [f'{self.asp.get_string(self.char)}']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name"']
        elif args[1].lower() == 'list':
            return [self.char.get_string_aspects()]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            aspect = ' '.join(args[2:])
            [a.delete() for a in Aspect().get_by_parent_id(self.char.id, aspect)]
            return [
                f'"{aspect}" removed from aspects',
                self.char.get_string_aspects()
            ]
        elif args[1].lower() == 'desc' or args[1].lower() == 'description':
            description = ' '.join(args[2:])
            self.asp.description = description
            if (not self.asp.created):
                self.asp.created = datetime.datetime.utcnow()
            self.asp.updated = datetime.datetime.utcnow()
            self.asp.save()
            messages.append(self.char.get_string_aspects())
        else:
            aspect = ' '.join(args[1:])
            self.asp = Aspect().get_or_create(aspect, self.char.id)
            self.char.active_aspect = str(self.asp.id)
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [self.char.get_string_aspects()]

    def approach(self, args):
        messages = []
        if args[1].lower() == 'help':
            app_str = '\n        '.join(APPROACHES)
            messages.append(f'**Approaches:**\n        {app_str}')
        elif len(args) != 3 and len(args) != 2:
            messages.append('Approach syntax: .d (app)roach {approach} {bonus}')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ".d c n Name"')
            else:
                if args[1].lower() == 'delete' or args[1].lower() == 'd':
                    skill = [s for s in APPROACHES if args[2][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else args[2]
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
                    skill = [s for s in APPROACHES if args[1][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else args[1]
                    self.char.skills[skill] = args[2]
                    self.char.use_approaches = True
                    if (not self.char.created):
                        self.char.created = datetime.datetime.utcnow()
                    self.char.updated = datetime.datetime.utcnow()
                    self.char.save()
                    messages.append(f'Updated {skill} to {args[2]}')
                messages.append(self.char.get_string_skills())
        return messages

    def skill(self, args):
        messages = []
        if args[1].lower() == 'help':
            sk_str = '\n        '.join(SKILLS)
            messages.append(f'**Skills:**\n        {sk_str}')
        elif len(args) != 3 and len(args) != 2:
            messages.append('Skill syntax: .d (sk)ill {skill} {bonus}')
        else:
            if not self.char:
                messages.append('You don\'t have an active character.\nTry this: ".d c n Name"')
            else:
                if args[1].lower() == 'delete' or args[1].lower() == 'd':
                    skill = [s for s in SKILLS if args[2][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else args[2]
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
                    skill = [s for s in SKILLS if args[1][0:2].lower() == s[0:2].lower()]
                    skill = skill[0].split(' - ')[0] if skill else args[1]
                    self.char.skills[skill] = args[2]
                    self.char.use_approaches = False
                    if (not self.char.created):
                        self.char.created = datetime.datetime.utcnow()
                    self.char.updated = datetime.datetime.utcnow()
                    self.char.save()
                    messages.append(f'Updated {skill} to {args[2]}')                
                messages.append(self.char.get_string_skills())
        return messages

    def stunt(self, args):
        messages = []
        if len(args) == 1:
            if not self.stu:
                return ['You don\'t have an active stunt.\nTry this: ".d c s {stunt}"']
            return [f'{self.stu.get_string(self.char)}']
        if not self.char:
            return ['You don\'t have an active character.\nTry this: ".d c n Name']
        elif args[1].lower() == 'list':
            return [self.char.get_string_stunts()]
        elif args[1].lower() == 'delete' or args[1].lower() == 'd':
            stunt = ' '.join(args[2:])
            [s.delete() for s in Stunt().get_by_parent_id(self.char.id, stunt)]
            return [
                f'"{stunt}" removed from stunts',
                self.char.get_string_stunts()
            ]
        elif args[1].lower() == 'desc' or args[1].lower() == 'description':
            description = ' '.join(args[2:])
            self.stu.description = description
            if (not self.stu.created):
                self.stu.created = datetime.datetime.utcnow()
            self.stu.updated = datetime.datetime.utcnow()
            self.stu.save()
            messages.append(self.char.get_string_stunts())
        else:
            stunt = ' '.join(args[1:])
            self.stu = Stunt().get_or_create(stunt, self.char.id)
            self.char.active_stunt = str(self.stu.id)
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            return [self.char.get_string_stunts()]
        return messages
    
    def get_available_stress(self, stress_type):
        return sum([1 for s in self.char.stress[stress_type] if s[1] == O])

    def stress(self, args):
        messages = []
        modified = None
        if len(args) == 1:
            messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_stress()}')
            return messages
        if args[1] in ['delete', 'd']:
            if len(args) == 2:
                messages.append('No stress type provided - (m)mental or (p)hysical')
                return messages
            if len(args) == 3:
                if args[2].lower() not in ['m', 'mental', 'p', 'physical']:
                    messages.append(f'{args[2].lower()} is not a valid stress type - (m)mental or (p)hysical')
                messages.append('Missing stress shift number - 1,2,3')
                return messages
            if len(args) == 4:
                shift = args[3]
                if not shift.isdigit():
                    return messages.append('Stress shift must be a positive integer')
                shift_int = int(shift)
                stress_type_str = args[2].lower()
                stress_type = 1 if stress_type_str in ['m', 'mental'] else 0
                stress_type_name = STRESS[stress_type]
                available = self.get_available_stress(stress_type)
                if available == 3:
                    messages.append(f'***{self.char.name}*** has no _{stress_type_name}_ stress to remove')
                    return messages
                modified = copy.deepcopy(self.char.stress)
                for s in range(len(self.char.stress[stress_type])-1,-1,-1):
                    if shift_int > 0 and self.char.stress[stress_type][s][1] == X:
                        shift_int -= 1
                        modified[stress_type][s][1] = O
                messages.append(f'Removed {shift} of ***{self.char.name}\'s*** _{stress_type_name}_ stress')
        else:
            if len(args) == 2:
                if args[1].lower() not in ['m', 'mental', 'p', 'physical']:
                    messages.append(f'{args[1].lower()} is not a valid stress type - (m)mental or (p)hysical')
                messages.append('Missing stress shift number - 1,2,3')
                return messages
            shift = args[2]
            if not shift.isdigit():
                return messages.append('Stress shift must be a positive integer')
            stress_type_str = args[1].lower()
            stress_type = 1 if stress_type_str in ['m', 'mental'] else 0
            stress_type_name = STRESS[stress_type]
            shift_int = int(shift)
            available = self.get_available_stress(stress_type)
            if shift_int > available:
                messages.append(f'***{self.char.name}*** cannot absorb {shift} {stress_type_name} stress ({available} available)')
                return messages
            modified = copy.deepcopy(self.char.stress)
            for s in range(0,len(self.char.stress[stress_type])):
                if shift_int > 0 and self.char.stress[stress_type][s][1] == O:
                    shift_int -= 1
                    modified[stress_type][s][1] = X
            messages.append(f'***{self.char.name}*** absorbed {shift} {stress_type_name} stress')
        if modified:
            self.char.stress = modified
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            messages.append(f'{self.char.get_string_stress()}')
        return messages

    def consequence(self, args):
        messages = []
        modified = None
        if len(args) == 1:
            messages.append(f'{self.char.get_string_name(self.user)}{self.char.get_string_consequences()}')
            return messages
        if args[1] in ['delete', 'd']:
            if len(args) == 2:
                messages.append('No severity provided - (mi)ld, (mo)oderate or (s)evere')
                if args[2].lower() not in ['mi', 'mild', 'mo', 'moderate', 's', 'severe']:
                    messages.append(f'{args[2].lower()} is not a valid severity - (mi)ld, (mo)oderate or (s)evere')
                return messages
            severity_str = args[2].lower()
            severity = 1 if severity_str in ['mo', 'moderate'] else (0 if severity_str in ['mi', 'mild'] else 2)
            severity_shift = CONSEQUENCE_SHIFTS[severity]
            severity_name = CONSEQUENCES[severity]
            if self.char.consequences[severity][1] == O:
                messages.append(f'***{self.char.name}*** does not currently have a _{severity_name}_ consequence')
                return messages
            previous = copy.deepcopy(self.char.consequences)
            modified = copy.deepcopy(self.char.consequences)
            modified[severity] = [severity_shift, O]
            messages.append(f'Removed ***{self.char.name}\'s*** _{severity_name}_ consequence ("{previous[severity][2]}")')
            messages.extend(self.aspect(['a', 'd', previous[severity][2]]))
        else:
            if len(args) == 2:
                if args[1].lower() not in ['mi', 'mild', 'mo', 'moderate', 's', 'severe']:
                    messages.append(f'{args[1].lower()} is not a valid severity - (mi)ld, (mo)oderate or (s)evere')
                messages.append('Missing consequence aspect')
                return messages
            severity_str = args[1].lower()
            severity = 1 if severity_str in ['mo', 'moderate'] else (0 if severity_str in ['mi', 'mild'] else 2)
            severity_shift = CONSEQUENCE_SHIFTS[severity]
            severity_name = CONSEQUENCES[severity]
            if self.char.consequences[severity][1] == X:
                messages.append(f'***{self.char.name}*** already has a _{severity_name}_ consequence ("{self.char.consequences[severity][2]}")')
                return messages
            aspect = ' '.join(args[2:])
            modified = copy.deepcopy(self.char.consequences)
            modified[severity] = [severity_shift, X, aspect]
            messages.append(f'***{self.char.name}*** absorbed {severity_shift} shift for a {severity_name} consequence')
            messages.extend(self.aspect(['a', aspect]))
        if modified:
            self.char.consequences = modified
            if (not self.char.created):
                self.char.created = datetime.datetime.utcnow()
            self.char.updated = datetime.datetime.utcnow()
            self.char.save()
            messages.append(f'{self.char.get_string_consequences()}')
        return messages