# test.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'

import unittest
from mongoengine import connect, disconnect
import tests

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(tests.TestDreamcraftBotE2E('test_user_setup'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_user_2_setup'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_npc_character_creation'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_character_creation'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_character_permissions'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_session_creation'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_scenario_creation'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_scene_creation'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_zone_creation'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_scene_features'))
    suite.addTest(tests.TestDreamcraftBotE2E('test_end_delete_components'))

    results = unittest.TestResult()

    connect('mongoenginetest', host='mongomock://localhost')
    suite.run(results)
    disconnect()

    print(results)