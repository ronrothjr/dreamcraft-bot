# config.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'


class Setup():
    start = '**CREATE A CHARACTER**```css\n.d new character "YOUR CHARACTER\'S NAME"```\
            \n**Character Help:**```css\n.d c help```**Additional Help:**```css\n.d help```Display condensed game instructions```css\n.d cheat\n.d cheat "SEARCH TEXT"```'

    help = '\n***ADDITIONAL INSTRUCTIONS***\n\
            \n**Character Setup:**```css\n.d c help\n/* Display active character */\n.d character\n.d c```\
            \n**Revisions:**```css\n/* Display a list of revisions to the bot */\n.d revision```\
            \n**Suggestions:**```css\n/* Suggest changes for the bot */\n.d suggest```\
            \n**Undo Help**```css\n.d undo help```\
            \n**Roll Help**```css\n.d roll help```\
            \n**User Setup:**```css\n.d u help\n/* Display user info */\n.d user```\
            \n**Scenario Setup**```css\n.d scenario help\n/* Display active scenario */\n.d scenario```\
            \n**Scene Setup**```css\n.d s help\n/* Display active scene */\n.d scene```\
            \n**Zone Setup**```css\n.d z help\n/* Display active zone */\n.d zone```\
            \n**Engagement Setup**```css\n.d e help\n/* Display active zone */\n.d zone```'

    new_help = '\n***NEW PREFIX INSTRUCTIONS***\n\
            \nHow to use the ***new*** prefix:\n```css\n.d new character "Character Name"\
            \n.d new session "Session Name"\
            \n.d new scenario "Scenario Name\
            \n.d new scene "Scene Name"\
            \n.d new zone "Zone Name"\
            \n.d new conflict "Conflict Name"\
            \n.d new contest "Contest Name"\
            \n.d new challenge "Challenge Name```'

    delete_help = '\n***DELETE PREFIX INSTRUCTIONS***\n\
            \nHow to use the ***delete*** prefix:\n```css\n.d delete skill "NAME"\
            \n.d delete approach "NAME"\
            \n.d delete aspect "NAME"\
            \n.d delete stunt "NAME"\
            \n.d delete stress "NAME"\n.d delete stress title "NAME"\
            \n.d delete consequence "NAME"\n.d delete consequence title "NAME"```'

    undo_help = '\n***UNDO INSTRUCTIONS***\n\
            \n**Log Story:**```css\n.d log story\n/* Display a list of changes */```\n\
            \n**Log Errors:**```css\n.d log errors\n/* Display a list of errors */```\n\
            \n**Undo List:**```css\n.d undo list\n/* Display a list of changes to undo */```\n\
            \n**Undo Last:**```css\n.d undo last\n/* Undo the last change */```\n\
            \n**Redo Next:**```css\n.d redo next\n/* Redo the next change */```'

    roll_help = '\n***Roll Instructions***\n\n\
            Roll fate dice```css\n.d r```\n\
            Roll fate dice and invoke aspects```css\n.d r invoke "ASPECT NAME" [...invoke "ASPECT NAME"]```\n\
            Roll fate dice with active character\'s stat bonus```css\n.d r "APPROACH NAME"|"SKILL NAME"```\n\
            Roll fate dice skill/approach with invokes```css\n.d r "APPROACH NAME"|"SKILL NAME" invoke "ASPECT NAME" +2|rerolll [...invoke "ASPECT NAME" +2|reroll]```\n\
            Reroll the character\'s last roll```css\n.d re invoke "ASPECT NAME" +2|rerolll [...invoke "ASPECT NAME" +2|rerolll]```\n\
            Clear the actions from a previous roll```css\n.d clear\n.d erase```\n\
            Display invocable/compelable aspects```css\n.d available```\n\
            Invoke an aspect and uses the active character\'s fate points```css\n.d invoke "ASPECT NAME" +2|rerolll [...iinvoke "ASPECT NAME" +2|rerolll]```\n\
            Compel aspects and grants the active character a fate point```css\n.d compel "ASPECT NAME" [...ccompel "ASPECT NAME"]```\n\
            Attack another character```css\n.d attack "Character Name" Forceful invoke "Man of Steel"```\n\
            Defend an attack```css\n.d defend /* regular defense roll */\n.d defend Quick /* defense roll with Quick bonus */\n.d defend exact +0 /* defend with a static roll of Mediocre (+0) */```\n\
            Create a boost from a Tie or Succeed with Style outcome```css\n.d boost I Got You Now```\n\
            Takeout a character that cannot absorb stress from an attack```css\n.d npc Mook 1\n.d takeout```'

    user_help = '.d u help - display user help\n\
            \n***User Setup:***\n\
            Display user info```css\n.d user```\n\
            Set user time zone```css\n.d u tz "TIME ZONE NAME"```\n\
            Search the list of time zones```css\n.d u tz list {search}```\n\
            Add contact information```css\n.d u contact "CONTACT INFO".d u contact "\nReddit - u/fuzzywuzzy\nEmail - fuzzy@gmail.com"```\n\
            Create user alias commands```css\n.d u alias punch "c Superman" "attack {target} Forceful invoke Super Punch"\n/* How to use an alias that takes an argument */\n.d punch "Lex Luther"\n.d u alias delete punch /* REMOVES the punch alias */```\n'

    revision_help = '.d revision help - display revision help\n\
            \nRevision Setup:\n\
            Display revision info```css\n.d revision```'

    suggestion_help = '.d suggest help - display suggestion help\n\
            \nSuggestion Setup:\n\
            Make a suggestion```css\n.d suggest "SUGGESTION TEXT"```\n\
            Display the list of suggestions```css\n.d suggest list```'

    character_help = '.d c help - display these instructions\nCharacter Help:\n\
            Display active character```css\n.d character```\n\
            Display character help```css\n.d c help```\n\
            Display help on stress tracks```css\n.d c stress help```\n\
            Display help on consequences and conditions```css\n.d c consequence help```\n\
            Display/set active character```css\n.d c "NAME"```\n\
            Display list of characters```css\n.d c list```\n\
            Set the description for the active character```css\n.d c description "DESCRIPTION TEXT"```\n\
            Set the high concept for the active character```css\n.d c high concept "HIGH CONCEPT TEXT"```\n\
            Set the trouble for the active character```css\n.d c trouble \{trouble\}```\n\
            Removes a character```css\n.d c delete "NAME"```\n\
            Display, refresh, add or subtract fate points```css\n.d c fate refresh|+|-```\n\
            Add/remove aspects```css\n.d c aspect [delete] "ASPECT NAME"```\n\
            Set custom aspect type```css\n.d c aspect delete "ASPECT TYPE"```\n\
            Set the current aspect as the active character```css\n.d c aspect character```\n\
            Add/remove stunts```css\n.d c stunt [delete] "STUNT NAME"```\n\
            Set custom stunt type```css\n.d c stunt delete "STUNT TYPE"```\n\
            Set the current stunt as the active character```css\n.d c stunt character```\n\
            Add/remove approach bonuses```css\n.d c approach [delete] "APPROACH NAME" BONUS```\n\
            Display a list of approach descriptions```css\n.d c approach help```\n\
            Set/remove bonuses```css\n.d c skill [delete] "SKILL NAME" BONUS```\n\
            Display a list of skill descriptions```css\n.d c skill help```\n\
            Share a character```css\n.d c share anyone /* READ-ONLY */\n.d c share to copy /* LET OTHERS COPY */\n.d c share revoke /* TURN OFF SHARING */```\n\
            Copy a character```css\n.d c shared /* VIEW SHARED CHARACTERS */\n.d c copy /* COPIES SELECTED CHARACTER */\n.d c copy to "SERVER NAME" /* COPIES YOUR CHARACTER TO ANOTHER SERVER */```'

    stress_help = '.d c stress help - display these instructions\nStress Help:\n\
            Add stress```css\n.d c stress Mental|Physical 1|2|3```\n\
            Remove stress```css\n.d c stress delete Mental|Physical 1|2|3```\n\
            Create custom stress track```css\n.d c stress title TOTAL STRESS```\n\
            Delete custom stress track```css\n.d c stress title delete stress```\n\
            Add custom stress```css\n.d c stress STRESS TOTAL```\n\
            Clear all stress tracks```css\n.d c stress refresh```\n\
            Clears the titled stress track```css\n.d c stress refresh STRESS```\n\
            Remove custom stress```css\n.d c stress delete stress```\n\
            Reset stress boxes to standard FATE configuration```css\n.d c stress title [FATE|FAE|CORE|None]```'

    consequences_help = '.d c consequence help - display these instructions\nConsequences and Conditions Help:\n\
            Add consequence```css\n.d c conequence Mild|Moderate|Severe "ASPECT NAME"```\n\
            Remove consequence```css\n.d c consequence delete Mild|Moderate|Severe```\n\
            Create condition```css\n.d c consequence title TOTAL "CONDITION NAME"```\n\
            Delete condition```css\n.d c consequence title delete "CONDITION Name"```\n\
            Add condition```css\n.d c consequence "CONDITION Name"```\n\
            Remove condition```css\n.d c consequence delete "CONDITION Name"```\n\
            Reset consequences to standard FATE configuration```css\n.d c consequence title [FATE|FAE|CORE|None]```'

    scenario_help = '.d scenario help - display these instructions\nScenario Help:\n\
            Display active scenario```css\n.d scenario```\n\
            Add/display/set active scenario```css\n.d scenario name "NAME"```\n\
            Display list of scenarios```css\n.d scenario list```\n\
            Set the description for the active scenario```css\n.d scenario description "DESCRIPTION TEXT"```\n\
            Add/remove aspect for active scenario```css\n.d scenario aspect [delete] "ASPECT NAME"```\n\
            Set the current aspect as the active character```css\n.d scenario aspect character```\n\
            Add/remove character for active scenario```css\n.d scenario character [delete] "CHARACTER NAME"```\n\
            Remove a scenario```css\n.d scenario delete "NAME"```'

    scene_help = '.d scene help - display these instructions\nScene Help:\n\
            Display active scene```css\n.d scene```\n\
            Add/display/set active scene```css\n.d new scene "NAME"```\n\
            Display list of scenes```css\n.d scene list```\n\
            Set the description for the active scene```css\n.d scene description "DESCRIPTION TEXT"```\n\
            Add/remove aspect for active scene```css\n.d scene aspect [delete] "ASPECT NAME"```\n\
            Set the current aspect as the active character```css\n.d scene aspect character```\n\
            Add/remove character for active scene```css\n.d scene character [delete] "CHARACTER NAME"```\n\
            Remove a scene```css\n.d scene delete "NAME"```'

    zone_help = '.d z help - display these instructions\nZone Help:\n\
            Display active zone```css\n.d (z)one```\n\
            Add/display/set active zone```css\n.d new z "NAME"```\n\
            Display list of zones```css\n.d z list```\n\
            Set the description for the active zone```css\n.d z description "DESCRIPTION TEXT"```\n\
            Add/remove aspect for active zone```css\n.d z aspect [delete] "ASPECT NAME"```\n\
            Set the current aspect as the active character```css\n.d z aspect character```\n\
            Add/remove character for active zone```css\n.d z character [delete] "CHARACTER NAME"```\n\
            Remove a zone```css\n.d z delete "NAME"```\n\
            Connet two zones within a scene```css\n.d z connect "Zone 1" to "Zone 2"```'

    session_help = '.d session help - display these instructions\nSession Help:\n\
            Display active session```css\n.d session```\n\
            Add/display/set active session```css\n.d new session "NAME"```\n\
            Display list of sessions```css\n.d session list```\n\
            Set the description for the active session```css\n.d session description "DESCRIPTION TEXT"```\n\
            Add/remove aspect for active session```css\n.d session aspect [delete] "ASPECT NAME"```\n\
            Set the current aspect as the active character```css\n.d session aspect character```\n\
            Add/remove character for active session```css\n.d session character [delete] "CHARACTER NAME"```\n\
            Remove a session```css\n.d session delete "NAME"```'

    engagement_help = '.d e help - display these instructions\nEngagement Help:\n\
            Display active engagement```css\n.d (e)ngagement```\n\
            Add/display/set active engagement```css\n.d new e "NAME"```\n\
            Display list of engagements```css\n.d e list```\n\
            Set the description for the active engagement```css\n.d e description "DESCRIPTION TEXT"```\n\
            Add/remove aspect for active engagement```css\n.d e aspect [delete] "ASPECT NAME"```\n\
            Set the current aspect as the active character```css\n.d e aspect character```\n\
            Add/remove character for active engagement```css\n.d e character [delete] "CHARACTER NAME"```\n\
            Remove a engagement```css\n.d e delete "NAME"```'

    approaches = [
        'Careful - pay close attention to detail and take your time.',
        'Flashy - draw attention to you; full of style and panache.',
        'Forceful - not subtle, but brute strength and power.',
        'Sneaky - emphasis on misdirection, stealth, or deceit.',
        'Clever - think fast, solve problems, or devise strategy.',
        'Quick - move fast and with dexterity'
    ]

    skills = [
        'Academics - knowledge, education, science expertise.',
        'Athletics - run, jump, dodge attacks.',
        'Burglary - bypass security, pick pockets, pull off crimes.',
        'Contacts - know the right people & helpful connections.',
        'Crafts - make, build, fix and break things.',
        'Deceive - lie, cheat, impersonate.',
        'Drive - maneuver, race, control vehicles.',
        'Empathy - counsel, spot lies, judge mood & intentions.',
        'Fight - fists or hand-to-hand weapons.',
        'Investigate - find clues, deductions, solve mysteries.',
        'Lore - supernatural knowledge.',
        'Notice - spot details, sense trouble, be perceptive.',
        'Physique - strength, durability, raw power.',
        'Provoke - scare, manipulate, anger, push people.',
        'Rapport - connect with others, build trust & goodwill.',
        'Resources - wealth, borrow or access material things.',
        'Shoot - ranged combat; guns, throwing knives, bows.',
        'Stealth - hide, evade, blend in, go unnoticed, vanish.',
        'Will - resist temptation, withstand trauma, hold steady.'
    ]

    cheats = {
        'On Your Turn': '\n\
 Describe what you’re trying to do.\n\
 Choose the skill & action that fit.\n\
 Roll: 4dF + skill + stunt.\n\
 Optional: invoke aspects \n\
  •  re-roll or add +2 (1 Fate point each)\n\
 Resolve action (see Outcomes/Actions).\n\
  •  Absorb shifts (if attacked).\n\
    – **Stress**:\n\
      • check off stress boxes\n\
      • one box per shift\n\
    – **Consequences**:\n\
      • absorb 2/4/6 shifts\n\
      • create a consequence aspect\n\
      • attacker gets one free invoke\n\
    – **Taken Out**:\n\
      • if you can’t absorb the hit\n\
      • attacker removes you from scene\n\
    – **Concede**:\n\
      • choose before a roll\n\
      • you get a Fate point\n\
      • you choose how to exit scene',
        'OUTCOMES/ACTIONS': '\n\
**Shifts** = \n\
  Your Effort - [Opposing Effort or Target Difficulty]\n\n\
  •  *Fail*: effort < opposition\n\
  •  *Tie*: effort = opposition\n\
  •  *Success*: effort > opposition by 1 or 2\n\
  •  *Success w/ Style*: effort > opp. by 3 or more\n\
**Create an Advantage (CaA)**\n\
     Leverage and create aspects\n\n\
     When creating a new situation aspect\n\
        *Fail*: not created or free enemy invoke\n\
        *Tie*: not created, but free boost\n\
        *Success*: created with free invoke\n\
        *SwS*: created with 2 free invokes\n\n\
     When targeting existing/unknown aspects\n\
        *Fail*: unknown or free enemy invoke\n\
        *Tie*: free invoke on known, boost on unk.\n\
        *Success*: free invoke on aspect\n\
        *SwS*: 2 free invokes on aspect\n',
        'OUTCOMES/ACTIONS (cont.)': '\n\
**Attack**:\n\
     to harm a target\n\
        *Fail*:  you fail to connect\n\
        *Tie*:  you get a boost\n\
        *Success*:  deal a hit equal to shifts\n\
        *SwS*:  may reduce 1 shift for a boost\n\n\
**Defend**:\n\
     to oppose attack or stop foe\n\
        *Fail*: foe succeeds or you take hit\n\
        *Tie*: action’s tie results applies\n\
        *Success*: enemy stopped/missed\n\
        *SwS*: as Success with a boost\n\n\
**Overcome**:\n\
     to clear obstacles or hindrances\n\
        *Fail*: fail or success w/ major cost\n\
        *Tie*: partial succ., at minor cost, or boost\n\
        *Success*: you meet your goal\n\
        *SwS*: as Success with a boost',
        'MAJOR/MINOR COSTS': '\n\
**Major**\n\
     significantly worse or more complicated\n\
     •  introduce new problem\n\
     •  bring in new foes\n\
     •  put PCs on a deadline\n\
     •  mild/moderate consequence\n\
     •  enemy gets situation aspect w/ free invoke\n\
**Minor**\n\
     difficulty or complication, not hindrance\n\
     •  a few points of stress\n\
     •  a boost to the enemy\n\
**Recovery**\n\
     •  stress clears at end of scene\n\
     •  consequences vary:\n\
         roll to overcome using skill\n\
         –  Mild: +2(Fair)\n\
             •   clears in one full scene\n\
         –  Moderate: +4(Great)\n\
             •   clears in one full session\n\
         –  Severe: +6(Fantastic)\n\
             •   clears on major milestone',
        'ASPECTS': '\n\
        Aspects are true. They can grant or withdraw\n\
        permission for what can happen in the story.\n\
        Invoke an aspect to get +2 on a roll, reroll,\n\
        or increase foe’s difficulty by 2.\n\
        Invoking costs a fate point or uses a free invoke.\n\
        Compel an aspect to add complications to a\n\
        character’s circumstances, Player receives fate point\n\
        or spends fate point to deny circumstances.',
        'TYPES OF ASPECTS': '\n\
        **Boost.** Temporary, sometimes unnamed aspect.\n\
            Provides a free invoke. Vanishes once used.\n\
            Can’t be compelled. Can’t be invoked with a fate point.\n\
        **Character.** Aspect on a character sheet.\n\
        **Situation.** Aspect of the scene.\n\
            Lasts only long as the circumstances persist.\n\
        **Organization, Scenario, Setting, Zone.**\n\
            Situation aspects of a group, scene or storyline,\n\
            campaign, or map area, respectively.',
        'ADJECTIVE LADDER': '\n\
        +12  Chuck Norris\n\
        +11  Godly\n\
        +10  Supreme\n\
        +9  Heroic\n\
        +8  Legendary\n\
        +7  Epic\n\
        +6  Fantastic\n\
        +5  Superb\n\
        +4  Great\n\
        +3  Good\n\
        +2  Fair\n\
        +1  Average\n\
        +0  Mediocre\n\
        -1  Poor\n\
        -2  Terrible\n\
        -3  Catastrophic\n\
        -4  Horrific\n\
        -5  Apocolyptic\n\
        -6  Abysmal',
        'SETTING DIFFICULTY': '\n\
        **Low** = below relevant PC skill\n\
        **Medium** =  close to PC skill\n\
        **High** = higher than PC skill\n\
        **Not tough** = Mediocre (0) or don’t roll.\n\
        +2 for tough, +2 for each extra factor against them.\n\
        Consult aspects to adjust. Use adjective ladder as guide.',
        'TEAMWORK OPTIONS': '\n\
        _Combine Skills._ Character with highest skill rolls. \n\
            PCs with same skill at Average (+1) or better use action to add +1.\n\
            Max bonus is highest skill rating.\n\
            Supporters face same costs & consequences as the PC who rolls.\n\
        _On your turn._ Create an advantage & let allies\n\
            use the free invokes on their turns.\n\
        _Outside your turn._ Invoke an aspect to add a bonus to an ally’s roll.',
        'TURN ORDER': '\n\
            At the start, everyone decides who goes first.\n\
            After acting, player chooses who goes next.\n\
            GM’s characters are in the turn order just like the PCs.\n\
            Last player to go picks who starts next.',
        'EARN FATE POINTS WHEN YOU': '\n\
  •  Accept a compel.\n\
  •  Have your aspectsinvoked.\n\
  •  Concede a conflict.',
        'SPEND FATE POINTS TO': '\n\
  •  Invoke an aspect.\n\
  •  Power a stunt.\n\
  •  Refuse a compel.\n\
  •  Declare a story detail.',
        'CHALLENGES': '\n\
        GM picks a number of skills representing the tasks needed to beat the challenge.\n\
        Number of tasks roughly equals the number of players.\n\
        Each player picks a task and rolls skill to overcome.\n\
        GM considers mix of results to determine outcome.',
        'CONTESTS': '\n\
        Take place over a series of exchanges.\n\
        Each side takes an overcome action for their goals.\n\
        Only one character from each side makes the roll.\n\
        Each participant may try to Create an Advantage (CaA)\n\
        in addition to rolling or combining skills.\n\
        On failed CaA, forfeit roll or give over free invoke.\n\
        At end of exchange, side with highest effort gains 1 victory\n\
        Success with Style gains 2 victories.\n\
        If harm is allowed, absorb shifts as stress.\n\
        Tie results in unexpected twist - GM describes.\n\
        First side to 3 victories (as GM determines) wins.',
        'CONFLICTS': '\n\
        When violence/coercion is an option and each side could harm the other.\n\
        Takes place over a series of exchanges. Each character acts in turn order (as On Your Turn).\n\
        Defenders roll to oppose. Conflict ends when one side concedes or is taken out.\n\
        Players who concede each take a fate point. GM also pays players hostile invoke fate points.'
    }

    timezone = 'America/New_York'
    fate_dice = {'-1': '-', '0': 'b', '1': '+'}
    x = '[X]'
    o = '[   ]'
    stress = [[['1', o],['1', o],['1', o]],[['1', o],['1', o],['1', o]]]
    stress_FAE = [[['1', o]],[['2', o]],[['3', o]]]
    stress_Core = [[['1', o],['1', o]],[['1', o],['1', o]]]
    stress_categories = ['Stress', 'Stress']
    stress_titles = ['Physical', 'Mental']
    stress_titles_FAE = ['1', '2', '3']
    stress_titles_Core = ['Physical', 'Mental']
    consequences = [['2', o],['4', o],['6', o]]
    consequences_categories = ['Consequences', 'Consequences', 'Consequences']
    consequences_titles = ['Mild', 'Moderate', 'Severe']
    consequence_shifts = ['2', '4', '6']
    fate_ladder = {
        'a12': 'Chuck Norris',
        'a11': 'Godly',
        'a10': 'Supreme',
        'a9': 'Heroic',
        'a8': 'Legendary',
        'a7': 'Epic',
        'a6': 'Fantastic',
        'a5': 'Superb',
        'a4': 'Great',
        'a3': 'Good',
        'a2': 'Fair',
        'a1': 'Average',
        'a0': 'Mediocre',
        'b1': 'Poor',
        'b2': 'Terrible',
        'b3': 'Catastrophic',
        'b4': 'Horrific',
        'b5': 'Apocolyptic',
        'b6': 'Abysmal'
    }
    reserved_commands = [
        'help',
        'channel', 'chan', 'list', 'users', 'u',
        'character', 'c', 'note', 'n', 'say', 'story', 'stats', 'parent', 'p', 'new', 'name', 'n', 'select', 'image', 'list', 'l', 'delete', 'restore', 'copy', 'description', 'desc', 'high', 'hc', 'trouble', 't', 'fate', 'f', 'aspects', 'aspect', 'a', 'boost', 'b', 'approaches', 'approach', 'apps', 'app', 'skills', 'skill', 'sks', 'sk', '', 'stunts', 'stunt', 's', 'stress', 'st', 'consequence', 'con', 'custom', 'share', 'shared',
        'cheat',
        'engagement', 'e', 'players', 'player', 'p', 'opposition', 'opp', 'o', 'start', 'end',
        'roll', 'r', 'reroll', 're', 'create', 'advantage', 'attack', 'att', 'defend', 'def', 'overcome', 'takeout', 'out', 'freeinvoke', 'available', 'avail', 'av',
        'scenario', 'scene', 's', 'session', 'zone', 'connect', 'adjoin', 'ajoin', 'join', 'j', 'enter', 'move', 'exit',
        'suggest', 'suggestion', 'revision', 'rev',
        'undo', 'errors', 'error', 'err', 'e', 'last', 'next',
        'user', 'timezone', 'tz', 'url', 'website', 'contact', 'alias'
    ]
    action_caa_image = 'http://drive.google.com/uc?export=view&id=14r8yVHdvbghvmwlZ-LU_GCv_Rss3CuJd'
    action_attack_image = 'http://drive.google.com/uc?export=view&id=15AZkpFEuKLtiFRm0dI7c4DFO6ut3ZizX'
    action_defend_image = 'http://drive.google.com/uc?export=view&id=15OXNLIphfNJLqZU9gXlnS8Un7m7qHxtf'
    action_overcome_image = 'http://drive.google.com/uc?export=view&id=1hgT8yLTYK3JHsp_N4Meg2qOUbh6AdDz8'