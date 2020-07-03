# dreamcraft_bot_e2e_test.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import unittest
import copy
import traceback
from handlers import DreamcraftHandler
from mocks import CTX

results = {
    'commands': 0,
    'assertions': 0,
    'passed': 0,
    'failed': 0,
    'failed_commands': [],
    'errors': 0,
    'command_errors': []
}

def print_results():
    for key in results:
        if key == 'failed_commands':
            print(f'Failed commands:\n\n' + '\n\n'.join(['    Command: {command}\n    Assertion: {assertion}\n    Expected: {expected}\n    Received: {received}'.format(**f) for f in results[key]]))
        elif key == 'command_errors':
            for f in results[key]:
                print(f'Failed command_errors:\n\n' + '\n\n'.join('    Command: {}\n    Assertion: {}\n    Error: {}\n    Traceback: {}'.format(**f)))
        else:
            print('{}: {}'.format(key, results[key]))

ctx1 = CTX('Test Guild 1', 'Test User 1', 'bot_testing', '1111', 'test_user_1')
ctx2 = CTX('Test Guild 1', 'Test User 2', 'bot_testing', '2222', 'test_user_2')
ctx3 = CTX('Test Guild 2', 'Test User 1', 'bot_spamming', '1111', 'test_user_1')
ctx4 = CTX('Test Guild 3', 'Test User 3', 'bot_spamming', '3333', 'test_user_3')

