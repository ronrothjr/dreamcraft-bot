# roll_command.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import traceback
import random
import copy
from bson.objectid import ObjectId
from models import Channel, Scenario, Scene, Zone, Engagement, Exchange, User, Character
from commands import CharacterCommand, SceneCommand, ZoneCommand
from services import EngagementService, ExchangeService, CharacterService, SceneService
from config.setup import Setup
from utils import T
import inflect
p = inflect.engine()

engagement_svc = EngagementService()
exchange_svc = ExchangeService()
char_svc = CharacterService()
scene_svc = SceneService()
SETUP = Setup()
ROLL_HELP = SETUP.roll_help
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
FATE_DICE = SETUP.fate_dice
LADDER = SETUP.fate_ladder

class RollCommand():
    """
    Handle 'roll', 'r' commands and subcommands

    Subcommands:
        help - display a set of instructions on RollCommand usage
        roll, r - roll fate dice with approach/skill and invoke/compel options
        reroll, re - reroll a previous roll with additional invoke/compel options
        attack, att - attack another roll within a scene and roll
        defend, def - defend from an attack by another roll within the scene and roll
        takeout, out - forcibly remove a character from an engagement
        boost - claim a boost after rolling a tie, succeed, or succeed with style
        available, avail, av - display a list of available aspects and stunts to invoke
    """

    def __init__(self, parent, ctx, args, guild, user=None, channel=None, char=None):
        """
        Command handler for roll command

        Parameters
        ----------
        parent : DreamcraftHandler
            The handler for Dreamcraft Bot commands and subcommands
        ctx : object(Context)
            The Discord.Context object used to retrieve and send information to Discord users
        args : array(str)
            The arguments sent to the bot to parse and evaluate
        guild : Guild
            The guild object containing information about the server issuing commands
        user : User, optional
            The user database object containing information about the user's current setttings, and dialogs
        channel : Channel, optional
            The channel from which commands were issued
        char : Character, optional
            The database roll object 

        Returns
        -------
        RollCommand - object for processing roll commands and subcommands
        """
    
        self.parent = parent
        self.ctx = ctx
        self.command = args[0].lower()
        self.args = args[1:]
        self.guild = guild
        self.user = user
        self.channel = channel
        self.invoke_index = [i for i in range(0, len(self.args)) if self.args[i] in ['invoke', 'i']]
        self.compel_index = [i for i in range(0, len(self.args)) if self.args[i] in ['compel', 'c']]
        self.scenario = Scenario().get_by_id(self.channel.active_scenario) if self.channel and self.channel.active_scenario else None
        self.sc = Scene().get_by_id(self.channel.active_scene) if self.channel and self.channel.active_scene else None
        self.engagement = Engagement().get_by_id(self.channel.active_engagement) if self.channel and self.channel.active_engagement else None
        self.exchange = Exchange().get_by_id(self.engagement.active_exchange) if self.engagement and self.engagement.active_exchange else None
        self.zone = Zone().get_by_id(self.channel.active_zone) if self.channel and self.channel.active_zone else None
        self.char = Character().get_by_id(self.user.active_character) if self.user and self.user.active_character else None
        self.target = Character().get_by_id(self.char.active_target) if self.char and self.char.active_target else None
        self.targeted_by = Character().get_by_id(self.char.active_target_by) if self.char and self.char.active_target_by else None
        self.skill = ''
        self.messages = []
        self.invokes = []
        self.compels = []
        self.errors = []
        self.invokes_cost = 0

    def run(self):
        """
        Execute the channel commands by validating and finding their respective methods

        Returns
        -------
        list(str) - a list of messages in response the command validation and execution
        """

        try:
            # List of subcommands mapped the command methods
            switcher = {
                'help': self.help,
                'roll': self.roll,
                'r': self.roll,
                'reroll': self.roll,
                're': self.roll,
                'attack': self.attack,
                'att': self.attack,
                'defend': self.defend,
                'def': self.defend,
                'boost': self.boost,
                'takeout': self.takeout,
                'out': self.takeout,
                'available': self.show_available,
                'avail': self.show_available,
                'av': self.show_available
            }
            # Get the function from switcher dictionary
            if self.command in switcher:
                func = switcher.get(self.command, lambda: self.roll)
                # Execute the function
                messages = func()
            else:
                messages = [f'Unknown command: {self.command}']
            # Send messages
            return messages
        except Exception as err:
            traceback.print_exc()
            # Log every error
            engagement_svc.log(
                str(self.char.id) if self.char else str(self.user.id),
                self.char.name if self.char else self.user.name,
                str(self.user.id),
                self.guild.name,
                'Error',
                {
                    'command': self.command,
                    'args': self.args,
                    'traceback': traceback.format_exc()
                }, 'created')
            return list(err.args)

    def help(self):
        """Returns the help text for the command"""
        return [ROLL_HELP]

    # Show available aspects and stunts to invoke
    def show_available(self):
        """Display all available aspects and stunts for characters within the active scenario, scene, and zone
        
        Returns
        -------
        list(str) - the response messages string array
        """

        self.get_available_invokes()
        self.available_invokes = []
        [self.available_invokes.extend(a['char'].get_available_aspects(a['parent'], self.char)) for a in self.available]
        if self.available_invokes:
            return ['**Available invokes:**\n        ' + '\n        '.join([a for a in self.available_invokes])]
        else:
            return ['No available aspects to invoke']

    def conflict_check(self):
        """Add messages indicating if a conflict or engagement has been started
        
        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        is_conflict = self.engagement and self.engagement.type_name != 'Conflict'
        if not self.engagement or not is_conflict:
            messages.append('"There is no conflict." -_Darth Vader in **Return of the Jedi**_')
        if self.engagement and self.engagement.characters:
            if str(self.char.id) not in self.engagement.characters and str(self.char.id) not in self.engagement.opposition:
                messages.append(f'***{self.char.name}*** is not in a conflict. Sure you wanna pick a fight?')
        return messages

    def add_chars_to_engagement(self):
        """If there is an engagement started, add characters being attacked or defending

        Returns
        -------
        list(str) - the response messages string array
        """

        messages = []
        if self.engagement:
            is_char_opposed = self.user.role == 'Game Master'
            # If no engagement started for this engagement, start one now between the attacker and the defender
            if is_char_opposed:
                if str(self.char.id) not in self.engagement.opposition:
                    self.engagement.opposition.append(str(self.char.id))
                    messages.append(f'Added ***{self.char.name}*** to _{self.engagement.name}_ engagement opposition')
                if str(self.target.id) not in self.engagement.characters:
                    self.engagement.characters.append(str(self.target.id))
                    messages.append(f'Added ***{self.target.name}*** to _{self.engagement.name}_ engagement characters')
                    engagement_svc.save(self.engagement, self.user)
            else:
                if str(self.target.id) not in self.engagement.opposition:
                    self.engagement.opposition.append(str(self.target.id))
                    messages.append(f'Added ***{self.target.name}*** to _{self.engagement.name}_ engagement opposition')
                if str(self.char.id) not in self.engagement.characters:
                    self.engagement.characters.append(str(self.char.id))
                    messages.append(f'Added ***{self.char.target}*** to _{self.engagement.name}_ engagement characters')
                    engagement_svc.save(self.engagement, self.user)
        return messages

    def check_unresolved_actions(self):
        """If there are any unresolved actions and warn of them"""
        messages = []
        characters = []
        if self.engagement and self.engagement.characters:
            characters.extend(self.engagement.characters)
        if self.engagement and self.engagement.opposition:
            characters.extend(self.engagement.opposition)
        if characters:
            attackers = list(Character().filter(id__in=characters, active_action='Attack').all())
            for a in attackers:
                if a.last_roll and a.last_roll['shifts'] and a.last_roll['shifts_remaining']:
                    target = Character().get_by_id(a.active_target)
                    shifts_remaining = a.last_roll['shifts_remaining']
                    messages.append('\n'.join([
                        f'***{self.char.name}*** cannot attack.',
                        f'{self.get_attack_text(a, target)} with {p.no("shift", shifts_remaining)} left to absorb.'
                    ]))
        if messages:
            raise Exception('\n\n'.join(messages))

    def attack(self):
        """Execute the attack subcommand to target another character and roll for attack
        
        Returns
        -------
        list(str) - the response messages string array
        """

        self.check_unresolved_actions()
        messages = self.conflict_check()
        self
        if len(self.args) == 0:
            raise Exception('No target identified for your attack action')
        search = self.args[0]
        if self.engagement and self.engagement.characters:
            chars = list(Character().filter(id__in=[c for c in self.engagement.characters]).all())
        else:
            chars = list(Character().filter(id__in=[c for c in self.sc.characters]).all())
        targets = [c for c in chars if search.lower() in c.name.lower()]
        if not targets:
            raise Exception(f'No target match for _{search}_ found in the ***{self.sc.name}*** scene.')
        if len(targets) > 1:
            names = '\n        '.join([f'***{m.name}***' for m in targets])
            raise Exception(f'Multiple targets matched _{search}_ in the ***{self.sc.name}*** scene. Please specify which:{names}')
        self.target = targets[0]
        self.target.active_target_by = str(self.char.id)
        self.save_char(self.target)
        self.char.active_action = 'Attack'
        self.char.active_target = str(self.target.id)
        self.save_char(self.char)
        messages.extend(self.add_chars_to_engagement())
        self.command = 'roll'
        # Allow for exact roll designation
        if self.args[1] == 'exact' and len(self.args) > 2:
            exact_roll = self.args[2]
            self.args = self.args[3:] if len(self.args) > 3 else tuple()
            self.invoke_index = [i for i in range(0, len(self.args)) if self.args[i] in ['invoke', 'i']]
            self.compel_index = [i for i in range(0, len(self.args)) if self.args[i] in ['compel', 'c']]
            roll_str = self.roll(exact_roll)
        else:
            self.args = self.args[1:]
            roll_str = self.roll()
        messages.extend(roll_str)
        return messages

    def defend(self):
        """Execute the defend subcommand in response to an attack and roll for defense
        
        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.targeted_by:
            raise Exception('You are not currently the target of any attacks.')
        messages = self.conflict_check()
        self.char.active_action = 'Defend'
        self.save_char(self.char)
        self.command = 'roll'
        # Allow for exact roll designation
        if len(self.args) > 1 and self.args[0] == 'exact':
            exact_roll = self.args[1]
            self.args = self.args[2:] if len(self.args) > 2 else tuple()
            self.invoke_index = [i for i in range(0, len(self.args)) if self.args[i] in ['invoke', 'i']]
            self.compel_index = [i for i in range(0, len(self.args)) if self.args[i] in ['compel', 'c']]
            roll_str = self.roll(exact_roll)
        else:
            roll_str = self.roll()
        messages.extend(roll_str)
        return messages

    def boost(self):
        """Claim a boost generated by an attack, create advantage, or overcome roll"""

        if not self.char:
            raise Exception('No active character. Try this to create/select one: ```css\n.d c CHARACTER_NAME```')
        if not self.char.last_roll:
            raise Exception('You have not rolled. There is no boost to claim.')
        if not self.char.active_action:
            raise Exception('You have not taken any action. Try one of these:```\n.d attack "OPPONENT_NAME" "SKILL_NAME"```')
        if 'outcome' not in self.char.last_roll:
            raise Exception(f'The outcome of your \'{self.char.active_action}\' has not yet been determined.')
        if self.char.active_action == 'Attack' and self.char.last_roll['outcome'] in ['Tie', 'Succeed with Style']:
            outcome = self.char.last_roll['outcome']
            if not self.args:
                raise Exception(f'No name given to claim the boost from \'{outcome}\'.```css\n.d boost "BOOST_NAME"```')
            cmd = CharacterCommand(self.parent, self.ctx, ('c', 'aspect', 'boost', ' '.join(self.args)), self.guild, self.user, self.channel, self.char)
            self.messages.extend(cmd.run())

            # Add boost from 'Tie' and resolve the action
            if outcome == 'Tie':
                if self.target and self.target.active_action == 'Defend':
                    self.target.active_action = ''
                    self.char.active_target_by = ''
                    char_svc.save(self.target, self.user)
                self.char.active_action = ''
                self.char.active_target = ''
                char_svc.save(self.char, self.user)
                self.messages.append(f'Attack from ***{self.char.name}*** has been resolved.')

            # Add boost from 'Succeed with Style' and decrement the shifts_remaining
            if outcome == 'Succeed with Style':
                last_roll = copy.deepcopy(self.char.last_roll)
                if 'boost_claimed' in last_roll:
                    raise Exception(f'The boost has already been claimed from \'{outcome}\'.')
                if last_roll['shifts_remaining'] < 3:
                    raise Exception(f'You do not have enough shifts to claim the boost from \'{outcome}\'.')
                shifts_remaining = last_roll['shifts_remaining'] - 1
                last_roll['shifts_remaining'] = shifts_remaining
                last_roll['boost_claimed'] = True
                self.char.last_roll = last_roll
                char_svc.save(self.char, self.user)
                self.messages.append(f'{p.no("shift", shifts_remaining)} left to absorb.')
        return self.messages

    def takeout(self):
        """Forcibly remove a character from a conflict

        Returns
        -------
        list(str) - the response messages string array
        """

        if not self.char:
            raise Exception('No active character. Try this to create/select one: ```css\n.d c CHARACTER_NAME```')
        if not self.targeted_by:
            raise Exception(f'***{self.char}*** is not being targeted in an attack.')
        if self.targeted_by.last_roll and self.targeted_by.last_roll['shifts_remaining'] == 0:
            raise Exception(f'***{self.char.name}*** will not be taken out because there are no shifts remaining.')
        self.messages.append(f'***{self.char.name}*** was taken out.')
        cmd = SceneCommand(self.parent, self.ctx, ('s', 'exit'), self.guild, self.user, self.channel)
        self.messages.extend(cmd.run())
        if self.char and self.char.active_action == 'Defend':
            self.char.active_action = ''
            self.char.active_target_by = ''
            char_svc.save(self.char, self.user)
        self.targeted_by.active_action = ''
        self.targeted_by.active_target = ''
        char_svc.save(self.targeted_by, self.user)
        self.messages.append(f'Attack from ***{self.targeted_by.name}*** has been resolved.')
        return self.messages

    def roll(self, exact_roll=None):
        """Roll the Dreamcreaft Bot Fate dice and process all subcommands
        
        Paramenters
        -----------
        exact_roll : str
            The string representation of the exact roll to replace the dice

        Returns
        -------
        list(str) - the response messages string array
        """

        self.skill = self.args[0] if len(self.args) > 0 and self.args[0].lower() not in ['i','invoke','c','compel'] else ''
        if len(self.args) > 0 and self.args[0].lower() in ['help','h']:
            return self.help()
        if not self.char:
            raise Exception('No active character. Try this to create/select one: ```css\n.d c CHARACTER_NAME```')
        self.messages = [self.char.get_string_name(self.user)]
        self.last_roll = None
        # parse skill from args
        self.get_skill()

        # Find and validate invokes and compels
        self.validate()
        if self.errors:
            raise Exception(*[e.error for e in self.errors])

        # Execute the roll command and apply fate point cost
        if self.command in ['roll', 'r']:
            self.roll_invokes = copy.deepcopy(self.invokes)
            self.last_roll = self.roll_next(exact_roll)
            self.char.last_roll = self.last_roll
            self.invokes_cost = sum([invoke['fate_points'] for invoke in self.invokes])
            self.messages.append(self.char.last_roll['roll_text'])

        # Execute the re-roll command to apply additional invokes
        elif self.command in ['reroll', 're']:
            # Re-rolling requires invokes. If there are none, return an error
            if not self.invokes:
                raise Exception('You did not include an invoke for the reroll')
            else:
                # Calculate fate point cost from invokes
                self.invokes_cost = sum([invoke['fate_points'] for invoke in self.invokes])
                self.last_roll = self.reroll()
                self.char.last_roll = self.last_roll
                self.messages.append(self.char.last_roll['roll_text'])

        # Resolve the invokes against their targets
        if self.invokes:
            self.resolve_invokes()

        # Resolve the compels against their targets
        if self.compels:
            self.handle_compels()

        # Resolve attack action
        if self.char.active_action == 'Attack':
            self.resolve_attack()

        # Resolve defend action
        if self.char.active_action == 'Defend':
            self.resolve_defend()

        self.save_char(self.char)

        return self.messages

    def save_char(self, char):
        """Save the Character database object"""

        char.updated_by = str(self.user.id)
        char.updated = T.now()
        char.save()

    # determine skill to validate
    def get_skill(self):
        """Get the skill being rolled if one was included in the roll command"""

        if self.command in ['reroll', 're']:
            self.skill = self.char.last_roll['skill']
        elif not self.invoke_index or (self.invoke_index and self.invoke_index[0] > 1):
            self.skill = self.match_skill()

    def validate(self):
        """Get validate invokes and compels, raise Exceptions where necessary"""

        self.get_invokes()
        self.errors.extend([i['error'] for i in self.invokes if i['aspect_name'] == 'error'])
        if self.errors:
            raise Exception(*self.errors)
        self.get_compels()
        self.errors.extend([c['error'] for c in self.compels if c['aspect_name'] == 'error'])
        if self.errors:
            raise Exception(*self.errors)
        if self.invoke_index and self.compel_index:
            raise Exception('You cannot invoke and compel on the same roll')

    def resolve_invokes(self):
        """Apply the fate point cost and stress absorbed from invokes"""

        char = self.get_parent_with_refresh(self.char)
        if char and self.invokes_cost >= char.fate_points + self.invokes_cost:
            raise Exception(f'***{char.name}*** does not have enough fate points')
        else:
            # Apply any fate point cost of invokes
            char.fate_points -= self.invokes_cost
            # Absorb any stress as cost of invokes
            for invoke in self.invokes:
                if invoke['stress_titles']:
                    for i in range(0, len(invoke['stress_titles'])):
                        self.absorb_invoke_stress(invoke['stress_titles'][i], invoke['stress'][i][0][0], invoke['stress_targets'][i])
                # Remove invoked boost aspect
                if invoke['is_boost']:
                    cmd = CharacterCommand(self.parent, self.ctx, ('c', 'aspect', 'delete', invoke['aspect_name']), self.guild, self.user, self.channel, self.char)
                    self.messages.extend(cmd.run())
            self.messages.append(self.char.get_string_fate())

    def absorb_invoke_stress(self, title, stress, target):
        """Apply the stress from invoking stunts
        
        Parameters
        ----------
        title : str
            The title of the stress being absorbed
        stress : str
            The number of shifts being absorbed
        target : Character
            Character database object to apply stress
        """

        # Apply stress to the targets identified during stress validation
        command = CharacterCommand(**{
            'parent': self.parent,
            'ctx': self.ctx,
            'args': self.args,
            'guild': self.guild,
            'user': self.user,
            'channel': self.channel,
            'char': target
        })
        stress_messages = command.stress(('stress', title, stress))
        if 'cannot absorb' in ''.join(stress_messages):
            raise Exception(*stress_messages)
        self.messages.extend(stress_messages)

    def get_attack_text(self, char, target):
        """Get the display text for an attack"""

        attack_roll = char.last_roll['final_roll']
        attack_roll_cleaned = str(attack_roll).replace('-','')
        attack_roll_ladder = f'b{attack_roll_cleaned}' if '-' in str(attack_roll) else f'a{str(attack_roll)}'
        attack_roll_str = attack_roll_ladder.replace('a','+').replace('b','-')
        ladder_text = LADDER[attack_roll_ladder]
        return f'***{target.name}*** faces {p.an(ladder_text)} ({attack_roll_str}) attack from ***{char.name}***'

    def resolve_attack(self):
        """Apply the attack action results and add it to the roll message response"""

        if self.target:
            self.messages.append(self.get_attack_text(self.char, self.target))

    def resolve_defend(self):
        """Apply the defend action results and add it to the roll message response"""

        if self.targeted_by and self.targeted_by.last_roll:
            defense_roll = self.last_roll['final_roll']
            defense_roll_cleaned = str(defense_roll).replace('-','')
            defense_roll_ladder = f'b{defense_roll_cleaned}' if '-' in str(defense_roll) else f'a{str(defense_roll)}'
            defense_roll_str = defense_roll_ladder.replace('a','+').replace('b','-')
            ladder_text = LADDER[defense_roll_ladder]
            self.targeted_by.last_roll['defense_roll'] = defense_roll
            shifts = self.targeted_by.last_roll['final_roll'] - defense_roll
            shifts_remaining = shifts if shifts > 0 else 0
            self.messages.append(f'... offering {p.an(ladder_text)} ({defense_roll_str}) defense leaving {shifts_remaining} shifts to absorb.')
            last_roll = copy.deepcopy(self.targeted_by.last_roll)
            last_roll['shifts'] = shifts
            last_roll['shifts_remaining'] = shifts_remaining
            if shifts > 2:
                last_roll['outcome'] = 'Succeed with Style'
                self.messages.append('\n'.join([
                    f'... allowing ***{self.targeted_by.name}*** the option to take a boost in exchange for one shift:```',
                    f'.d boost NAME_OF_BOOST_ASPECT```'
                ]))
            elif shifts > 0:
                last_roll['outcome'] = 'Succeed'
            elif shifts == 0:
                last_roll['outcome'] = 'Tie'
            else:
                last_roll['outcome'] = 'Fail'
            self.targeted_by.last_roll = last_roll
            char_svc.save(self.targeted_by, self.user)

    def handle_compels(self):
        """Apply the compels stored for processing"""

        if len(self.compels) + self.char.fate_points <= 5:
            self.char.fate_points += len(self.compels)
            self.messages.append(''.join([f'Compelled "{c}" and added 1 fate point' for c in self.compels]))
            self.messages.append(self.char.get_string_fate())
        else:
            raise Exception(f'{self.char.name} already has the maximum fate points (5)')

    def get_invokes(self):
        """Store the list of invokes passed in as command arguments"""

        self.re = self.command in ['reroll', 're']
        stress_targets = []
        for i in self.invoke_index:
            if len(self.args) < i+1 or self.skill and len(self.args) < i+2:
                self.invokes.append({'aspect_name': 'error', 'error': f'An invoke is missing an aspect'})
                continue
            search = self.args[i+1]
            aspect_name = ''
            category = ''
            skills = []
            aspect = None
            is_boost = False
            fate_points = None
            asp = self.find_aspect(search)
            if asp:
                aspect = asp['char']
                category = asp['category']
                if category in ['High Concept', 'Trouble']:
                    aspect_name = getattr(aspect, category.lower().replace(' ','_'))
                    skills = []
                    fate_points = 0 if category == 'Stunt' else 1
                    stress = []
                    stress_titles = []
                else:
                    aspect_name = aspect.name
                    is_boost = True if aspect.is_boost else False
                    skills = aspect.skills if aspect.skills else []
                    if aspect.fate_points is not None:
                        fate_points = aspect.fate_points
                    else:
                        # Don't incur fate point cost if is_boost or is a 'Stunt'
                        fate_points = 0 if is_boost or category == 'Stunt' else 1
                    stress = aspect.stress if aspect.stress else []
                    stress_titles = aspect.stress_titles if aspect.stress_titles else []
                    stress_errors, stress_targets = self.validate_stress(aspect, stress, stress_titles, stress_targets)
                    [self.invokes.append({'aspect_name': 'error', 'error': s}) for s in stress_errors]
            else:
                self.invokes.append({'aspect_name': 'error', 'error': f'_{search}_ not found in availabe aspects'})
                continue
            if self.re and (len(self.args) <= i+2 or (len(self.args) > i+2 and self.args[i+2] not in ['+2', 're', 'reroll'])):
                self.invokes.append({'aspect_name': 'error', 'error': f'Reroll invoke on {aspect_name} is missing +2 or (re)roll'})
                continue
            check_invokes = []
            check_invokes.extend(copy.deepcopy(self.invokes))
            if self.re:
                check_invokes.extend(self.char.last_roll['invokes'])
            if [dup for dup in check_invokes if aspect_name == dup['aspect_name']]:
                self.invokes.append({'aspect_name': 'error', 'error': f'{aspect_name} cannot be invoked more than once on the same roll'})
                continue
            invoke = {
                'aspect_name': aspect_name,
                'is_boost': is_boost,
                'bonus_str': '+2',
                'skills': skills,
                'fate_points': fate_points,
                'category': category,
                'stress': stress,
                'stress_titles': stress_titles,
                'stress_targets': stress_targets
            }
            if self.re:
                invoke['bonus_str'] = '+2' if self.args[i+2] == '+2' else 'reroll'
            self.invokes.append(invoke)

    def validate_stress(self, aspect, stress, stress_titles, stress_targets):
        """Loop through stress to be applied and verify that stress targets are available to apply them

        Parameters
        ----------
        aspect : Character
            Character database object of category 'Aspect'
        stress : list(list)
            A list of stress lists for tracking stress
        stress_titles : list(str)
            A list of stress titles for tracking stress
        stress_targets : list(Character)
            list of targets for validated stress
        
        Returns
        -------
        tuple(list(str), list(Character))
            stress_errors : list(str)
                list of errors when attempting to validate stress
            stress_targets : list(Character)
                list of targets for validated stress
        """

        aspect_name = aspect.name
        stress_errors = []
        possible_targets = self.char.get_invokable_objects()
        for s in range(0, len(stress_titles)):
            targets = copy.deepcopy(possible_targets)
            # Look for a parent with stress track matching the stress title
            parent_stress = self.get_parent_with_stress(self.char, stress_titles[s])
            if parent_stress:
                targets.append({'char': parent_stress, 'parent': parent_stress})
            stress_targets.append(None)
            has_stress = []
            for target in targets:
                stress_target = copy.deepcopy(target['char'])
                command = CharacterCommand(parent=self.parent, ctx=self.ctx, args=self.args, guild=self.guild, user=self.user, channel=self.channel, char=stress_target)
                target_errors = command.stress(['st', stress_titles[s], stress[s][0][0]], stress_target)
                if target_errors:
                    for error in target_errors:
                        if 'cannot absorb' in error and aspect_name.lower() not in stress_target.name.lower():
                            has_stress.append(error)
                            continue
                else:
                    stress_targets[s] = stress_target
                    continue
            if stress_targets[s] is None:
                stress_errors.append(f'Cannot find a target to apply _{stress[s][0][0]} {stress_titles[s]}_ from **{aspect_name}**')
                if has_stress:
                    [stress_errors.append(has) for has in has_stress]
        return stress_errors, stress_targets        

    def get_compels(self):
        """Store the list of compels passed in as command arguments"""

        for i in self.compel_index:
            aspect = self.find_aspect(self.args[i+1])
            if len(self.args) < i+1:
                self.compels.append(['error', f'Mssing aspect'])
                continue
            if not aspect:
                self.compels.append(['error', f'{self.args[i+1]} not found in availabe aspects'])
                continue
            if [dup for dup in self.compels if aspect == dup]:
                self.compels.append(['error', f'{aspect} cannot be compeled more than once on the same roll'])
                continue
            self.compels.append(aspect)

    def get_parent_with_refresh(self, char):
        """Find a parent with avaiable fate refresh

        Parameters
        ----------
        char : Character
            Character database object used to find related parents
        
        Returns
        -------
        Character - parent with available refresh
        """

        if char:
            if char.refresh:
               return char
            elif char.parent_id:
                    parent = Character.get_by_id(char.parent_id)
                    return self.get_parent_with_refresh(parent)
        return None

    def get_parent_with_stress(self, char, stress):
        """Find a parent character with a stress title matching the search text

        Pareameters
        -----------
        char : Character
            Character database object to check for parents
        stress : list(list)
            A list of stress lists for tracking stress
        
        Returns
        -------
        list(str) - the response messages string array
        """

        if char:
            if char.stress_titles and stress in char.stress_titles:
               return char
            else:
                if char.parent_id:
                    parent = Character.get_by_id(char.parent_id)
                    return self.get_parent_with_stress(parent, stress)
        else:
            return None

    def get_available_invokes(self, char=None):
        """Return a list of all available aspects and stunts available for invoking and compeling

        Parameters
        ----------
        char : Character
            Character database object for checking for aspects and stunts available to invoke
        
        Returns
        -------
        list(str) - the response messages string array
        """

        char = char if char else self.char
        self.available = char.get_invokable_objects() if char else []
        scenario_aspects = self.scenario.character.get_invokable_objects() if self.scenario else []
        self.available.extend(scenario_aspects)
        sc_aspects = self.sc.character.get_invokable_objects() if self.sc else []
        self.available.extend(sc_aspects)
        zone_aspects = self.zone.character.get_invokable_objects() if self.zone else []
        self.available.extend(zone_aspects)
        if self.sc and self.sc.characters:
            for char_id in self.sc.characters:
                char = Character.get_by_id(char_id)
                if char and not char.name == char.name:
                    self.available.extend(char.get_invokable_objects())
        if self.zone and self.zone.characters:
            for char_id in self.zone.characters:
                char = Character.get_by_id(char_id)
                if char and not char.name == self.char.name:
                    self.available.extend(char.get_invokable_objects())
        return self.available

    def find_aspect(self, aspect):
        """Find an available aspect matching the aspect search text

        Parameters
        ----------
        apsect : str
            Aspect string to search in the list of available aspects
        
        Returns
        -------
        list(str) - list of aspects matching the search text
        """

        aspect = aspect.replace('_', ' ')
        available = self.get_available_invokes()
        aspects = []
        if self.char:
            for a in available:
                aspect_list = []
                if a['char'].category in ['Aspect','Stunt']:
                    aspect_list.append({'name': a['char'].name.lower(), 'category': a['char'].category})
                if a['char'].high_concept:
                    aspect_list.append({'name': a['char'].high_concept.lower(), 'category': 'High Concept'})
                if a['char'].trouble:
                    aspect_list.append({'name': a['char'].trouble.lower(), 'category': 'Trouble'})
                [
                    aspects.append({'char': a['char'], 'category': asp['category']}) \
                    for asp in aspect_list \
                    if aspect.lower() in asp['name'].lower()
                ]
                    
            if aspects:
                return aspects[0]
        return aspects

    def roll_next(self, exact_roll=None):
        """Make a fate roll and return the roll information
        
        Paramenters
        -----------
        exact_roll : str
            The string representation of the exact roll to replace the dice

        Returns
        -------
        dict - the attributes of a Dreamcraft Bot fate roll
        """

        skill_str, bonus = self.get_skill_bonus()
        bonus_invokes, bonus_invokes_total, invokes_bonus_string, invoke_string = \
            self.get_invoke_bonus()
        bonus += bonus_invokes_total
        dice_roll = self.roll_dice()
        if exact_roll and exact_roll.replace('+','').replace('-','').isdigit():
            dice_roll['rolled'] = int(exact_roll)
        final_roll = dice_roll['rolled'] + bonus
        skill_bonus_str = f' + ({self.skill}{skill_str})' if skill_str else ''
        skill_bonus_str += f' = {final_roll}' if skill_bonus_str or bonus_invokes else ''
        rolled = dice_roll['rolled']
        fate_roll_string = dice_roll['fate_roll_string']
        return {
            'roll_text': f'... rolled: {fate_roll_string} = {rolled}{invokes_bonus_string}{skill_bonus_str}{invoke_string}',
            'roll': dice_roll['rolled'],
            'skill': self.skill,
            'skill_str': skill_str,
            'bonus': bonus,
            'fate_dice_roll': dice_roll['fate_dice_roll'],
            'fate_roll_string': dice_roll['fate_roll_string'],
            'dice': dice_roll['dice'],
            'final_roll': final_roll,
            'defense_roll': 0,
            'shifts': final_roll,
            'shifts_absorbed': 0,
            'shifts_remaining': final_roll,
            'invokes': self.roll_invokes,
            'invokes_bonus': bonus_invokes_total,
            'invokes_bonus_string': invokes_bonus_string,
            'invoke_string': invoke_string
        }

    def reroll(self):
        """Get the previous roll and apply the invoke options to it
        
        Returns
        -------
        dict - the attributes of a Dreamcraft Bot fate roll
        """

        self.char.last_roll['invokes'].extend(copy.deepcopy(self.invokes))
        self.skill = self.char.last_roll['skill']
        self.roll_invokes = self.char.last_roll['invokes']
        return self.roll_next()

    def match_skill(self):
        """Find the skill matching the skill search text
        
        Returns
        -------
        str - the skill matching the skill attribut search text
        """

        if self.skill:
            if self.char.use_approaches:
                skill_name = [s for s in APPROACHES if self.skill[0:2].lower() == s[0:2].lower()]
            else:
                skill_name = [s for s in SKILLS if self.skill[0:2].lower() == s[0:2].lower()]
            self.skill = skill_name[0].split(' - ')[0] if skill_name else self.skill
        return self.skill

    def get_skill_bonus(self):
        """Get the skill and bonus to appply to the roll
        
        Returns
        -------
        tuple(str, int)
            skill_str : str
                The roll text string for the skill
            bonus : int
                The integer bonus to apply for the skill roll
        """

        skill_str = ''
        bonus = 0
        if self.skill !='':
            skill_str = ' ' + self.char.skills[self.skill] if self.skill in self.char.skills else ''
            bonus = int(skill_str) if skill_str else 0
        return skill_str, bonus

    def get_invoke_bonus(self):
        """Get the invoke bonus information to apply to a roll
        
        Returns
        -------
        tuple(list(str), int, str, str)
            bonus_invokes : list(str)
                The list of invokes with bonuses to apply to the total
            bonus_invokes_total - int
                The total amount to apply to a roll for invoke bonuses
            invokes_bonus_string - str
                The string representation of invoke bonuses
            invoke_string - str
                The description of all invoke actions including bonuses and costs
        """

        bonus_invokes = []
        for invoke in self.roll_invokes:
            bonus_str = invoke['bonus_str']
            if self.skill in invoke['skills']:
                bonus_str = invoke['skills'][self.skill]
            elif invoke['category'] == 'Stunt':
                bonus_str = '+0'
            invoke.update({'bonus_str': bonus_str})
        bonus_invokes = len([invoke for invoke in self.roll_invokes if invoke['bonus_str'] == '+2'])
        bonus_invokes_total = sum([int(i['bonus_str']) for i in self.roll_invokes if 'reroll' not in i['bonus_str']])
        invokes_bonus_string = f' + (Invokes bonus = {bonus_invokes_total})' if self.roll_invokes and bonus_invokes_total else ''
        invoke_string = self.get_invoke_string()
        return bonus_invokes, bonus_invokes_total, invokes_bonus_string, invoke_string

    def get_invoke_string(self):
        """Ge the completed string containing descriptions of all invokes
        
        Returns
        -------
        str - the description of all invoke actions including bonuses and costs
        """

        invoke_strings = []
        for invoke in self.roll_invokes:
            name = invoke['aspect_name']
            category = invoke['category']
            bonus_str = invoke['bonus_str']
            fate_points = invoke['fate_points']
            s = 's' if invoke['fate_points'] == 0 or invoke['fate_points'] > 1 else ''
            invoike_string = f'\n...invoked the "{name}" _{category}_ for {bonus_str} (cost {fate_points} fate point{s})'
            invoke_strings.append(invoike_string)
        return ''.join(invoke_strings)

    def roll_dice(self):
        """Roll fate dice and return fate dice attributes
        
        Returns
        -------
        dict - the attributes of a Dreamcraft Bot fate roll
        """

        dice = [random.choice(range(-1, 2)) for _ in range(4)]
        fate_dice_roll = [FATE_DICE[str(d)] for d in dice]
        return {
            'dice': dice,
            'fate_dice_roll': fate_dice_roll,
            'fate_roll_string': ''.join(fate_dice_roll),
            'rolled': sum(dice)
        }
