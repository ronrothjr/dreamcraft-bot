# config.py

class Setup():
    help = '.d - display these instructions\nDreamcraft Bot:\n\
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

    fate_dice = {'-1': '-', '0': 'b', '1': '+'}