class TestDreamcraftBotE2E(unittest.TestCase):

    def send_and_validate_commands(self, ctx, commands):
        for command in commands:
            complete_messages = []
            args = copy.deepcopy(command['args'])
            results['commands'] += len(args)
            for arg  in args:
                a = copy.deepcopy(arg)
                messages = []
                self.command = ' '.join(a)
                self.print_command('Command: ' + self.command, '-')
                handler = DreamcraftHandler(command['ctx'] if 'ctx' in command else ctx, a)
                messages.extend(handler.get_messages())
                [print(message) for message in messages]
                complete_messages.extend(messages)
            if 'assertions' in command:
                results['assertions'] += len(command['assertions'])
                [self.assert_command(complete_messages, a[0], a[1]) for a in command['assertions']]

    def assert_command(self, messages, assert_str, err_str):
        try:
            if 'should not' in err_str.lower():
                assert_test = assert_str not in ''.join(messages)
            else:
                assert_test = assert_str in ''.join(messages)
            results['passed' if assert_test else 'failed'] += 1
            assert_result = (f'Passed: ' if assert_test else 'Failed: ') + err_str
            self.print_command(assert_result)
            if not assert_test:
                results['failed_commands'].append({
                    'command': copy.deepcopy(self.command),
                    'assertion': err_str,
                    'expected': ('NOT TO FIND ' if 'should not' in err_str.lower() else '') + assert_str,
                    'received': '\n'.join(messages)
                })
        except Exception as err:
            results['command_errors'].append({
                'command': copy.deepcopy(self.command),
                'assertion': err_str,
                'error': ' '.join(err.args),
                'traceback': traceback.format_exc()
            })
            traceback.print_exc()
            raise Exception(' '.join(err.args))

    def print_command(self, result, sep='*'):
        seps = sep * 84
        result = result + (' ' * (84 - len(result)))
        print(''.join([
            f'\n{sep*3}{seps}{sep*3}',
            f'\n{sep}  {result}  {sep}',
            f'\n{sep*3}{seps}{sep*3}\n'
        ]))

    def test_user_setup(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('user', 'timezone', 'US/')],
                'assertions': [
                    ['Time zone search \'us/\' returned more than one. Try one of these:```css', 'should display list of other searches']
                ]
            },
            {
                'args': [('user', 'timezone', 'America/New_York')],
                'assertions': [
                    ['Saved time zone as ***America/New_York***', 'should save user time_zone as New York']
                ]
            },
            {
                'args': [('user', 'contact', 'Reddit - u/ensosati')],
                'assertions': [
                    ['***Contact:*** _Reddit - u/ensosati_', 'should save user contact info']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('user', 'timezone', 'America/New_York')],
                'assertions': [
                    ['Saved time zone as ***America/New_York***', 'should save user time_zone as New York']
                ]
            },
            {
                'ctx': ctx3,
                'args': [('user', 'timezone', 'America/New_York')],
                'assertions': [
                    ['Saved time zone as ***America/New_York***', 'should save user time_zone as New York']
                ]
            },
            {
                'ctx': ctx4,
                'args': [('user', 'timezone', 'America/New_York')],
                'assertions': [
                    ['Saved time zone as ***America/New_York***', 'should save user time_zone as New York']
                ]
            },
            {
                'args': [('u', 'alias', 'character', 'c Test Character 1', 'attack {} exact +1 Forceful')],
                'assertions': [
                    ['_character_ is a reserved command or subcommand', 'should warn of reserved commands']
                ]
            },
            {
                'args': [('u', 'alias', 'character1', 'c Test Character 1', 'attack {} exact +1 Forceful')],
                'assertions': [
                    ['***Aliases:***\n. . .***character1***', 'should set up character1 alias']
                ]
            },
            {
                'args': [('u', 'alias', 'delete', 'character1')],
                'assertions': [
                    ['***Aliases:***\n. . .***character1***', 'should not display deleted character1 alias']
                ]
            },
            {
                'args': [('u', 'alias', 'alias1', 'c Test Character 1', 'attack {} exact +1 Forceful')],
                'assertions': [
                    ['***Aliases:***\n. . .***alias1***', 'should set up alias1 alias']
                ]
            }
        ])

    def test_npc_character_creation(self):
        self.send_and_validate_commands(ctx2, [
            {
                'args': [('r',)],
                'assertions': [
                    ['No active character. Try this to create/select one: ```css\n.d c "CHARACTER NAME"```', 'Should include instructions to create character']
                ]
            },
            {
                'args': [('s',)],
                'assertions': [
                    ['No active scenario. Try this:```css\n.d scenario "SCENARIO NAME"```', 'Should include instructions to create scenario']
                ]
            },
            {
                'args': [('c',)],
                'assertions': [
                    ['No active character or name provided', 'should return no active character if empty characters'],
                    ['CREATE or SELECT A CHARACTER', 'Should include instructions to create character']
                ]
            },
            {
                'args': [('undo','list')],
                'assertions': [
                    ['_args:_ [\'c\']', 'should display command in log']
                ]
            },
            {
                'args': [('5',)],
                'assertions': [
                    ['Page number 5 does not exist', 'should display warning on page number 5']
                ]
            },
            {
                'args': [('c','new')],
                'assertions': [
                    ['How to use the ***new*** prefix:', 'should display new syntax commands']
                ]
            },
            {
                'args': [('c','list')],
                'assertions': [
                    ['No ITEMS found', 'should warn of no characters found']
                ]
            },
            {
                'args': [('new', 'c', 'npc', 'Test NPC 1'), ('y',)],
                'assertions': [
                    ['Create a new CHARACTER named ***Test NPC 1***', 'Should ask Create Test NPC 1 question'],
                    ['YOU ARE CURRENTLY EDITING', 'Should be editing a character'],
                    ['***Test NPC 1*** _(Active)_  _(Nonplayer Character)_', 'Test NPC 1 should be the active character']
                ]
            },
            {
                'args': [('approach', 'Fo', '-2')],
                'assertions': [
                    ['**Approaches:**\n        -2 - Forceful', 'Should add approaches']
                ]
            },
            {
                'args': [('st', 't', '2', 'Physical')],
                'assertions': [
                    ['**_Physical_**  [   ]', 'Should add custom Physical stress track']
                ]
            },
            {
                'args': [('con', 't', '2', 'Wounded')],
                'assertions': [
                    ['[   ] _2_ _Wounded_', 'Should add custom Wounded condition track']
                ]
            },
            {
                'args': [('aspect', 'Test Aspect 2')],
                'assertions': [
                    ['***Test Aspect 2*** _(Active)_  _(Aspect)_', 'Should add Test Aspect 2']
                ]
            },
            {
                'args': [('stunt', 'Test Stunt 2')],
                'assertions': [
                    ['***Test Stunt 2*** _(Active)_  _(Stunt)_', 'Should add Test Stunt 2']
                ]
            }
        ])

    def test_character_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('new', 'c', 'Test Character 1')],
                'assertions': [
                    ['Create a new CHARACTER named ***Test Character 1***', 'Should ask Create Test Character 1 question']
                ]
            },
            {
                'args': [('y',)],
                'assertions': [
                    ['YOU ARE CURRENTLY EDITING', 'Should be editing a character'],
                    ['***Test Character 1*** _(Active)_  _(Character)_', 'Test Character 1 should be the active character'],
                    ['**Fate Points:** 3 (_Refresh:_ 3)', 'Should have defaulted 3 Fate Points'],
                    ['_Physical:_  [   ] [   ] [   ]', 'Physical stress should be added'],
                    ['_Mental:_  [   ] [   ] [   ]', 'Mental stress should be added'],
                    ['[   ] _2_ _Mild_', 'Mild consequences should be added'],
                    ['[   ] _4_ _Moderate_', 'Moderate consequences should be added'],
                    ['[   ] _6_ _Severe_', 'Severe consequences should be added']
                ]
            },
            {
                'args': [('hc', 'High', 'Concept')],
                'assertions': [
                    ['**High Concept:** High Concept', 'Should add and display High Concept']
                ]
            },
            {
                'args': [('t', 'Trouble')],
                'assertions': [
                    ['**Trouble:** Trouble', 'Should add and display Trouble']
                ]
            },
            {
                'args': [('custom', 'Location', 'Earth')],
                'assertions': [
                    ['**Location:** Earth', 'Should add custom Location Earth']
                ]
            },
            {
                'args': [('skill', 'will', '+4', 'Rapport', '+2', 'Lore', '+1')],
                'assertions': [
                    ['**Skills:**\n        +4 - Will', 'Should add skills']
                ]
            },
            {
                'args': [('skill', 'dark magic', '+3')],
                'assertions': [
                    ['+3 - Dark Magic', 'Should add Dark \'Magic\' skill']
                ]
            },
            {
                'args': [('Will',)],
                'assertions': [
                    ['.d skill "SKILL NAME" BONUS [..."SKILL NAME" BONUS]', 'Should display skill syntax']
                ]
            },
            {
                'args': [('provoke', '+3',)],
                'assertions': [
                    ['+3 - Dark Magic, Provoke', 'Should add skills']
                ]
            },
            {
                'args': [('skill', 'delete', 'Will')],
                'assertions': [
                    ['Removed Will skill', 'Should remove Will skill']
                ]
            },
            {
                'args': [('skill', 'delete', 'Rapport')],
                'assertions': [
                    ['Removed Rapport skill', 'Should remove Rapport skill']
                ]
            },
            {
                'args': [('delete', 'skill', 'Lore')],
                'assertions': [
                    ['Removed Lore skill', 'Should remove Lore skill']
                ]
            },
            {
                'args': [('delete', 'skill', 'dark magic')],
                'assertions': [
                    ['Removed Dark Magic skill', 'Should remove Dark Magic skill']
                ]
            },
            {
                'args': [('approach', 'Fo', '+4', 'Cl', '+2', 'Qu', '+1', 'Sn', '+2', 'Ca', '+1', 'Fl', '0', 'Empathic', '+1')],
                'assertions': [
                    ['**Approaches:**\n        +4 - Forceful', 'Should add approaches']
                ]
            },
            {
                'args': [('aspect', 'Test Aspect 1')],
                'assertions': [
                    ['***Test Aspect 1*** _(Active)_  _(Aspect)_', 'Should add Test Aspect 1']
                ]
            },
            {
                'args': [('aspect', 'type', 'Weapons')],
                'assertions': [
                    ['Set the ***Test Aspect 1*** aspect with type _Weapons_', 'Should \'Weapons\' aspect type']
                ]
            },
            {
                'args': [('stunt', 'Test Stunt 1')],
                'assertions': [
                    ['***Test Stunt 1*** _(Active)_  _(Stunt)_', 'Should add Test Stunt 1']
                ]
            },
            {
                'args': [('c', 'stunt', 'character')],
                'assertions': [
                    ['Test Stunt 1', 'Should edit Test Stunt 1']
                ]
            },
            {
                'args': [('st', 't', '1', 'Energy')],
                'assertions': [
                    ['**_Energy_**  [   ]', 'Should add custom Energy stress track']
                ]
            },
            {
                'args': [('st', 'Energy')],
                'assertions': [
                    ['**_Energy_**  [X]', 'Should absorb 1 Energy stress']
                ]
            },
            {
                'args': [('fate', '+')],
                'assertions': [
                    ['**Fate Points:** 1', 'Should add 1 fate point']
                ]
            },
            {
                'args': [('c', 'p')],
                'assertions': [
                    ['Test Character 1', 'Should edit Test Character 1']
                ]
            },
            {
                'args': [('st', 't', '4', 'Energy')],
                'assertions': [
                    ['_Energy:_  [   ] [   ] [   ] [   ]', 'Should add custom Energy stress track']
                ]
            },
            {
                'args': [('st', 't', '4', 'Energy')],
                'assertions': [
                    ['_Energy:_  [   ] [   ] [   ] [   ]', 'Should add custom Energy stress track']
                ]
            },
            {
                'args': [('r', 'i')],
                'assertions': [
                    ['An invoke is missing an aspect', 'Should warn of missing aspect']
                ]
            },
            {
                'args': [('r', 'i', 'Test Stunt 1')],
                'assertions': [
                    ['_Energy:_  [X] [   ] [   ] [   ]', 'Should absorb 1 custom Energy'],
                    ['**Fate Points:** 2', 'Should spend 1 Fate Point']
                ]
            },
            {
                'args': [('r', 'Will', 'i')],
                'assertions': [
                    ['An invoke is missing an aspect', 'Should warn of missing aspect']
                ]
            },
            {
                'args': [('r', 'Will', 'i', 'Test Stunt 1')],
                'assertions': [
                    ['_Energy:_  [X] [X] [   ] [   ]', 'Should absorb 1 custom Energy'],
                    ['**Fate Points:** 1', 'Should spend 1 Fate Point']
                ]
            },
            {
                'args': [('st', 'refresh', 'Energy')],
                'assertions': [
                    ['_Energy:_  [   ] [   ] [   ] [   ]', 'Should refresh Energy']
                ]
            },
            {
                'args': [('fate', 'refresh')],
                'assertions': [
                    ['**Fate Points:** 3', 'Should refresh Fate Points']
                ]
            },
            {
                'args': [('stunt', 'Test Stunt 2')],
                'assertions': [
                    ['***Test Stunt 2*** _(Active)_  _(Stunt)_', 'Should add Test Stunt 2']
                ]
            },
            {
                'args': [('delete', 'stunt')],
                'assertions': [
                    ['Syntax error:```css\n.d delete stunt "NAME"```', 'Should warn with delete stunt syntax']
                ]
            },
            {
                'args': [('delete', 'stunt', 'Test Stunt 2')],
                'assertions': [
                    ['"Test Stunt 2" removed from stunts', 'Should display removal of \'Test Stunt 2']
                ]
            },
            {
                'args': [('counter', 'help')],
                'assertions': [
                    ['Counters Help:', 'Should display counters help']
                ]
            },
            {
                'args': [('counter', 'add', 'Karmic Debt')],
                'assertions': [
                    ['Incorrect syntax for counter.\nTry this: ```css\n.d c counter add 3 "Strikes"```', 'Should warn of add syntax error']
                ]
            },
            {
                'args': [('counter', 'add', 'Karmic Debt', '6')],
                'assertions': [
                    ['Incorrect syntax for counter.\nTry this: ```css\n.d c counter add 3 "Strikes"```', 'Should warn of add syntax error']
                ]
            },
            {
                'args': [('counter', 'add', '6', 'Karmic Debt')],
                'assertions': [
                    ['**_Karmic Debt:_**  [   ] [   ] [   ] [   ] [   ] [   ]', 'Should add Karmic Debt counter track']
                ]
            },
            {
                'args': [('counter', 'edit', '7', 'Karmic Debt')],
                'assertions': [
                    ['**_Karmic Debt:_**  [   ] [   ] [   ] [   ] [   ] [   ] [   ]', 'Should add Karmic Debt counter track']
                ]
            },
            {
                'args': [('count', 'Karmic Debt')],
                'assertions': [
                    ['**_Karmic Debt:_**  [X] [   ] [   ] [   ] [   ] [   ] [   ]', 'Should count 1 Karmic Debt counter']
                ]
            },
            {
                'args': [('tick', '2', 'Karmic Debt')],
                'assertions': [
                    ['**_Karmic Debt:_**  [X] [X] [X] [   ] [   ] [   ] [   ]', 'Should tick 2 Karmic Debt counters']
                ]
            },
            {
                'args': [('tick', '5', 'Karmic Debt')],
                'assertions': [
                    ['Cannot tick for 5 Karmic Debt (4 available)', 'Should warn of unavailable ticks']
                ]
            },
            {
                'args': [('delete', 'counter', 'Karmic Debt')],
                'assertions': [
                    ['Removed **_Karmic Debt_** counter', 'Should remove Karmic Debt counter'],
                    ['**_Karmic Debt:_**', 'Should not display Karmic Debt counter']
                ]
            },
            {
                'args': [('counter', 'add', '7', 'Karmic Debt')],
                'assertions': [
                    ['**_Karmic Debt:_**  [   ] [   ] [   ] [   ] [   ] [   ] [   ]', 'Should add Karmic Debt counter track']
                ]
            }
        ])

    def test_character_permissions(self):
        self.send_and_validate_commands(ctx2, [
            {
                'args': [
                    ('c','list'),
                    ('=1',)
                ],
                'assertions': [
                    ['***Test Character 1*** _(Active)_  _(Character)_', 'Test Character 1 should be the active character']
                ]
            },
            {
                'args': [('t','Trouble 2')],
                'assertions': [
                    ['You do not have permission', 'should prevent Test User 2 from editing Test Character 1']
                ]
            }
        ])

    def test_copy_character(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('c', 'copy', 'to', 'Guild 2')],
                'assertions': [
                    ['You may not copy until you have created a character on another server', 'should warn user to create a character on another server']
                ]
            },
            {
                'ctx': ctx3,
                'args': [
                    ('new', 'c', 'Test Character 2'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test Character 2*** _(Active)_  _(Character)_', 'Test Character 2 should be the active character']
                ]
            },
            {
                'args': [('aspect', 'Test Aspect 2')],
                'assertions': [
                    ['***Test Aspect 2*** _(Active)_  _(Aspect)_', 'Should add Test Aspect 2']
                ]
            },
            {
                'args': [('c', 'copy', 'to', 'Guild 2')],
                'assertions': [
                    ['***Test Character 1*** copied to ***Test Guild 2***', 'should copy character to another server']
                ]
            },
            {
                'ctx': ctx3,
                'args': [
                    ('c', 'Test Character 1')
                ],
                'assertions': [
                    ['***Test Character 1*** _(Active)_  _(Character)_', 'Test Character 1 should be the active character'],
                    ['***Test Aspect 1*** _(Aspect)_', 'Should have Test Aspect 1'],
                    ['***Test Stunt 1*** _(Stunt)_', 'Should have Test Stunt 1']
                ]
            }
        ])

    def test_command_logging(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('undo','list')],
                'assertions': [
                    ['Command', 'should display comand in log']
                ]
            }
        ])

    def test_session_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('session',)],
                'assertions': [
                    ['No active session or name provided', 'should return no active session if empty sessions'],
                    ['**CREATE or SESSION**```css\n.d new session "YOUR SESSION\'S NAME"```', 'Should include instructions to create session']
                ]
            },
            {
                'args': [
                    ('new', 'session', 'Test', 'Session'),
                    ('y')
                ],
                'assertions': [
                    ['***Test Session*** _(Active Session)_', 'should create sesion named Test Session']
                ]
            },
            {
                'args': [('session', 'desc', 'Test', 'description')],
                'assertions': [
                    ['***Test Session*** _(Active Session)_  - "Test description"', 'should add a \'Test description\' session named Test Session']
                ]
            },
            {
                'args': [('session', 'start')],
                'assertions': [
                    ['_Started On:_', 'should start session named Test Session']
                ]
            }
        ])

    def test_scenario_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('s', 'Test Scene 1')],
                'assertions': [
                    ['No active scenario. Try this:```css\n.d scenario "SCENARIO NAME"```', 'Should include instructions to create scenario']
                ]
            },
            {
                'args': [('scenario',)],
                'assertions': [
                    ['No active scenario or name provided', 'should return no active scenario if empty scenarios'],
                    ['**CREATE or SCENARIO**```css\n.d new scenario "YOUR SCENARIOR\'S NAME"```', 'Should include instructions to create scenario']
                ]
            },
            {
                'args': [('new', 'scenario', 'Test', 'Scenario', '1')],
                'assertions': [
                    ['Create a new SCENARIO named ***Test Scenario 1***?', 'should ask question to create scenario named Test Scenario 1']
                ]
            },
            {
                'args': [('y',)],
                'assertions': [
                    ['***Test Scenario 1*** _(Active Scenario)_', 'should create scenario named Test Scenario 1']
                ]
            },
            {
                'args': [('scenario', 'desc', 'Test', 'description')],
                'assertions': [
                    ['***Test Scenario 1*** _(Active Scenario)_  - "Test description"', 'should add a \'Test description\' scenario named Test Scenario 1']
                ]
            },
            {
                'args': [('scenario','list')],
                'assertions': [
                    ['***Test Scenario 1*** _(Active Scenario)_', 'should create scenario named Test Scenario 1']
                ]
            },
            {
                'args': [('new', 'scenario', 'Test', 'Scenario', '2'), ('y',)],
                'assertions': [
                    ['Create a new SCENARIO named ***Test Scenario 2***?', 'should ask question to create scenario named Test Scenario 2'],
                    ['***Test Scenario 2*** _(Active Scenario)_', 'should create scenario named Test Scenario 2']
                ]
            },
            {
                'args': [('scenario', 'Test', 'Scenario', '1')],
                'assertions': [
                    ['***Test Scenario 1***', 'should select scenario named Test Scenario 1']
                ]
            }
        ])

    def test_scene_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('scene',)],
                'assertions': [
                    ['No active scene or name provided', 'should return no active scene if empty scenes'],
                    ['**CREATE or SCENE**```css\n.d new scene "YOUR SCENE\'S NAME"```', 'Should include instructions to create scene']
                ]
            },
            {
                'args': [('new', 'scene', 'Test', 'Scene', '1'),('y',)],
                'assertions': [
                    ['Create a new SCENE named ***Test Scene 1***?', 'should ask question to create scene named Test Scene 1'],
                    ['***Test Scene 1*** _(Active Scene)_', 'should create scene named Test Scene 1']
                ]
            },
            {
                'args': [('desc', 'Test', 'description')],
                'assertions': [
                    ['***Test Scene 1*** _(Active Scene)_  - "Test description"', 'should add a \'Test description\' scene named Test Scene 1']
                ]
            },
            {
                'args': [('player', 'Test Character 1')],
                'assertions': [
                    ['Added ***Test Character 1*** to _Test Scene 1_ scene', 'should add \'Test Character 1\' to \'Test Scene 1\'']
                ]
            },
            {
                'args': [('start',)],
                'assertions': [
                    ['_Started On:_', 'should start the scene named Test Scene 1']
                ]
            },
            {
                'args': [('scene', 'list')],
                'assertions': [
                    ['***Test Scene 1***', 'should display scene named Test Scene 1']
                ]
            },
            {
                'args': [('new', 'Test', 'Scene', '2'),('y',)],
                'assertions': [
                    ['Create a new SCENE named ***Test Scene 2***?', 'should ask question to create scene named Test Scene 2'],
                    ['***Test Scene 2*** _(Active Scene)_', 'should create scene named Test Scene 2']
                ]
            },
            {
                'args': [('scene', 'Test', 'Scene', '1')],
                'assertions': [
                    ['***Test Scene 1*** _(Active Scene)_', 'should select scene named Test Scene 1']
                ]
            }
        ])

    def test_zone_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('zone',)],
                'assertions': [
                    ['No active zone or name provided\n\n\n**CREATE or ZONE**```css\n.d new zone "YOUR ZONE\'S NAME"```', 'should return no active scene if empty scenes and  include instructions to create scene']
                ]
            },
            {
                'args': [('new', 'z', 'Test', 'Zone', '1')],
                'assertions': [
                    ['Create a new ZONE named ***Test Zone 1***?', 'should ask question to create zone named Test Zone 1']
                ]
            },
            {
                'args': [('y',)],
                'assertions': [
                    ['***Test Zone 1*** _(Active Zone)_', 'should create scene named Test Zone 1']
                ]
            },
            {
                'args': [('desc', 'Test', 'description')],
                'assertions': [
                    ['***Test Zone 1*** _(Active Zone)_  - "Test description"', 'should add a \'Test description\' scene named Test Zone 1']
                ]
            },
            {
                'args': [('z', 'character', 'aspect', 'Test Scene Aspect 1')],
                'assertions': [
                    ['***Test Scene Aspect 1*** _(Active)_  _(Aspect)_', 'should add a \'Test Scene Aspect 1\' aspect to \'Test Zone 1\'']
                ]
            },
            {
                'args': [
                    ('new', 'z', 'Test', 'Zone', '2'),
                    ('y',),
                    ('desc', 'Test', 'description', '2')],
                'assertions': [
                    ['***Test Zone 2*** _(Active Zone)_', 'should create scene named Test Zone 2'],
                    ['***Test Zone 2*** _(Active Zone)_  - "Test description 2"', 'should add a \'Test description 2\' scene named Test Zone 2']
                ]
            }
        ])

    def test_scene_features(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [
                    ('scene', 'connect', 'Zone 1', 'Zone 2'),
                    ('scene', 'connect', 'Zone 1', 'to', 'Zone 3'),
                    ('scene', 'connect', 'Zone 1', 'to', 'Zone 2'),
                    ('scene', 'connect', 'Zone 1', 'to', 'Zone 2'),
                    ('zone', 'Test Zone 1')
                ],
                'assertions': [
                    ['Incorrect syntax:', 'should warn of incorrect syntax'],
                    ['***Test Zone 1*** and ***Test Zone 2*** are now adjoined in ***Test Scene 1***', 'should adjoin \'Test Zone 1\' and \'Test Zone 2\''],
                    ['***Test Zone 1*** and ***Test Zone 2*** are already adjoined in ***Test Scene 1***', 'should warn that \'Test Zone 1\' and \'Test Zone 2\' are already adjoined']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'npc', 'Test NPC 1'),
                    ('scene', 'enter')
                ],
                'assertions': [
                    ['Added ***Test NPC 1*** to _Test Scene 1_ scene', 'should add \'Test NPC 1\' to \'Test Scene 1\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('scene', 'move', 'Test Zone 1')],
                'assertions': [
                    ['***Test NPC 1*** is already in the _Test Zone 1_ zone', 'should show \'Test NPC 1\' is already in \'Test Zone 1\'']
                ]
            },
            {
                'args': [
                    ('new', 'engagement', 'Conflict', 'Test Conflict'),
                    ('y',)
                ],
                'assertions': [
                    ['***YOU ARE CURRENTLY EDITING...***\n:point_down:\n\n        ***Test Conflict***', 'should add a new Conflict engagement']
                ]
            },
            {
                'args': [('e', 'start')],
                'assertions': [
                    ['_Started On:_', 'should start \'Test Conflict\' engagement']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('e', 'oppose', 'NPC')],
                'assertions': [
                    ['Added ***Test NPC 1*** to the opposition in the _Test Conflict_ engagement', 'should add \'Test NPC 1\' to the conflict']
                ]
            },
            {
                'args': [
                    ('c', 'Test Character 1'),
                    ('scene', 'enter')
                ],
                'assertions': [
                    ['***Test Character 1*** is already in _Test Scene 1_', 'should report that  \'Test Character 1\' is already in \'Test Scene 1\'']
                ]
            },
            {
                'args': [('scene', 'move', 'Test Zone 1')],
                'assertions': [
                    ['***Test Character 1*** is already in the _Test Zone 1_ zone', 'should show \'Test Character 1\' is already in \'Test Zone 1\'']
                ]
            },
            {
                'args': [('scene', 'note', 'An eerie cloud of mist rolls over the walls of Castle Dracula'), ('c', 'say','The children of the night. What beautiful music they make.'), ('scene', 'story')],
                'assertions': [
                    ['Log created', 'should record that a note was recorded'],
                    ['An eerie cloud of mist rolls over the walls of Castle Dracula', 'should display scene note in the story dialog'],
                    ['_note:_ ***Test Character 1*** says, "The children of the night. What beautiful music they make."', 'should display character dialog in the story']
                ]
            }
        ])

    def test_actions(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [
                    ('c','Test Character 1'),
                    ('available',)
                ],
                'assertions': [
                    ['***Test Scene Aspect*** (Aspect of ***Test Zone 1***)', 'should show \'Test Scene Aspect\' from \'Test Zone 1\''],
                    ['***Test Stunt*** (Stunt of ***Test NPC 1***)', 'should not show \'Test Stunt\' from \'Test NPC 1\'']
                ]
            },
            {
                'args': [('alias1','NPC')],
                'assertions': [
                    ['***Test NPC 1*** faces', 'should display \'Test NPC 1\' facing an attack'],
                    ['attack from ***Test Character 1***', 'should display an attack from \'Test Character 1\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'npc', 'Test NPC 1'),
                    ('defend', 'exact', '+0', 'Forceful')
                ],
                'assertions': [
                    [' shifts to absorb', 'should display \'Test NPC 1\' rolling with shifts to absorb'],
                    ['option to take a boost in exchange for one shift', 'should allow succeed with style boost']
                ]
            },
            {
                'args': [('boost', 'Got \'em on the Ropes')],
                'assertions': [
                    ['***Got \'em on the Ropes*** _(Active)_  _(Boost)_  _(Aspect)_', 'should add boost aspect'],
                    ['6 shifts left to absorb.', 'should display remaining shifts']
                ]
            },
            {
                'args': [('boost', 'Got \'em on the Ropes')],
                'assertions': [
                    ['boost has already been claimed', 'should warn of boost already being claimed']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('c', 'con', 'Wounded')],
                'assertions': [
                    ['4 shifts left to absorb.', 'should display remaining shifts to absorb']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('c', 'p'),('c', 'st', 'Physical', '3')],
                'assertions': [
                    ['cannot absorb', 'should display cannot absorb warning']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('c', 'st', 'Physical', '1')],
                'assertions': [
                    ['3 shifts left to absorb.', 'should display remaining shifts to absorb']
                ]
            },
            {
                'args': [('attack', 'NPC', 'Forceful')],
                'assertions': [
                    ['***Test Character 1*** cannot attack', 'should display cannot attack warning']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('c', 'st', 'Physical', '1')],
                'assertions': [
                    ['2 shifts left to absorb.', 'should display 1 shift left to absorb']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('takeout',)],
                'assertions': [
                    ['***Test NPC 1*** was taken out.', 'should take out \'Test NPC 1\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('new', 'c', 'npc', 'Test NPC 2'),
                    ('y',),
                    ('approach', 'Fo', '-2'),
                    ('st', 't', 'CORE'),
                    ('con', 't', 'FATE'),
                    ('aspect', 'freeinvoke', 'Test Aspect 3'),
                    ('aspect', 'freeinvoke', '2', 'Test Aspect 4'),
                    ('stunt', 'Test Stunt 2'),
                    ('scene', 'enter')
                ],
                'assertions': [
                    ['**_Invokes:_**  [   ] [   ]', 'should add 2 \'Invokes\' to \'Test Aspect 4\'']
                ]
            },
            {
                'args': [
                    ('attack', 'Test NPC 2', 'exact', '+8', 'Forceful'),
                    ('freeinvoke',),
                    ('freeinvoke', 'Not So Fast')
                ],
                'assertions': [
                    ['***Test NPC 2*** faces', 'should display \'Test NPC 2\' facing an attack'],
                    ['attack from ***Test Character 1***', 'should display an attack from \'Test Character 1\''],
                    ['The outcome of your \'Attack\' has not yet been determined.', 'should warn of undetermined outcome']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('defend', 'exact', '+0', 'Forceful', 'invoke', 'Test Aspect 3'),
                    ('boost',)
                ],
                'assertions': [
                    [' shifts to absorb', 'should display \'Test NPC 2\' rolling with shifts to absorb'],
                    ['option to take a boost in exchange for one shift', 'should allow succeed with style boost'],
                    ['You may not claim a boost', 'should warn of being unable to claim a boost'],
                ]
            },
            {
                'args': [
                    ('freeinvoke',),
                    ('freeinvoke', 'Not So Fast'),
                    ('freeinvoke', 'Not So Fast'),
                    ('boost',),
                    ('boost', 'Prone'),
                    ('boost', 'Prone')
                ],
                'assertions': [
                    ['.d freeinvoke "ASPECT NAME"', 'should warn of freeinvoke syntax error'],
                    ['***Not So Fast*** _(Active)_  _(Aspect)_', 'should display \'Not So Fast\' aspect'],
                    ['The free invoke has already been claimed from \'Succeed with Style\'.', 'should warn of freeinvoke already claimed'],
                    ['**_Invokes:_**  [   ] [   ]', 'should display \'Invokes\' on the \'Not So Fast\' aspect'],
                    ['.d boost "BOOST NAME"', 'should display boost syntax warning'],
                    ['***Prone*** _(Active)_  _(Boost)_  _(Aspect)_', 'should display the \'Prone\' boost on the defender'],
                    ['The boost has already been claimed from \'Succeed with Style\'.', 'should warn of boost already claimed']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'con', 'Moderate', 'Dislocated Shoulder'),
                    ('c', 'parent')
                ],
                'assertions': [
                    ['[X] _4_ _Moderate:_  - Dislocated Shoulder', 'should display \'Dislocated Shoulder\' in Moderate consequence'],
                    ['***Dislocated Shoulder*** _(Active)_  _(Aspect)_', 'should show the \'Dislocated Shoulder\' aspect']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'con', 'delete', 'Moderate')
                ],
                'assertions': [
                    ['[X] _4_ _Moderate:_  - Dislocated Shoulder', 'should not display \'Dislocated Shoulder\' in Moderate consequence'],
                    ['***Dislocated Shoulder*** _(Active)_  _(Aspect)_', 'should not show the \'Dislocated Shoulder\' aspect']
                ]
            }
        ])

    def test_end_delete_components(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [
                    ('c', 'Test Character 1'),
                    ('scene', 'exit')
                ],
                'assertions': [
                    ['***Test Character 1*** removed from _Test Scene 1_', 'should remove \'Test Character 1\' from \'Test Scene 1\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'npc', 'Test NPC 1'),
                    ('scene', 'exit')
                ],
                'assertions': [
                    ['***Test NPC 1*** removed from _Test Scene 1_', 'should remove \'Test NPC 1\' from \'Test Scene 1\'']
                ]
            },
            {
                'args': [('engagement', 'end')],
                'assertions': [
                    ['_Ended On:_', 'should end the engagement named Test Conflict']
                ]
            },
            {
                'args': [('scene', 'end')],
                'assertions': [
                    ['_Ended On:_', 'should end the scene named Test Scene 1']
                ]
            },
            {
                'args': [('session', 'end')],
                'assertions': [
                    ['_Ended On:_', 'should end the session named Test Session']
                ]
            },
            {
                'args': [('engagement', 'delete')],
                'assertions': [
                    ['***Test Conflict*** removed', 'should remove \'Test Conflict\'']
                ]
            },
            {
                'args': [('zone', 'delete')],
                'assertions': [
                    ['***Test Zone 1*** removed', 'should remove \'Test Zone 1\'']
                ]
            },
            {
                'args': [('scene', 'list')],
                'assertions': [
                    ['***Test Scene 1***', 'should display scene named Test Scene 1']
                ]
            },
            {
                'args': [('scene', 'delete')],
                'assertions': [
                    ['***Test Scene 1*** removed', 'should remove \'Test Scene 1\'']
                ]
            },
            {
                'args': [('scene', 'list')],
                'assertions': [
                    ['***Test Scene 2***', 'should display scene named Test Scene 2']
                ]
            },
            {
                'args': [('scene', 'Test Scene 2'), ('delete', 'scene')],
                'assertions': [
                    ['***Test Scene 2*** removed', 'should remove \'Test Scene 2\'']
                ]
            },
            {
                'args': [('scenario', 'delete')],
                'assertions': [
                    ['***Test Scenario 1*** removed', 'should remove \'Test Scenario 1\'']
                ]
            },
            {
                'args': [('scenario', 'Test Scenario 2'), ('delete', 'scenario')],
                'assertions': [
                    ['***Test Scenario 2*** removed', 'should remove \'Test Scenario 2\'']
                ]
            },
            {
                'args': [('session', 'delete')],
                'assertions': [
                    ['***Test Session*** removed', 'should remove \'Test Session\'']
                ]
            }
        ])

    def test_character_sharing(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [
                    ('c', 'Test Character 1'),
                    ('share',)
                ],
                'assertions': [
                    ['No share settings specified.', 'should warn that no share settings were specified']
                ]
            },
            {
                'args': [('share', 'anyone')],
                'assertions': [
                    ['Sharing enabled for ***Test Character 1***', 'should share character']
                ]
            },
            {
                'args': [('share', 'copy')],
                'assertions': [
                    ['Copying enabled for ***Test Character 1**', 'should enable copying']
                ]
            },
            {
                'args': [('share', 'revoke')],
                'assertions': [
                    ['Sharing revoked for ***Test Character 1***', 'should revoke sharing']
                ]
            },
            {
                'args': [
                    ('share', 'anyone'),
                    ('share', 'copy'),
                    ('c', 'shared'),
                    ('copy',)
                ],
                'assertions': [
                    ['You cannot copy your own character within the same guild', 'should warn that you cannot copy your own character within the same guild']
                ]
            },
            {
                'ctx': ctx4,
                'args': [
                    ('c', 'shared')
                ],
                'assertions': [
                    ['***Test Character 1*** copied', 'should copy shared \'Test Character 1\'']
                ]
            }
        ])

    def test_delete_restore_characters(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [
                    ('c', 'Test Character 1'),
                    ('c', 'delete'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test Character 1*** removed', 'should remove \'Test Character 1\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'npc', 'Test NPC 1'),
                    ('c', 'delete'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test NPC 1*** removed', 'should archive \'Test NPC 1\'']
                ]
            },
            {
                'ctx': ctx3,
                'args': [
                    ('c', 'Test Character 1'),
                    ('c', 'delete'),
                    ('y',),
                    ('c', 'Test Character 2'),
                    ('c', 'delete'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test Character 2*** removed', 'should remove \'Test Character 2\''],
                    ['***Test Character 1*** removed', 'should remove \'Test Character 1\'']
                ]
            },
            {
                'args': [
                    ('c', 'restore', 'Test Character 1')
                ],
                'assertions': [
                    ['***Test Character 1*** restored', 'should restore \'Test Character 1\''],
                    ['***Test Aspect 1*** _(Aspect)_', 'Should have Test Aspect 1'],
                    ['***Test Stunt 1*** _(Stunt)_', 'Should have Test Stunt 1']
                ]
            },
            {
                'args': [
                    ('c', 'Test Character 1'),
                    ('c', 'delete'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test Character 1*** removed', 'should remove \'Test Character 1\'']
                ]
            },
            {
                'args': [
                    ('new', 'c', 'Test Character 1'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test Character 1*** _(Active)_  _(Character)_', 'Test Character 1 should be the active character']
                ]
            },
            {
                'args': [
                    ('c', 'Test Character 1'),
                    ('c', 'delete'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test Character 1*** removed', 'should remove \'Test Character 1\'']
                ]
            },
            {
                'args': [
                    ('c', 'restore', 'Test Character 1'),
                    ('c', '=1')
                ],
                'assertions': [
                    ['***Test Character 1*** restored', 'should restore \'Test Character 1\''],
                    ['***Test Aspect 1*** _(Aspect)_', 'should have Test Aspect 1'],
                    ['***Test Stunt 1*** _(Stunt)_', 'should have Test Stunt 1']
                ]
            },
            {
                'args': [
                    ('c', 'delete', 'approach', 'Forceful'),
                    ('c', 'delete', 'aspect', 'Test Aspect 1'),
                    ('c', 'delete', 'stunt', 'Test Stunt 1'),
                    ('c', 'delete', 'stress', 'title', 'Energy'),
                    ('c', 'delete', 'consequence', 'title', 'Mild')
                ],
                'assertions': [
                    ['Are you sure you want to delete this CHARACTER?', 'should not ask to delete the character'],
                    ['+4 - Forceful', 'should not have skill \'+4 - Forceful\''],
                    ['***Test Aspect 1*** _(Aspect)_', 'should not have Test Aspect 1'],
                    ['***Test Stunt 1*** _(Stunt)_', 'should not have Test Stunt 1'],
                    ['_Energy:_  [   ] [   ] [   ] [   ]', 'should not have Energy stress track'],
                    ['[   ] _2_ _Mild_', 'should not have Mild consequence']
                ]
            },
            {
                'args': [
                    ('log', 'errors')
                ],
                'assertions': [
                    ['Error', 'should show error in undo list']
                ]
            }
        ])
