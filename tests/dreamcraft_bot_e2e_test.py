# dreamcraft_bot_e2e_test.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import unittest
from handlers import DreamcraftHandler
from mocks import CTX

ctx1 = CTX('Test Guild 1', 'Test User 1', 'bot_testing')
ctx2 = CTX('Test Guild 1', 'Test User 2', 'bot_testing')
ctx3 = CTX('Test Guild 2', 'Test User 1', 'bot_spamming')
ctx4 = CTX('Test Guild 3', 'Test User 3', 'bot_spamming')

class TestDreamcraftBotE2E(unittest.TestCase):

    def send_and_validate_commands(self, ctx, commands):
        for command in commands:
            complete_messages = []
            for arg  in command['args']:
                messages = []
                self.print_command('Command: ' + ' '.join(arg), '-')
                handler = DreamcraftHandler(command['ctx'] if 'ctx' in command else ctx, arg)
                messages.extend(handler.get_messages())
                [print(message) for message in messages]
                complete_messages.extend(messages)
            if 'assertions' in command:
                [self.assert_command(complete_messages, a[0], a[1]) for a in command['assertions']]

    def assert_command(self, messages, assert_str, err_str):
        assert_test = assert_str in ''.join(messages)
        assert_result = (f'Passed: ' if assert_test else 'Failed: ') + err_str
        self.print_command(assert_result)
        self.assertTrue(assert_test, err_str)

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
            }
        ])

    def test_user_2_setup(self):
        self.send_and_validate_commands(ctx2, [
            {
                'args': [('user', 'timezone', 'America/New_York')],
                'assertions': [
                    ['Saved time zone as ***America/New_York***', 'should save user time_zone as New York']
                ]
            }
        ])

    def test_npc_character_creation(self):
        self.send_and_validate_commands(ctx2, [  
            {
                'args': [('c',)],
                'assertions': [
                    ['No active character or name provided', 'should return no active character if empty characters'],
                    ['CREATE or SELECT A CHARACTER', 'Should include instructions to create character']
                ]
            },
            {
                'args': [('npc', 'Test', 'NPC')],
                'assertions': [
                    ['Create a new CHARACTER named ***Test NPC***', 'Should ask Create Test NPC question']
                ]
            },
            {
                'args': [('y',)],
                'assertions': [
                    ['YOU ARE CURRENTLY EDITING', 'Should be editing a character'],
                    ['***Test NPC*** _(Active)_  _(Nonplayer Character)_', 'Test NPC should be the active character']
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
            }
        ])

    def test_character_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('c', 'Test Character 1')],
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
                'args': [('skill', 'Will', '+4', 'Rapport', '+2', 'Lore', '+1')],
                'assertions': [
                    ['**Skills:**\n        +4 - Will', 'Should add skills']
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
                'args': [('skill', 'delete', 'Lore')],
                'assertions': [
                    ['Removed Lore skill', 'Should remove Lore skill']
                ]
            },
            {
                'args': [('approach', 'Fo', '+4', 'Cl', '+2', 'Qu', '+1', 'Sn', '+2', 'Ca', '+1', 'Fl', '0', 'Empathic', '+1')],
                'assertions': [
                    ['**Approaches:**\n        +4 - Forceful', 'Should add approaches']
                ]
            },
            {
                'args': [('aspect', 'Test Aspect')],
                'assertions': [
                    ['***Test Aspect*** _(Aspect)_', 'Should add Test Aspect']
                ]
            },
            {
                'args': [('stunt', 'Test Stunt')],
                'assertions': [
                    ['***Test Stunt*** _(Active)_  _(Stunt)_', 'Should add Test Stunt']
                ]
            },
            {
                'args': [('c', 'stunt', 'character')],
                'assertions': [
                    ['Test Stunt', 'Should ecit Test Stunt']
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
                'args': [('r', 'i', 'Test Stunt')],
                'assertions': [
                    ['_Energy:_  [X] [   ] [   ] [   ]', 'Should absorb 1 custom Energy'],
                    ['**Fate Points:** 2', 'Should spend 1 Fate Point']
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
                    ['You do not have permission', 'should not allow Test User 2 to edit Test Character 1']
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
                    ('c', 'Test Character 2'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test Character 2*** _(Active)_  _(Character)_', 'Test Character 2 should be the active character']
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
                    ['***Test Aspect*** _(Aspect)_', 'Should have Test Aspect'],
                    ['***Test Stunt*** _(Stunt)_', 'Should have Test Stunt']
                ]
            }
        ])

    def test_session_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('session',)],
                'assertions': [
                    ['No active session or name provided', 'should return no active session if empty sessions'],
                    ['**CREATE or SESSION**```css\n.d session YOUR_SESSION\'S_NAME```', 'Should include instructions to create session']
                ]
            },
            {
                'args': [
                    ('session', 'Test', 'Session'),
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
                'args': [('scenario',)],
                'assertions': [
                    ['No active scenario or name provided', 'should return no active scenario if empty scenarios'],
                    ['**CREATE or SCENARIO**```css\n.d scenario YOUR_SCENARIOR\'S_NAME```', 'Should include instructions to create scenario']
                ]
            },
            {
                'args': [('scenario', 'Test', 'Scenario')],
                'assertions': [
                    ['Create a new SCENARIO named ***Test Scenario***?', 'should ask question to create scenario named Test Scenario']
                ]
            },
            {
                'args': [('y',)],
                'assertions': [
                    ['***Test Scenario*** _(Active Scenario)_', 'should create scenario named Test Scenario']
                ]
            },
            {
                'args': [('scenario', 'desc', 'Test', 'description')],
                'assertions': [
                    ['***Test Scenario*** _(Active Scenario)_  - "Test description"', 'should add a \'Test description\' scenario named Test Scenario']
                ]
            }
        ])

    def test_scene_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('scene',)],
                'assertions': [
                    ['No active scene or name provided', 'should return no active scene if empty scenes'],
                    ['**CREATE or SCENE**```css\n.d scene YOUR_SCENE\'S_NAME```', 'Should include instructions to create scene']
                ]
            },
            {
                'args': [('Test', 'Scene')],
                'assertions': [
                    ['Create a new SCENE named ***Test Scene***?', 'should ask question to create scene named Test Scene']
                ]
            },
            {
                'args': [('y',)],
                'assertions': [
                    ['***Test Scene*** _(Active Scene)_', 'should create scene named Test Scene']
                ]
            },
            {
                'args': [('desc', 'Test', 'description')],
                'assertions': [
                    ['***Test Scene*** _(Active Scene)_  - "Test description"', 'should add a \'Test description\' scene named Test Scene']
                ]
            },
            {
                'args': [('player', 'Test Character 1')],
                'assertions': [
                    ['Added ***Test Character 1*** to _Test Scene_ scene', 'should add \'Test Character 1\' to \'Test Scene\'']
                ]
            },
            {
                'args': [('start',)],
                'assertions': [
                    ['_Started On:_', 'should start the scene named Test Scene']
                ]
            }
        ])

    def test_zone_creation(self):
        self.send_and_validate_commands(ctx1, [
            {
                'args': [('zone',)],
                'assertions': [
                    ['No active zone or name provided\n\n\n**CREATE or ZONE**```css\n.d zone YOUR_ZONE\'S_NAME```', 'should return no active scene if empty scenes and  include instructions to create scene']
                ]
            },
            {
                'args': [('Test', 'Zone', '1')],
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
                'args': [
                    ('z', 'Test', 'Zone', '2'),
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
                    ['***Test Zone 1*** and ***Test Zone 2*** are now adjoined in ***Test Scene***', 'should adjoin \'Test Zone 1\' and \'Test Zone 2\''],
                    ['***Test Zone 1*** and ***Test Zone 2*** are already adjoined in ***Test Scene***', 'should warn that \'Test Zone 1\' and \'Test Zone 2\' are already adjoined']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'npc', 'Test NPC'),
                    ('scene', 'enter')
                ],
                'assertions': [
                    ['Added ***Test NPC*** to _Test Scene_ scene', 'should add \'Test NPC\' to \'Test Scene\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('scene', 'move', 'Test Zone 1')],
                'assertions': [
                    ['***Test NPC*** is already in the _Test Zone 1_ zone', 'should show \'Test NPC\' is already in \'Test Zone 1\'']
                ]
            },
            {
                'args': [
                    ('engagement', 'Conflict', 'Test Conflict'),
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
                    ['Added ***Test NPC*** to the opposition in the _Test Conflict_ engagement', 'should add \'Test NPC\' to the conflict']
                ]
            },
            {
                'args': [
                    ('c', 'Test Character 1'),
                    ('scene', 'enter')
                ],
                'assertions': [
                    ['***Test Character 1*** is already in _Test Scene_', 'should report that  \'Test Character 1\' is already in \'Test Scene\'']
                ]
            },
            {
                'args': [('scene', 'move', 'Test Zone 1')],
                'assertions': [
                    ['***Test Character 1*** is already in the _Test Zone 1_ zone', 'should show \'Test Character 1\' is already in \'Test Zone 1\'']
                ]
            },
            {
                'args': [('attack', 'NPC', 'Forceful')],
                'assertions': [
                    ['***Test NPC*** faces', 'should display \'Test NPC\' facing an attack'],
                    ['attack from ***Test Character 1***', 'should display an attack from \'Test Character 1\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'npc', 'Test NPC'),
                    ('defend', 'Forceful')
                ],
                'assertions': [
                    [' shifts to absorb', 'should display \'Test NPC\' rolling with shifts to absorb']
                ]
            },
            {
                'ctx': ctx2,
                'args': [('c', 'st', 'Physical')],
                'assertions': [
                    [' left to absorb.', 'should display remaining shifts to absorb']
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
                    ['***Test Character 1*** removed from _Test Scene_', 'should remove \'Test Character 1\' from \'Test Scene\'']
                ]
            },
            {
                'ctx': ctx2,
                'args': [
                    ('c', 'npc', 'Test NPC'),
                    ('scene', 'exit')
                ],
                'assertions': [
                    ['***Test NPC*** removed from _Test Scene_', 'should remove \'Test NPC\' from \'Test Scene\'']
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
                    ['_Ended On:_', 'should end the scene named Test Scene']
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
                'args': [('scene', 'delete')],
                'assertions': [
                    ['***Test Scene*** removed', 'should remove \'Test Scene\'']
                ]
            },
            {
                'args': [('scenario', 'delete')],
                'assertions': [
                    ['***Test Scenario*** removed', 'should remove \'Test Scenario\'']
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
                    ['You cannot copy your own shared character', 'should warn that you cannot copy your own shared character']
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
                    ('c', 'npc', 'Test NPC'),
                    ('c', 'delete'),
                    ('y',)
                ],
                'assertions': [
                    ['***Test NPC*** removed', 'should archive \'Text NPC\'']
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
                    ['***Test Aspect*** _(Aspect)_', 'Should have Test Aspect'],
                    ['***Test Stunt*** _(Active)_  _(Stunt)_', 'Should have Test Stunt']
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
                    ('c', 'name', 'Test Character 1'),
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
                    ['***Test Aspect*** _(Aspect)_', 'should have Test Aspect'],
                    ['***Test Stunt*** _(Active)_  _(Stunt)_', 'should have Test Stunt']
                ]
            }
        ])
