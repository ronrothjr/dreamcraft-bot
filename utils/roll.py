# roll.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import random

from config.setup import Setup

SETUP = Setup()
APPROACHES = SETUP.approaches
SKILLS = SETUP.skills
FATE_DICE = SETUP.fate_dice

class Roll():
    def __init__(self, character):
        self.character = character

    def get_skill_bonus(self, skill=''):
        skill_str = ''
        bonus = 0
        if skill !='':
            if self.character.use_approaches:
                skill_name = [s for s in APPROACHES if skill[0:2].lower() == s[0:2].lower()]
            else:
                skill_name = [s for s in SKILLS if skill[0:2].lower() == s[0:2].lower()]
            skill = skill_name[0].split(' - ')[0] if skill_name else skill
            skill_str = ' ' + self.character.skills[skill] if skill in self.character.skills else ''
            bonus = int(skill_str) if skill_str else 0
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
        bonus_invokes = [arr for arr in invokes if arr[1] == '+2 bonus']
        bonus_invokes_total = len(bonus_invokes) * 2
        invokes_bonus_string = f' + (Invokes bonus = {bonus_invokes_total})' if invokes else ''
        invoke_string = ''.join([f'\nInvoked "{arr[0]}" for {arr[1]} (cost 1 fate point)' for arr in invokes]) if invokes else ''
        if skill:
            skill, skill_str, bonus = self.get_skill_bonus(skill)
        else:
            skill_str, bonus = '', 0 + bonus_invokes_total
        dice_roll = self.roll_dice()
        final_roll = dice_roll['rolled'] + bonus
        skill_bonus_str = f' + ({skill}{skill_str})' if skill_str else ''
        skill_bonus_str += f' = {final_roll}' if skill_bonus_str or bonus_invokes else ''
        rolled = dice_roll['rolled']
        fate_roll_string = dice_roll['fate_roll_string']
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
            'invokes_bonus': bonus_invokes_total,
            'invokes_bonus_string': invokes_bonus_string,
            'invoke_string': invoke_string
        }

    def reroll(self, invokes=[]):
        self.character.last_roll['invokes'].extend(invokes)
        return self.roll(self.character.last_roll['skill'], self.character.last_roll['invokes'])