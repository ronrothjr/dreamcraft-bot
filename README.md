# DREAMCRAFT BOT


#### Fate CLI is a Discord bot that will cover the complete features of the Fate Condensed, FAE and Core Systems.

**_Bold italics Indicates that the feature has not yet been implemented_**


## This Command Line Interface (CLI) allows users to:



*   Get help with condensed game instructions.
*   Run commands for selecting, viewing, and editing all FATE game components.
    *   Sessions, scenarios, scenes, and zones are confined to a channel.
    *   Characters are free to be used in any channel on the Discord server.
*   Setup users for local timezone display of all dates.
*   Create customizable character sheets for PCs and NPCs:
    *   Description, high concept, trouble, images.
    *   Aspects, stunts, refresh, and fate points.
    *   **_Allow nested stunts that upgrade the original._**
    *   **_Spend/award refresh when adding/removing stunts._**
    *   Custom character fields.
    *   Standard and custom skills/approacches.
    *   Standard and custom tracks for stress, consequences, and conditions.
    *   **_Enforce character creation rules (stunt refresh, selection of specific stunts)._**
    *   **_Character templates for PCs and NPCs to use during character creation._**
*   Manage all aspects and stunts as if they were characters (FATE Fractal/Bronze Rule).
*   Create zones, scenes, scenarios, and sessions, which can be treated as characters.
*   Manage contests, challenges, and conflicts within zones, scenes, sessions, and sessions.
    *   Start and end sessions and scenes.
    *   Enter and exit zones within scenes.
    *   Connect zones to each other.
    *   Add/move characters to zones and scenes.
    *   Display invokable/compellable aspects and stunts.
    *   Roll fate dice using character skills/approaches with invocation of aspects and stunts.
    *   Resolve rolls by consuming/awarding fate points.
        *   Handle reroll with invokes/compels
        *   **_Manage Defend, Overcome, and Create an Advantage results_**
        *   **_Add assisting with rolls._**
        *   **_Add succeed with style._**
        *   **_Add boosts with free invokes_**
        *   **_Add concede before rolling to award fate point(s)._**
        *   **_Apply passive stunt resolutions._**
            *   **_Add automatic bonuses and defenses_**
            *   **_Handle situational requirements_**
    *   **_Enforce limits on stunts._**
    *   Apply triggers for actions using aspects and stunts
        *   Absorb stress **_or take out target_**
        *   **_Inflict/heal consequences with aspects and GM free invokes_**
        *   **_Add/remove aspects with and without Free Invoke(s)_**
        *   **_Remove used boosts and free invokes on aspects_**
    *   **_Handle conflicts, contests, and challenges._**
        *   **_Start, setup, run through, and end._**
        *   **_Track turn order within exchanges._**
        *   **_Manage available targets and roll/defend with stress/consequence/aspect resolution._**
        *   **_Handle transitions for PCs as they move, are taken out, and concede._**
            *   **_Aspects that expire upon scene exit_**
            *   **_Stunts that are triggered by moving, taking out, or conceding_**
*   Record notes, character dialog, and scene narration to read back and view them within the context of their scenes within scenarios.
*   Archive and restore of all character-based game components.
*   Undo/redo for viewing all a log of changes and returning to a previous point in time to alter history on a new timeline.
*   Copy and backup characters to Private Message channel and to other servers.


## Enhancements List:


### Items on this list are slated for development during Beta testing



*   Schedule and record sessions with invites to and acceptance from players
*   Improved instructions
    *   Improve instructions for aspects and stunts
    *   Character copy to guild
*   Lists Upgrade:
    *   reorder lists in character sheet
    *   display descriptions only in lists
*   NPCs Character Upgrade:
    *   allow customized consequences tracks
    *   different instructions for NPCs
*   Aspects Upgrade
    *   allow aspect types
    *   consequences create aspects unless changed to conditions
*   Enable Assets Upgrade:
    *   Look up Jade Punk assets system
