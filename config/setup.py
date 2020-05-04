# config.py

class Setup():
    help = 'Dreamcraft Bot:\n\.d - display these instructions\n.d cheat {search} - display condensed game instructions\n\
            \nCharacter Setup:\n\
            .d (c)haracter - display active character\n\
            .d c help - display character help\n\
            \nScene Setup\n\
            .d (s)cene - display active scene\n\
            .d s help - display scene help\n\
            \nRoll Fate Dice\n\
            .d r - roll fate dice\n\
            .d r {approach|skill} - roll fate dice with active character\'s stat bonus\n\
            .d r {approach|skill} (i)nvoke {aspect} [...(i)nvoke {aspect}] - roll fate dice with active character\'s stat bonus\n\
            .d r compel {aspect} - compels an aspect and grants the active character a fate point\n\
            .d re - reroll the character\'s last roll'

    character_help = '.d c help - display these instructions\nCharacter Help:\n\
            .d (c)haracter - display active character\n\
            .d c help - display character help\n\
            .d c (n)ame \{name\} - display/set active character\n\
            .d c (l)ist - display list of characters\n\
            .d c (desc)ription \{description\} - set the description for the active character\n\
            .d c (high/hc) concept \{high concept\} - set the high concept for the active character\n\
            .d c (t)rouble \{trouble\} - set the trouble for the active character\n\
            .d c (d)delete \{name} - removes a character\n\
            .d c (f)ate {refresh|+|-} - display, refresh, add or subtract fate points\n\
            .d c (a)spect [(d)elete] \{aspect} - add/remove aspects\n\
            .d c (s)tunt [(d)elete] \{stunt} - add/remove stunts\n\
            .d c (app)roach [(d)elete] \{approach\} \{bonus\} - add/remove approach bonuses\n\
            .d c (app)roach help - display a list of approach descriptions\n\
            .d c (sk)ill [(d)elete] \{skill\} \{bonus\} - set/remove bonuses\n\
            .d c (sk)ill help - display a list of skill descriptions'

    scene_help = '.d s help - display these instructions\nScene Help:\n\
            .d (s)cene - display active scene\n\
            .d s (n)ame \{name\} - add/display/set active scene\n\
            .d s (l)ist - display list of scenes\n\
            .d s (desc)ription \{description\} - set the description for the active scene\n\
            .d s (a)spect [(d)elete] \{aspect} - add/remove aspect for active scene\n\
            .d s (c)haracter [(d)elete] \{character} - add/remove character for active scene\n\
            .d s (d)delete \{name} - removes a scene'

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
 Optional: invoke aspect(s) \n\
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
        *Success*:  deal a hit equal to shift(s)\n\
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
        -4  Horrifying',
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

    fate_dice = {'-1': '-', '0': 'b', '1': '+'}