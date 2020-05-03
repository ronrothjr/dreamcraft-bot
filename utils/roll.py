# roll.py
import random

from config.setup import Setup

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
FATE_DICE = SETUP.fate_dice

class Roll():
    def __init__(self, character):
        self.character = character

    def get_skill_bonus(self, skill='', invokes=[]):
        skill_str = ''
        bonus = 0
        if skill !='':
            if self.character.use_approaches:
                skill_name = [s for s in APPROACHES if skill[0:2].lower() == s[0:2].lower()]
            else:
                skill_name = [s for s in SKILLS if skill[0:2].lower() == s[0:2].lower()]
            skill = skill_name[0].split(' - ')[0] if skill_name else skill
            skill_str = self.character.skills[skill] if skill in self.character.skills else ''
            bonus = int(skill_str) if skill_str else 0
        bonus += len(invokes) * 2 if invokes else 0
        return skill, skill_str, bonus

    def roll_dice(self):
        dice = [random.choice(range(-1, 2)) for _ in range(4)]
        fate_dice_roll = [FATE_DICE[str(d)] for d in dice]
        return {
            'dice': dice,
            'fate_dice_roll': fate_dice_roll,
            'fate_roll_string': ''.join(fate_dice_roll),
            'rolled': sum(dice)
        }

    def roll(self, skill='', invokes=[]):
        skill, skill_str, bonus = self.get_skill_bonus(skill, invokes)
        dice_roll = self.roll_dice()
        final_roll = dice_roll['rolled'] + bonus
        skill_bonus_str = f' + ({skill} {skill_str}) = {final_roll}' if skill_str else ''
        rolled = dice_roll['rolled']
        fate_roll_string = dice_roll['fate_roll_string']
        invokes_bonus_string = f' + (Invokes bonus = {len(invokes) * 2})' if invokes else ''
        invoke_string = ''.join([f'\nInvoked "{i}" for +2 bonus (cost 1 fate point)' for i in invokes]) if invokes else ''
        return {
            'roll_text': f'{self.character.name} rolled: {fate_roll_string} = {rolled}{invokes_bonus_string}{skill_bonus_str}{invoke_string}',
            'roll': dice_roll['rolled'],
            'skill': skill,
            'skill_str': skill_str,
            'bonus': bonus,
            'fate_dice_roll': dice_roll['fate_dice_roll'],
            'fate_roll_string': dice_roll['fate_roll_string'],
            'dice': dice_roll['dice'],
            'final_roll': final_roll,
            'invokes': invokes,
            'invokes_bonus_string': invokes_bonus_string,
            'invoke_string': invoke_string
        }

    def reroll(self):
        return self.roll(self.character.last_roll['skill'])

    def invoke(self, invokes=[]):
        return self.roll(self.character.last_roll['skill'])