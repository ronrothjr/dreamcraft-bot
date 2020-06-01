# dreamcraft_bot_e2e_test.py
import unittest
import datetime
import asyncio
from handlers import DreamcraftHandler
from mocks import CTX

ctx1 = CTX('Test Guild', 'Test User 1', 'bot_testing')
ctx2 = CTX('Test Guild', 'Test User 2', 'bot_testing')

class TestDreamcraftBotE2E(unittest.TestCase):

    def send_and_validate_commands(self, ctx, commands):
        for command in commands:
            print('\nCommand: ' + ' '.join(command['args']) + '\n')
            handler = DreamcraftHandler(command['ctx'] if 'ctx' in command else ctx, command['args'])
            messages = handler.get_messages()
            [print(message) for message in messages]
            if 'assertions' in command:
                [self.assert_command(messages, a[0], a[1]) for a in command['assertions']]

    def assert_command(self, messages, assert_str, err_str):
        assert_test = assert_str in ''.join(messages)
        assert_result = (f'Passed ' if assert_test else 'Failed ') + err_str
        print(f'\n{assert_result}\n')
        self.assertTrue(assert_test, err_str)

    def test_user_setup(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': ('user', 'timezone', 'America/New_York'),
                'assertions': [
                    ['Saved time zone as ***America/New_York***', 'should save user time_zone as New York']
                ]
            }
        ])

    def test_user_2_setup(self):
        self.send_and_validate_commands(ctx2, [
            {
                'args': ('user', 'timezone', 'America/New_York'),
                'assertions': [
                    ['Saved time zone as ***America/New_York***', 'should save user time_zone as New York']
                ]
            }
        ])

    def test_npc_character_creation(self):
        self.send_and_validate_commands(ctx2, [  
            {
                'args': ('c',),
                'assertions': [
                    ['No active character or name provided', 'should return no active character if empty characters'],
                    ['CREATE or SELECT A CHARACTER', 'Should include instructions to create character']
                ]
            },
            {
                'args': ('npc', 'Test', 'NPC'),
                'assertions': [
                    ['Create a new CHARACTER named ***Test NPC***', 'Should ask Create Test NPC question']
                ]
            },
            {
                'args': ('y',),
                'assertions': [
                    ['YOU ARE CURRENTLY EDITING', 'Should be editing a character'],
                    ['***Test NPC*** _(Active)_  _(Nonplayer Character)_', 'Test NPC should be the active character']
                ]
            },
            {
                'args': ('approach', 'Fo', '-2'),
                'assertions': [
                    ['**Approaches:**\n        -2 - Forceful', 'Should add approaches']
                ]
            },
            {
                'args': ('st', 't', '2', 'Physical'),
                'assertions': [
                    ['**_Physical_**  [   ]', 'Should add custom Physical stress track']
                ]
            }
        ])

    def test_character_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': ('c', 'Test Character'),
                'assertions': [
                    ['Create a new CHARACTER named ***Test Character***', 'Should ask Create Test Character question']
                ]
            },
            {
                'args': ('y',),
                'assertions': [
                    ['YOU ARE CURRENTLY EDITING', 'Should be editing a character'],
                    ['***Test Character*** _(Active)_  _(Character)_', 'Test Character should be the active character'],
                    ['**Fate Points:** 3 (_Refresh:_ 3)', 'Should have defaulted 3 Fate Points'],
                    ['_Physical:_  [   ] [   ] [   ]', 'Physical stress should be added'],
                    ['_Mental:_  [   ] [   ] [   ]', 'Mental stress should be added'],
                    ['[   ] _2_ _Mild_', 'Mild consequences should be added'],
                    ['[   ] _4_ _Moderate_', 'Moderate consequences should be added'],
                    ['[   ] _6_ _Severe_', 'Severe consequences should be added']
                ]
            },
            {
                'args': ('hc', 'High Concept'),
                'assertions': [
                    ['**High Concept:** High Concept', 'Should add and display High Concept']
                ]
            },
            {
                'args': ('t', 'Trouble'),
                'assertions': [
                    ['**Trouble:** Trouble', 'Should add and display Trouble']
                ]
            },
            {
                'args': ('custom', 'Location', 'Earth'),
                'assertions': [
                    ['**Location:** Earth', 'Should add custom Location Earth']
                ]
            },
            {
                'args': ('skill', 'Will', '+4', 'Rapport', '+2', 'Lore', '+1'),
                'assertions': [
                    ['**Skills:**\n        +4 - Will', 'Should add skills']
                ]
            },
            {
                'args': ('skill', 'delete', 'Will'),
                'assertions': [
                    ['Removed Will skill', 'Should remove Will skill']
                ]
            },
            {
                'args': ('skill', 'delete', 'Rapport'),
                'assertions': [
                    ['Removed Rapport skill', 'Should remove Rapport skill']
                ]
            },
            {
                'args': ('skill', 'delete', 'Lore'),
                'assertions': [
                    ['Removed Lore skill', 'Should remove Lore skill']
                ]
            },
            {
                'args': ('approach', 'Fo', '+4', 'Cl', '+2', 'Qu', '+1', 'Sn', '+2', 'Ca', '+1', 'Fl', '0', 'Empathic', '+1'),
                'assertions': [
                    ['**Approaches:**\n        +4 - Forceful', 'Should add approaches']
                ]
            },
            {
                'args': ('aspect', 'Test Aspect'),
                'assertions': [
                    ['***Test Aspect*** _(Aspect)_', 'Should add Test Aspect']
                ]
            },
            {
                'args': ('stunt', 'Test Stunt'),
                'assertions': [
                    ['***Test Stunt*** _(Active)_  _(Stunt)_', 'Should add Test Stunt']
                ]
            },
            {
                'args': ('c', 'stunt', 'character'),
                'assertions': [
                    ['Test Stunt', 'Should ecit Test Stunt']
                ]
            },
            {
                'args': ('st', 't', '1', 'Energy'),
                'assertions': [
                    ['**_Energy_**  [   ]', 'Should add custom Energy stress track']
                ]
            },
            {
                'args': ('st', 'Energy'),
                'assertions': [
                    ['**_Energy_**  [X]', 'Should absorb 1 Energy stress']
                ]
            },
            {
                'args': ('fate', '+'),
                'assertions': [
                    ['**Fate Points:** 1', 'Should add 1 fate point']
                ]
            },
            {
                'args': ('c', 'p'),
                'assertions': [
                    ['Test Character', 'Should edit Test Character']
                ]
            },
            {
                'args': ('st', 't', '4', 'Energy'),
                'assertions': [
                    ['_Energy:_  [   ] [   ] [   ] [   ]', 'Should add custom Energy stress track']
                ]
            },
            {
                'args': ('st', 't', '4', 'Energy'),
                'assertions': [
                    ['_Energy:_  [   ] [   ] [   ] [   ]', 'Should add custom Energy stress track']
                ]
            },
            {
                'args': ('r', 'i', 'Test Stunt'),
                'assertions': [
                    ['_Energy:_  [X] [   ] [   ] [   ]', 'Should absorb 1 custom Energy'],
                    ['**Fate Points:** 2', 'Should spend 1 Fate Point']
                ]
            },
            {
                'args': ('st', 'refresh', 'Energy'),
                'assertions': [
                    ['_Energy:_  [   ] [   ] [   ] [   ]', 'Should refresh Energy']
                ]
            },
            {
                'args': ('fate', 'refresh'),
                'assertions': [
                    ['**Fate Points:** 3', 'Should refresh Fate Points']
                ]
            }
        ])

    def test_character_permissions(self):
        self.send_and_validate_commands(ctx2, [
            {
                'args': ('c','list')
            },
            {
                'args': ('=1',),
                'assertions': [
                    ['***Test Character*** _(Active)_  _(Character)_', 'Test Character should be the active character']
                ]
            },
            {
                'args': ('t','Trouble 2'),
                'assertions': [
                    ['You do not have permission', 'should not allow Test User 2 to edit Test Character']
                ]
            }
        ])

    def test_scenario_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': ('scenario',),
                'assertions': [
                    ['No active scenario or name provided', 'should return no active scenario if empty scenarios'],
                    ['**CREATE or SCENARIO**```css\n.d scenario YOUR_SCENARIOR\'S_NAME```', 'Should include instructions to create scenario']
                ]
            },
            {
                'args': ('scenario', 'Test', 'Scenario'),
                'assertions': [
                    ['Create a new SCENARIO named ***Test Scenario***?', 'should ask question to create scenario named Test Scenario']
                ]
            },
            {
                'args': ('y'),
                'assertions': [
                    ['***Test Scenario*** _(Active Scenario)_', 'should create scenario named Test Scenario']
                ]
            },
            {
                'args': ('scenario', 'desc', 'Test', 'description'),
                'assertions': [
                    ['***Test Scenario*** _(Active Scenario)_  - "Test description"', 'should add a \'Test description\' scenario named Test Scenario']
                ]
            }
        ])

    def test_scene_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': ('scene',),
                'assertions': [
                    ['No active scene or name provided', 'should return no active scene if empty scenes'],
                    ['**CREATE or SCENE**```css\n.d scene YOUR_SCENE\'S_NAME```', 'Should include instructions to create scene']
                ]
            },
            {
                'args': ('Test', 'Scene'),
                'assertions': [
                    ['Create a new SCENE named ***Test Scene***?', 'should ask question to create scene named Test Scene']
                ]
            },
            {
                'args': ('y',),
                'assertions': [
                    ['***Test Scene*** _(Active Scene)_', 'should create scene named Test Scene']
                ]
            },
            {
                'args': ('desc', 'Test', 'description'),
                'assertions': [
                    ['***Test Scene*** _(Active Scene)_  - "Test description"', 'should add a \'Test description\' scene named Test Scene']
                ]
            },
            {
                'args': ('player', 'Test Character'),
                'assertions': [
                    ['Added ***Test Character*** to _Test Scene_ scene', 'should add \'Test Character\' to \'Test Scene\'']
                ]
            },
            {
                'args': ('start',),
                'assertions': [
                    ['_Started On:_', 'should start the scene named Test Scene']
                ]
            }
        ])

    def test_zone_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': ('zone',),
                'assertions': [
                    ['No active zone or name provided\n\n\n**CREATE or ZONE**```css\n.d zone YOUR_ZONE\'S_NAME```', 'should return no active scene if empty scenes and  include instructions to create scene']
                ]
            },
            {
                'args': ('Test', 'Zone'),
                'assertions': [
                    ['Create a new ZONE named ***Test Zone***?', 'should ask question to create zone named Test Zone']
                ]
            },
            {
                'args': ('y',),
                'assertions': [
                    ['***Test Zone*** _(Active Zone)_', 'should create scene named Test Zone']
                ]
            },
            {
                'args': ('desc', 'Test', 'description'),
                'assertions': [
                    ['***Test Zone*** _(Active Zone)_  - "Test description"', 'should add a \'Test description\' scene named Test Zone']
                ]
            }
        ])

    def test_scene_features(self):
        self.send_and_validate_commands(ctx1, [
            {
                'ctx': ctx2,
                'args': ('c', 'npc', 'Test NPC')
            },
            {
                'ctx': ctx2,
                'args': ('scene', 'enter'),
                'assertions': [
                    ['Added ***Test NPC*** to _Test Scene_ scene', 'should add \'Test NPC\' to \'Test Scene\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': ('scene', 'move', 'Test Zone'),
                'assertions': [
                    ['Added ***Test NPC*** to _Test Zone_ zone', 'should move \'Test NPC\' to \'Test Zone\'']
                ]
            },
            {
                'args': ('c', 'Test Character')
            },
            {
                'args': ('scene', 'enter'),
                'assertions': [
                    ['***Test Character*** is already in _Test Scene_', 'should report that  \'Test Character\' is already in \'Test Scene\'']
                ]
            },
            {
                'args': ('scene', 'move', 'Test Zone'),
                'assertions': [
                    ['Added ***Test Character*** to _Test Zone_ zone', 'should move \'Test Character\' to \'Test Zone\'']
                ]
            },
            {
                'args': ('attack', 'NPC', 'Forceful'),
                'assertions': [
                    ['***Test NPC*** faces', 'should display \'Test NPC\' facing an attack'],
                    ['attack from ***Test Character***', 'should display an attack from \'Test Character\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': ('c', 'npc', 'Test NPC')
            },
            {
                'ctx': ctx2,
                'args': ('defend', 'Forceful'),
                'assertions': [
                    [' shifts to absorb', 'should display \'Test NPC\' rolling with shifts to absorb']
                ]
            },
            {
                'ctx': ctx2,
                'args': ('c', 'st', 'Physical'),
                'assertions': [
                    [' left to absorb.', 'should display remaining shifts to absorb']
                ]
            },
            {
                'args': ('scene', 'end',),
                'assertions': [
                    ['_Ended On:_', 'should end the scene named Test Scene']
                ]
            }
        ])