*   Create Stunt Builder:
    *   stunt actions triggered:
        *   when using one or more stunts
        *   when creating advantage
        *   when defending
        *   when active/full defense
        *   when rolling a skill/approach
        *   when assisting others
        *   when conditions are added
        *   when stress is absorbed
        *   when specific aspects are invoked
        *   when a stress track is exhausted
        *   when scenario/session/scene start or end
        *   when entering or exiting zone
        *   when milestone is reached
    *   stunt resolutions:
        *   apply/remove stress
        *   apply/remove consequences
        *   apply/remove conditions
        *   spend fate point(s)
        *   add bonus to specific skill/approach roll
        *   create specific aspect
        *   create specific aspect w/ free invoke(s)
        *   remove specific aspect
    *   stunt limitations:
        *   once/twice/thrice per zone/scene/session/scenario
        *   requires avilable points on stress track
        *   requires fate point(s)
        *   requires specific action
        *   requires specific skill
        *   requires specific situation/circumstance


## Technical Goals:



*   Add comments and docstrings
*   Update README with complete usage and developer setup instructions
*   Replace timestamps with custom save hooks in mongoengineAdd setuptools files for easy install of dreacraft-bot for local development
    *   [https://pypi.org/project/setuptools/](https://pypi.org/project/setuptools/)
    *   [https://setuptools.readthedocs.io/en/latest/easy_install.html](https://setuptools.readthedocs.io/en/latest/easy_install.html)
*   Research use of Cogs and how to apply to dreamcraft-bot:
    *   [https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html#ext-commands-cogs](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html#ext-commands-cogs)
    *   [https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be](https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be)
*   Research distutils to create dreamcraft-bot as a package:
    *   [https://docs.python.org/3/distutils/introduction.html](https://docs.python.org/3/distutils/introduction.h



# HELP COMMANDS

`.d`

### Dreamcraft Bot:
* `.d` - display these instructions
* `.d` cheat {search} - display condensed game instructions

### User Setup:
* `.d (u)ser` - display user info
* `.d u help` - display user help

### Character Setup:
* `.d (c)haracter` - display active character
* `.d c help` - display character help

### Roll Fate Dice
* `.d r` - roll fate dice
* `.d r (i)nvoke {aspect}` [...(i)nvoke {aspect}] - roll fate dice and apply
* `.d r {approach|skill}` - roll fate dice with active character's stat bonus
* `.d r {approach|skill} (i)nvoke {aspect} (+2|reroll) [...(i)nvoke {aspect} (+2|reroll)]` - roll fate dice with active character's stat bonus
* `.d re (i)nvoke {aspect} (+2|reroll) [...(i)nvoke {aspect} (+2|reroll)]` - reroll the character's last roll
* `.d (av)ailable` - display invocable/compelable aspects
* `.d (i)nvoke {aspect} (+2|reroll) [...(i)invoke {aspect} (+2|reroll)]` - invokes an aspect and uses the active character's fate point(s)
* `.d compel {aspect} [...(c)compel {aspect}]` - compels aspect(s) and grants the active character a fate point

### Scenario Setup
* `.d scenario help` - display active scenario

### Scene Setup
* `.d (s)cene` - display active scene
* `.d s help` - display scene help

### Zone Setup
* `.d (z)oen` - display active zone
* `.d z help` - display scene help

### User Setup:
`.d u help` - display user help
* `.d (u)ser` - display user info
* `.d u tz {timezone}` - set user time zone
* `.d u tz (l)ist {search}` - search the list of time zones

### Character Help:
`.d c help` - display these instructions
* `.d (c)haracter` - display active character
* `.d c help` - display character help
* `.d c (st)ress help` - display help on stress tracks
* `.d c (con)sequence help` - display help on consequences and conditions
* `.d c {name}` - display/set active character
* `.d c (l)ist` - display list of characters
* `.d c (desc)ription {description}` - set the description for the active character
* `.d c (high/hc) concept {high concept}` - set the high concept for the active character
* `.d c (t)rouble {trouble}` - set the trouble for the active character
* `.d c (d)delete {name}` - removes a character
* `.d c (f)ate {refresh|+|-}` - display, refresh, add or subtract fate points
* `.d c (a)spect [(d)elete] {aspect}` - add/remove aspects
* `.d c (a)spect (c)character` - set the current aspect as the active character
* `.d c (s)tunt [(d)elete] {stunt}` - add/remove stunts
* `.d c (s)tunt (c)character` - set the current stunt as the active character
* `.d c (app)roach [(d)elete] {(ap)proach} {bonus} [{(ap)proach} {bonus}...]` - add/remove approach bonuses
* `.d c (app)roach help` - display a list of approach descriptions
* `.d c (sk)ill [(d)elete] {(sk)ill} {bonus} [{(sk)ill} {bonus}...]` - set/remove bonuses
* `.d c (sk)ill help` - display a list of skill descriptions

### Stress Help:
`.d c (st)ress help` - display these instructions
* `.d c (st)ress (m)ental|(p)hysical {1,2,3...}` - add stress
* `.d c (st)ress (d)elete (m)ental|(p)hysical {1,2,3...}` - remove stress
* `.d c (st)ress (t)itle {1,2,3...} {stress}` - create custom stress track
* `.d c (st)ress (t)itle (d)elete {(st)ress}` - delete custom stress track
* `.d c (st)ress {(st)ress} {1,2,3}`- add custom stress
* `.d c (st)ress (r)efresh` - clears all stress tracks
* `.d c (st)ress (r)efresh {(st)ress}` - clears the titled stress track
* `.d c (st)ress (d)elete {(st)ress}` - remove custom stress
* `.d c (st)ress (t)itle FATE` - reset stress boxes to standard FATE configuration

### Consequences and Conditions Help:
`.d c (con)sequence help` - display these instructions
* `.d c (con)sequence (mi)ld|(mo)derate|(se)vere {aspect}` - add consequence
* `.d c (con)sequence (d)elete (mi)ld|(mo)derate|(s)evere` - remove consequence
* `.d c (con)sequence (t)itle {1,2,3...} {condition}` - create condition
* `.d c (con)sequence (t)itle (d)elete {(co)ndition}` - delete condition
* `.d c (con)sequence {(co)ndition}` - add condition
* `.d c (con)sequence (d}elete {(co)ndition}` - remove condition
* `.d c (con)sequence (t)itle FATE` -reset consequences to standard FATE configuration

### Scenario Help:
`.d scenario help` - display these instructions
* `.d scenario` - display active scenario
* `.d scenario (n)ame {name}` - add/display/set active scenario
* `.d scenario (l)ist` - display list of scenarios
* `.d scenario (desc)ription {description}` - set the description for the active scenario
* `.d scenario (a)spect [(d)elete] {aspect}` - add/remove aspect for active scenario
* `.d scenario (a)spect (c)character` - set the current aspect as the active character
* `.d scenario (c)haracter [(d)elete] {character}` - add/remove character for active scenario
* `.d scenario (d)delete {name}` - removes a scenario

### Scene Help:
`.d s help` - display these instructions
* `.d (s)cene` - display active scene
* `.d s (n)ame {name}` - add/display/set active scene
* `.d s (l)ist` - display list of scenes
* `.d s (desc)ription {description}` - set the description for the active scene
* `.d s (a)spect [(d)elete] {aspect}` - add/remove aspect for active scene
* `.d s (a)spect (c)character` - set the current aspect as the active character
* `.d s (c)haracter [(d)elete] {character}` - add/remove character for active scene
* `.d s (d)delete {name}` - removes a scene

### Zone Help:
`.d z help` - display these instructions
* `.d (z)one` - display active zone
* `.d z (n)ame {name}` - add/display/set active zone
* `.d z (l)ist` - display list of zones
* `.d z (desc)ription {description}` - set the description for the active zone
* `.d z (a)spect [(d)elete] {aspect}` - add/remove aspect for active zone
* `.d z (a)spect (c)character` - set the current aspect as the active character
* `.d z (c)haracter [(d)elete] {character}` - add/remove character for active zone
* `.d z (d)delete {name}` - removes a zone

### APPROACHES:
* `.d character approach help`
* `.d c app help`
* Careful - pay close attention to detail and take your time.
* Flashy - draw attention to you; full of style and panache.
* Forceful - not subtle, but brute strength and power.
* Sneaky - emphasis on misdirection, stealth, or deceit.
* Clever - think fast, solve problems, or devise strategy.
* Quick - move fast and with dexterity

### SKILLS:
* `.d character skills help`
* `.d c sk help`
* Academics - knowledge, education, science expertise.
* Athletics - run, jump, dodge attacks.
* Burglary - bypass security, pick pockets, pull off crimes.
* Contacts - know the right people & helpful connections.
* Crafts - make, build, fix and break things.
* Deceive - lie, cheat, impersonate.
* Drive - maneuver, race, control vehicles.
* Empathy - counsel, spot lies, judge mood & intentions.
* Fight - fists or hand-to-hand weapons.
* Investigate - find clues, deductions, solve mysteries.
* Lore - supernatural knowledge.
* Notice - spot details, sense trouble, be perceptive.
* Physique - strength, durability, raw power.
* Provoke - scare, manipulate, anger, push people.
* Rapport - connect with others, build trust & goodwill.
* Resources - wealth, borrow or access material things.
* Shoot - ranged combat; guns, throwing knives, bows.
* Stealth - hide, evade, blend in, go unnoticed, vanish.
* Will - resist temptation, withstand trauma, hold steady.

# CHEAT CARDS
`.d cheat {search}`
### On Your Turn
1. Describe what you’re trying to do.
1. Choose the skill & action that fit.
1. Roll: 4dF + skill + stunt.
1. Optional: invoke aspect(s) - re-roll or add +2 (1 Fate point each)
1. Resolve action (see Outcomes/Actions). - Absorb shifts (if attacked).
            – **Stress**:
              • check off stress boxes
              • one box per shift
            – **Consequences**:
              • absorb 2/4/6 shifts
              • create a consequence aspect
              • attacker gets one free invoke
            – **Taken Out**:
              • if you can’t absorb the hit
              • attacker removes you from scene
            – **Concede**:
              • choose before a roll
              • you get a Fate point
              • you choose how to exit scene

### OUTCOMES/ACTIONS

        **Shifts** = 
          Your Effort - [Opposing Effort or Target Difficulty]
          
          •  *Fail*: effort < opposition
          •  *Tie*: effort = opposition
          •  *Success*: effort > opposition by 1 or 2
          •  *Success w/ Style*: effort > opp. by 3 or more
        
        **Create an Advantage (CaA)**
             Leverage and create aspects
        
             When creating a new situation aspect
                *Fail*: not created or free enemy invoke
                *Tie*: not created, but free boost
                *Success*: created with free invoke
                *SwS*: created with 2 free invokesn\
             When targeting existing/unknown aspects
                *Fail*: unknown or free enemy invoke
                *Tie*: free invoke on known, boost on unk.
                *Success*: free invoke on aspect
                *SwS*: 2 free invokes on aspect

### OUTCOMES/ACTIONS (cont.)

        **Attack**:
             to harm a target
                *Fail*:  you fail to connect
                *Tie*:  you get a boost
                *Success*:  deal a hit equal to shift(s)
                *SwS*:  may reduce 1 shift for a boostn\
        **Defend**:
             to oppose attack or stop foe
                *Fail*: foe succeeds or you take hit
                *Tie*: action’s tie results applies
                *Success*: enemy stopped/missed
                *SwS*: as Success with a boostn\
        **Overcome**:
             to clear obstacles or hindrances
                *Fail*: fail or success w/ major cost
                *Tie*: partial succ., at minor cost, or boost
                *Success*: you meet your goal
                *SwS*: as Success with a boost

### MAJOR/MINOR COSTS

        **Major**
             significantly worse or more complicated
             •  introduce new problem
             •  bring in new foes
             •  put PCs on a deadline
             •  mild/moderate consequence
             •  enemy gets situation aspect w/ free invoke
        **Minor**
             difficulty or complication, not hindrance
             •  a few points of stress
             •  a boost to the enemy
        **Recovery**
             •  stress clears at end of scene
             •  consequences vary:
                 roll to overcome using skill
                 –  Mild: +2(Fair)
                     •   clears in one full scene
                 –  Moderate: +4(Great)
                     •   clears in one full session
                 –  Severe: +6(Fantastic)
                     •   clears on major milestone

### ASPECTS

        Aspects are true. They can grant or withdraw
        permission for what can happen in the story.
        Invoke an aspect to get +2 on a roll, reroll,
        or increase foe’s difficulty by 2.
        Invoking costs a fate point or uses a free invoke.
        Compel an aspect to add complications to a
        character’s circumstances, Player receives fate point
        or spends fate point to deny circumstances.

### TYPES OF ASPECTS

        **Boost.** Temporary, sometimes unnamed aspect.
            Provides a free invoke. Vanishes once used.
            Can’t be compelled. Can’t be invoked with a fate point.
        **Character.** Aspect on a character sheet.
        **Situation.** Aspect of the scene.
            Lasts only long as the circumstances persist.
        **Organization, Scenario, Setting, Zone.**
            Situation aspects of a group, scene or storyline,
            campaign, or map area, respectively.',

### ADJECTIVE LADDER

        +8  Legendary
        +7  Epic
        +6  Fantastic
        +5  Superb
        +4  Great
        +3  Good
        +2  Fair
        +1  Average
        +0  Mediocre
        -1  Poor
        -2  Terrible
        -3  Catastrophic
        -4  Horrifying

### SETTING DIFFICULTY

        **Low** = below relevant PC skill
        **Medium** =  close to PC skill
        **High** = higher than PC skill
        **Not tough** = Mediocre (0) or don’t roll.
        +2 for tough, +2 for each extra factor against them.
        Consult aspects to adjust. Use adjective ladder as guide.

### TEAMWORK OPTIONS

        _Combine Skills._ Character with highest skill rolls. 
            PCs with same skill at Average (+1) or better use action to add +1.
            Max bonus is highest skill rating.
            Supporters face same costs & consequences as the PC who rolls.
        _On your turn._ Create an advantage & let allies
            use the free invokes on their turns.
        _Outside your turn._ Invoke an aspect to add a bonus to an ally’s roll.

### TURN ORDER

            At the start, everyone decides who goes first.
            After acting, player chooses who goes next.
            GM’s characters are in the turn order just like the PCs.
            Last player to go picks who starts next.

### EARN FATE POINTS WHEN YOU

          •  Accept a compel.
          •  Have your aspectsinvoked.
          •  Concede a conflict.',

### SPEND FATE POINTS TO

          •  Invoke an aspect.
          •  Power a stunt.
          •  Refuse a compel.
          •  Declare a story detail.
  
### CHALLENGES

        GM picks a number of skills representing the tasks needed to beat the challenge.
        Number of tasks roughly equals the number of players.
        Each player picks a task and rolls skill to overcome.
        GM considers mix of results to determine outcome.

### CONTESTS

        Take place over a series of exchanges.
        Each side takes an overcome action for their goals.
        Only one character from each side makes the roll.
        Each participant may try to Create an Advantage (CaA)
        in addition to rolling or combining skills.
        On failed CaA, forfeit roll or give over free invoke.
        At end of exchange, side with highest effort gains 1 victory
        Success with Style gains 2 victories.
        If harm is allowed, absorb shifts as stress.
        Tie results in unexpected twist - GM describes.
        First side to 3 victories (as GM determines) wins.

### CONFLICTS

        When violence/coercion is an option and each side could harm the other.
        Takes place over a series of exchanges. Each character acts in turn order (as On Your Turn).
        Defenders roll to oppose. Conflict ends when one side concedes or is taken out.
        Players who concede each take a fate point. GM also pays players hostile invoke fate points.



# DEVELOPER SETUP

https://www.mongodb.com/download-center/community?tck=docs_server

your settings.json file setup:
https://github.com/microsoft/vscode-python/issues/9346

Mongoengine info:
http://mongoengine.org/

Mongoengine Tutorial:
http://docs.mongoengine.org/tutorial.html

Mongoengine API Reference:
http://docs.mongoengine.org/apireference.html

Discord.py Docs:
https://discordpy.readthedocs.io/en/latest/index.html

Use “virtualenv”
“virtualenv” is a 3rd-party python package that effectively “clones” a python installation, thereby creating an isolated location to install packages. The evolution of “virtualenv” started before the existence of the User installation scheme. “virtualenv” provides a version of easy_install that is scoped to the cloned python install and is used in the normal way. “virtualenv” does offer various features that the User installation scheme alone does not provide, e.g. the ability to hide the main python site-packages.

Please refer to the virtualenv documentation for more details.
Setting up your virtual environment:
c:\>python -m venv c:\path\to\myenv
c:\path\to\myenv\scripts\acitvate

{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Dreamcraft Bot",
            "type": "python",
            "request": "launch",
            "pythonPath": "${config:python.pythonPath}",
            "program": "${workspaceFolder}/bot.py",
            "console": "externalTerminal"
        }
    ]
}

Making a test Discord bot:
https://realpython.com/how-to-make-a-discord-bot-python/
