############ getCoffee  -  text-based RPG in a coffee house ############
#
#.... Game - essential workings of the game / Area - generic coffee shop areas ....#

import random as rn          #.package for generating random numbers (fighting/dodging)

# Global values #

#.success / failure for primary functions
SUCCESS = 0
FAILURE = 1
#.useful quick strings
DOT = "."
BLANK = " "
NEW_LINE = "\n"
END_LINE = DOT + NEW_LINE
CENTER_LEN = 100    #.number of characters used for 'centering'
STAR_TRIO = "*** "  #.trio of stars [asterisks] (with space)
STAR_LEN_1 = 12     #.number of repetitions of star trio (intro)
STAR_LEN_2 = 16     #.number of repetitions of star trio (congrats)
STAR_MID = len(STAR_TRIO) * (STAR_LEN_2 - 2)    #.number of central characters (for making a box)
STAR_LINE = BLANK + (STAR_TRIO * STAR_LEN_1).center(CENTER_LEN) + (NEW_LINE * 3)    #.a line of stars
STAR_EDGES = NEW_LINE + (STAR_TRIO + " ".center(STAR_MID) + STAR_TRIO).center(CENTER_LEN)
STAR_BOX_TOP = (STAR_TRIO * STAR_LEN_2).center(CENTER_LEN) + (STAR_EDGES * 2) + NEW_LINE
STAR_BOX_BOT = (STAR_EDGES * 2) + NEW_LINE + (STAR_TRIO * STAR_LEN_2).center(CENTER_LEN)
#.directions, and a dictionary for movement (north/east -> + , south/west -> - )
ALL_DIRECTIONS = ("North", "South", "East", "West")
GRID_DIRECTION = {"north":(0,1), "south":(0,-1), "east":(1,0), "west":(-1,0)}
#.all good verbs, and the ones actually used to trigger responses
VERB_DICT = {"move":["move", "go", "walk", "run", "shimmy", "travel"],
             "say":["say", "speak"], "grab":["grab", "take"],
             "trade":["trade", "buy", "sell", "barter", "shop"], #"steal",
             "attack":["attack", "fight", "hit", "slap", "punch", "pound", "cut", "beat", "stab", "slice"],
             "quit":["quit", "exit", "leave", "abort"]}
VERB_BANK = sum(list(VERB_DICT.values()), [])
MY_VERBS = ("move", "say", "grab", "trade", "attack", "quit")
TRADE_ESCAPES = ("stop", "nevermind", "none", "decline", "no", "nope", "end")
#.ask "what <thing>" to get information - need a list of possible <thing>s
WHAT_BANK = ("self", "me", "points", "moneys", "money", "status", "items", "area")#, "associations")
#.items are kept in a dictionary, labeled with the item names
MY_ITEMS = {}
#.areas and their coordinates will be organized in a dictionary (each entry added upon creation of area)
MY_MAP = {}
#.NPCs will need to be tracked (updated upon creation of each NPC)
MY_NPCS = {}
#.the player should be tracked as well
PLAYER = ()
#.system messages
MESSAGES = {"FAIL":"Something has gone horribly wrong...\n\n",
            "WELCOME":( (NEW_LINE * 13) + STAR_LINE
                        + "Welcome to the Coffee Shop Game!".center(CENTER_LEN) + (NEW_LINE * 3)
                        + STAR_LINE ),
            "INTRO":( "You are in desperate need of a coffee, but you are without any money."
                     + NEW_LINE + "You must interact with others to get your coffee" 
                     + " -- trade, fight, or con your way to success!" + (NEW_LINE * 2) ),
            "HELP":( "(If you get confused try typing 'what', "
                     + "followed by 'area' or the name of a character or item.)" + (NEW_LINE) ),
            "NAME":"What is your name?\t",
            "HELLO":"Hello ",
            "QUIT":( NEW_LINE + "Abandoning the quest for coffee..." + (NEW_LINE * 5) ),
            "WIN":( (NEW_LINE * 3) + STAR_BOX_TOP
                    + (STAR_TRIO
                       + "Congratulations, you have obtained your coffee!".center(STAR_MID)
                       + STAR_TRIO).center(CENTER_LEN)
                    + NEW_LINE
                    + (STAR_TRIO + "You may finally caffeinate in peace....".center(STAR_MID)
                       + STAR_TRIO).center(CENTER_LEN) 
                    + STAR_BOX_BOT
                    + (NEW_LINE * 5) ),
            "DEATH":(  NEW_LINE + STAR_BOX_TOP
                    + (STAR_TRIO
                       + "You perished in your quest for coffee...".center(STAR_MID)
                       + STAR_TRIO).center(CENTER_LEN)
                    + STAR_BOX_BOT + (NEW_LINE * 3) ).replace("*", "+"),
            "ENTER":"You are ",
            "RETURN":"You return to ",
            "OBTAIN":"You now have ",
            "ALLOW":"You may ",
            "REINPUT":"What was that?" + NEW_LINE}

# The main game needs its own class, with: gamestate, turnstate, input handling, begin(), etc.

class Game :
    def __init__(self) :
        self._PROMPT = " : >  "          #.prompt for player input
        self._INDENT = " : "            #.indent mark for player
        self._game_state = "NEW"         #.initial game state ("NEW","PLAYING","DEAD")
        self._turn_state = "PLAYER"      #.initial turn state ("PLAYER","SHOP","PATRON")
        self._reinputs = 0               #.reinput counter (print 'HELP' after so many)
        self._VALUE_SEP = " --> "        #.separator for indicating value (of items)

    # Map initialization function (add directions and check grid) #
    def map_init(self) :
        ok = True
        grid = [ m[1] for m in MY_MAP.values() ]
        areas = [ m[0] for m in MY_MAP.values() ]
        i = 0
        while i < len(grid) :
            xy = grid[i]
            a = areas[i]
            a.add_directions()
            if grid.count(xy) > 1 :
                ok = False
                print("<: Warning - grid overlap for : " + a.name() + " :>" + NEW_LINE)
            elif len(a.ACTIONS["move"]) == 0 and a.name() != "The Void" :
                ok = False
                print("<: Warning - isolated area : " + a.name() + " :>" + NEW_LINE)
            i += 1
        return ok

    #.function for interpreting input of two-word items
    def lst_doubles(self, lst) :
        return [ " ".join(lst[j:j+2]) for j in range(0,len(lst)-1) ]

    # return an Item object, given the name (whether proper or lowercase)
    def find_item(self, item_name) :
        name = item_name.lower()
        itm_names = list(MY_ITEMS.keys())
        itm_lower = list(map( str.lower, itm_names ))
        itm_match = itm_names[ itm_lower.index(name) ]
        return MY_ITEMS[itm_match]

    # return an NPC (Patron) object, given the name
    def find_npc(self, npc_name) :
        name = npc_name.lower()
        npc_names = list(MY_NPCS.keys())
        npc_lower = list(map( str.lower, npc_names ))
        npc_match = npc_names[ npc_lower.index(name) ]
        return MY_NPCS[npc_match]

    # function for carrying out responses to player input: verb (vb) on object (ob), possibly with item (it)
    def do_input(self, player, vb, ob, it) :
        if vb == "move" :
            player.move(ob)
            player.area.enter()
            return
        elif vb == "grab" :
            itm = self.find_item(ob)
            player.grab(itm)
            print(MESSAGES["OBTAIN"] + itm.name() + END_LINE)
            if it != None:
                itm2 = self.find_item(it)
                player.grab(itm2)
                print(MESSAGES["OBTAIN"] + itm2.name() + END_LINE)
            return
        elif vb == "trade" :
            if player.points[2] == 0 and len(player.items) == 0 :
                print("You have no items or money to offer..." + NEW_LINE)
                return
            npc = self.find_npc(ob)
            self.what_input(player, "items")
            self.what_input(player, "moneys")
            self.what_input(player, "items", ob)
            self.what_input(player, "moneys", ob)
            self.trade_query(player, npc, it)
            return
        elif vb == "attack" :
            myitms = [ itm.name().lower() for itm in player.items ]
            if it != None :
                if it not in myitms :
                    print("You do not have any", it, "with which to attack..." + NEW_LINE)
                    return
                else :
                    weapon = self.find_item(it)
            else :
                weapon = None
            npc = self.find_npc(ob)
            if not self.fight(player, npc, weapon) :    #.fight() returns True/False for alive/dead
                self._game_state = "DEAD"               #.change game state if player died during a fight
            return
        else :
            print(MESSAGES["FAIL"])
            return

    # function for trading, with one or more queries to decide what's being traded
    def trade_query(self, player, other, myOffer) :
        #.some useful strings
        TRADE_PROMPT = "    :trade>>  "
        TAB = "\t"
        smtab = BLANK * 4
        SEP = self._VALUE_SEP
        TRY_AGAIN = "You cannot do that. Try again" + END_LINE
        #.mimic of enumeration in C++
        ITEM, MONEY = 0, 1
        #.names of player's items
        myitem_names = [ i.name().lower() for i in player.items ]
        #.function for checking if the trade is cancelled
        def is_cancelled(s_in) :
            try:
                s = s_in.lower()
            except AttributeError:
                s = str(s_in).lower()
            if s in TRADE_ESCAPES :
                print("You decide not to do the trade..." + NEW_LINE)
                return True
            else :
                return False
        #.check for integer-type input
        def int_check(s_in) :
            try :
                s_in = int(s_in)
            except ValueError :
                s_in = str(s_in)
            return s_in
        #.function for printing real vs. perceived values for some item (assumes player's item by default)
        def value_info(item_obj, npc_item = False) :
            raw_val = item_obj.value()
            val = SEP + "valued @ " + str(raw_val)
            if npc_item :
                p_val = other.self_value(raw_val)
            else :
                p_val = other.other_value(raw_val)
            perc = " (to " + other.get_name() + ": " +  str(p_val) + ")"
            return (val + perc)
        #.!..while loop for getting a good offer
        npc_value = None
        while npc_value == None :
            #.ask for an offer if it hasn't already been given
            if myOffer == None :
                print(smtab
                      + "Do you want to offer an item (type its name), or money (type a number)?" + NEW_LINE)
                offer = input(TRADE_PROMPT).lower()
                offer = offer.split(" ")
                offer_doubles = self.lst_doubles(offer)
                for wd in offer + offer_doubles :
                    wd1 = wd.split(" ")[0]
                    if wd in TRADE_ESCAPES or wd in myitem_names :
                        offer = wd
                        break
                    elif type(int_check(wd1)) == int :
                        offer = wd1
                        break
                if type(offer) == list :
                    offer = offer[0]
            else :
                offer = myOffer
            if is_cancelled(offer) :        #.check if the player cancels the trade
                return
            offer = int_check(offer)        #.check if money (integer), return converted string if so
            #.handle offer of item or moneys
            if type(offer) == str :
                if offer.lower() in myitem_names :
                    found_item = self.find_item(offer)
                    value = found_item.value()              #.true value of item
                    npc_value = other.other_value(value)    #.value of item as seen by the npc
                    print( smtab + "You offer the " + found_item.name() + DOT
                           + value_info(found_item) + NEW_LINE)
                    offer_type = ITEM                       #.type of offer made by player
                else :
                    print(smtab + "You do not have a " + offer + " in your possession." + NEW_LINE)
                    myOffer = None
            elif type(offer) == int :
                if player.points[2] >= offer >= 0 :
                    value = offer                           #.value of money is direct
                    npc_value = value
                    print( smtab + "You offer", offer, "moneys" + END_LINE)
                    offer_type = MONEY
                else :
                    print(smtab + "You do not have", offer, "moneys." + NEW_LINE)
                    myOffer = None
            else :
                print(TRY_AGAIN)
                return
        #....(end of while loop [offer])
        #.valid options from the NPC
        otheritem_choices = [ i for i in other.items if other.self_value(i.value()) <= npc_value ]
        otheritem_names = [ i.name().lower() for i in otheritem_choices ]
        othermoney_max = min( other.points[2], npc_value )
        #.show any items available from the NPC, with their values
        if len(otheritem_choices) > 0 :
            print(TAB + other.get_name() + " has the following item(s) for that offer:" + NEW_LINE)
            for itm in otheritem_choices :
                print(TAB + BLANK + itm.name() + value_info(itm, True))
            print(BLANK)
        else :
            print(TAB + other.get_name() + " has no items for that offer." + NEW_LINE)
            if offer_type == MONEY :
                return
        #.display trade options
        if offer_type == ITEM :
            print(TAB + "Or, you could sell your " + offer + " for up to",
                  othermoney_max, "moneys." + NEW_LINE)
            s_money = "(or how much money) "
        elif offer_type == MONEY :
            s_money = ""
        else :
            print(MESSAGES["FAIL"])
            return FAILURE
        #.!..while loop for choosing item/money to receive
        choice_value = None
        while choice_value == None :
            #.get input for the desired item/money from the NPC
            print(TAB + "Which item " + s_money + "do you want?" + NEW_LINE)
            choice = input(TRADE_PROMPT)
            choice = choice.split(" ")
            choice_doubles = self.lst_doubles(choice)
            for wd in choice + choice_doubles :
                wd1 = wd.split(" ")[0]
                if wd in TRADE_ESCAPES or wd in otheritem_names :
                    choice = wd
                    break
                elif type(int_check(wd1)) == int :
                    choice = wd1
                    break
            if type(choice) == list :
                choice = choice[0]
            if is_cancelled(choice) :       #.check if the player cancels the trade
                return
            choice = int_check(choice)
            #.handle choice & offer cases
            if type(choice) == str and choice.lower() in otheritem_names :
                s_choice = other.get_name() + "'s " + self.find_item(choice).name() + END_LINE
                choice = self.find_item(choice)
                choice_value = choice.value()
                npc_choice_value = other.self_value(choice_value)
                if type(offer) == str :
                    print("You trade your " + found_item.name() + " for " + s_choice)
                    offer = self.find_item(offer)
                elif type(offer) == int :
                    print("You spend", offer, "moneys on " + s_choice)
                else :
                    print(MESSAGES["FAIL"])
                    return FAILURE
            elif type(choice) == int and 0 <= choice <= othermoney_max :
                s_choice = str(choice) + " moneys" + END_LINE
                choice_value = choice
                npc_choice_value = choice_value
                if type(offer) == str :
                    print("You sell your " + found_item.name() + " to "
                          + other.get_name() + " for " + s_choice)
                    offer = self.find_item(offer)
                else :
                    print(smtab + "You cannot trade money for money..." + NEW_LINE)
                    choice_value = None
            else :
                print(smtab + TRY_AGAIN)
                choice_value = None
        #....(end of while loop [choice])
        #.choice & offer must be valid at this point, so do the trade
        player.trade(other, offer, choice)
        #.modify stress if a bad deal is made
        NPC_half_diff = (npc_choice_value - value) // 2
        MY_half_diff = (choice_value - value) // 2
        if NPC_half_diff != 0 :
            other.mod_stress(NPC_half_diff)     #.inc/dec npc stress based on perceived values
        if MY_half_diff != 0 :
            player.mod_stress(-MY_half_diff)    #.inc/dec player stress based on real values
        #.items/money have been redistributed - update the current area (in case NPC goes broke)
        player.area.rem_char(other.get_name(), "trade")
        return

    # function for battling, with a loop to go until death (or upon fleeing)
    def fight(self, player, npc, myWeapon) :
        #.random attack verbs
        AT_verbs = ("swing", "lunge", "thrust", "slash")    #.attack verbs which need "at" following ("swing at..")
        NM_verbs = ("attack", "stab", "hit", "pound", "slice")  #.normal attack verbs, without an "at"
        E_verbs = ("slash",)                                #.verbs from above that need "e" to be 3rd person
        atkverbs = AT_verbs + NM_verbs                      #.all attack verbs together (E is alone)
        #.some useful strings
        npcName = npc.get_name()
        FIGHT_PROMPT = "    :fight>>  "
        TAB = "\t"
        smtab = BLANK * 4
        TRY_AGAIN = "Are you sure that's what you want to do?"
        SWING = "You %s " + npcName
        O_SWING = npcName + BLANK + "%s you"
        WPN_MSG = " with the %s"
        HIT = "You hit " + npcName + "%s for %i damage!"     #.need a tuple of: (wmsg, dmg)
        O_HIT = npcName + " hits you%s for %i damage!"
        DGE = "You dodge " + npcName + "'s attack!"
        O_DGE = npcName + " dodges your attack!"
        CRT = "You get a critical hit%s!"
        O_CRT = npcName + " gets a critical hit%s!"
        BL = "You block " + npcName + "'s attack!"
        O_BL = npcName + " blocks your attack!"
        IBL = "You prepare to block an attack..."
        O_IBL = npcName + " was waiting to block..."
        FL = "You flee the battle..."
        O_FL = npcName + " flees the battle..."
        MISS = "%s attack misses..."
        DEATH = "%s died..."
        ALIVE, O_ALIVE = True, True     #.indicate alive for player and npc
        FLEE = False                    #.indicate whether the player (or npc) is fleeing
        D_STS = 1       #.de-stress by this amount if the NPC is killed
        #.fractions for effective stat or other rewards / effects
        DMG_FRAC = 1
        DEF_FRAC = 2 / 3
        DGE_FRAC = 2 / 100  # 1 / 40
        BASE_HIT = 98 / 100
        CRIT_MULT = 3 / 2       #.multiplier for critical damage
        FLEE_FRAC = 1 / 100     #.flee fraction - stress increases chance for npc to flee
        BDMG_FRAC = 2 / 3       #.blocking reduces damage to this amount
        BLOCK_FRAC = 1 / 3      #.npc base chance to block (at defense = 0)
        BLOCK_DMAX = 10         #.effective max defense in npc block chance (block = 0 at DMAX)
        #.stats, items, and player's initial attack weapon
        [myDmg, myDef, myDge] = player.get_stats()
        [npcDmg, npcDef, npcDge] = npc.get_stats()
        myItems = player.items
        myItemNames = [ itm.name().lower() for itm in myItems ]
        npcItems = npc.items
        wpn = myWeapon
        #.function for giving True/False according to the given probability
        def roll(prob) :
            if prob > 1 or prob < 0 :
                print(" >> BAD PROBABILITY: ", prob)
                return True
            return rn.random() < prob
        #.# fight loop: get input, calculate hit and damage, make rolls, check for death #.#
        FIRST_PASS = True
        while ALIVE and O_ALIVE and not FLEE :
            #.reset variables
            BLOCK, O_BLOCK = False, False   #.indicate whether blocking (player, npc)
            #.player's base values
            dge = myDge * DGE_FRAC  #.true dodge chance
            dfn = myDef * DEF_FRAC  #.true defence (incoming damage reduction)
            dmg = myDmg * DMG_FRAC  #.true base damage
            #.npc base values
            odge = npcDge * DGE_FRAC
            odfn = npcDef * DEF_FRAC
            odmg = npcDmg * DMG_FRAC
            oblk = max(0, BLOCK_FRAC * (1 - npcDef/BLOCK_DMAX))
            #.print status of player and npc
            self.what_input(player, "status")
            self.what_input(player, "status", npcName.lower())
            #.check for first pass (initial attack)
            if not FIRST_PASS :
                #!# get player input: attack (with item), block, or flee #!#
                wpn = None      #.indicate weapon choice
                OK_in = False   #.initialization for acceptable input
                while not OK_in :
                    print(smtab + "Do you want to attack, block, or flee?" + NEW_LINE)
                    fight_in = input(FIGHT_PROMPT)
                    fight_in = fight_in.split(" ")
                    fight_in = [ w.lower() for w in fight_in ]
                    for wd in fight_in :
                        if wd == "attack" :
                            OK_in = True
                            aidx = fight_in.index("attack") + 1
                            doubles = self.lst_doubles(fight_in[aidx:])
                            for it in doubles + fight_in[aidx:] :
                                if it in myItemNames :
                                    wpn = self.find_item(it)
                                    break
                            if len(fight_in[aidx:]) > 0 and wpn == None :
                                OK_in = False
                            break
                        elif wd == "block" :
                            OK_in = True
                            BLOCK = True
                            break
                        elif wd == "flee" :
                            OK_in = True
                            FLEE = True
                            break
                    print(BLANK)
                    if not OK_in :
                        print(smtab + TRY_AGAIN + NEW_LINE)
                #!#   end input loop   #!#
            else :      #.change the setting on the first pass (allow for new input on further passes)
                FIRST_PASS = False
                    
            #.player details
            sts = player.points[1]  #.current stress level
            hit = BASE_HIT               #.base hit chance
            hit *= player.accMod(sts)    #.modify hit chance according to stress function
            crt = player.critMod(sts)    #.give crit chance from stress
            wmsg = ""
            if wpn != None :        #.modify damage (and attack message) if using a weapon
                dmg += wpn.damage()
                wmsg = WPN_MSG % wpn.name()
            #.npc details (similar to above)
            osts = npc.points[1]
            ohit = BASE_HIT
            ohit *= npc.accMod(osts)
            ocrt = npc.critMod(sts)
            owmsg = ""
            if len(npcItems) > 0 :
                rand_index = rn.randint(-1, len(npcItems) - 1)  #.randomly select weapon for the npc (or None)
                if rand_index < 0 :
                    owpn = None
                else :
                    owpn = npcItems[rand_index] 
                    odmg += owpn.damage()
                    owmsg = WPN_MSG % owpn.name()
            else :
                owpn = None
            #.player actions - block, flee, or roll to hit, and print appropriate response
            O_BLOCK = roll(oblk)    #.roll for npc blocking before doing anything
            if FLEE :       #.flee action
                print(FL + NEW_LINE)
                return ALIVE
            elif BLOCK :    #.block action
                print(smtab + IBL + NEW_LINE)
            else :          #.attempt to attack
                verb = atkverbs[ rn.randint(0, len(atkverbs)-1) ]   #.verb for attack messages
                if verb in AT_verbs :
                    verb += " at"
                print(smtab + (SWING % verb) + wmsg + "..." + NEW_LINE)  #.swing
                if roll(hit) :  #.accuracy roll (from stress) to hit
                    if roll(odge) : #.luck roll for dodge
                        print(TAB + O_DGE + NEW_LINE)
                    else :
                        if roll(crt) :  #.crit roll - multiply damage
                            dmg *= CRIT_MULT    #.crit damage multiplication
                            print(TAB + (CRT % wmsg) + NEW_LINE)
                        if O_BLOCK :    #.check for npc block action
                            dmg *= BDMG_FRAC    #.block damage reduction
                            print(TAB + O_BL + NEW_LINE)
                        dmg = max(0, round(dmg - odfn))    #.final damage, after defense reduction
                        npc.take_damage(player, dmg)    #.damage is dealt to the npc by the player
                        print(TAB + ( HIT % (wmsg, dmg) ) + NEW_LINE)
                else :          #.missed attack
                    print(TAB + ( MISS % "Your" ) + NEW_LINE)
                if npc.points[0] == 0 :     #.check for npc death
                    O_ALIVE = False     #.tag changed to stop loop
                    print(smtab + (DEATH % (npcName + " has")) + NEW_LINE)
                    player.mod_stress(-D_STS)   #.de-stress after killing (could add stress instead..)
                    npc.drop_items()            #.drop items into the area upon death
                    moneys = npc.drop_money(player)      #.drop (give) money to the killer (player)
                    print("You receive", moneys, "moneys" + END_LINE)
                    npc.death()         #.make the npc 'die' -- i.e. remove from game
                    return ALIVE    #.return the value of the player's status ('True' when alive)
            #.npc actions
            FLEE = roll( npc.points[1] * FLEE_FRAC )    #.give a chance for the npc to flee
            if FLEE :
                print(O_FL + NEW_LINE)
                return ALIVE
            elif O_BLOCK :
                print(smtab + O_IBL + NEW_LINE)
            else :
                verb = atkverbs[ rn.randint(0, len(atkverbs)-1) ]
                if verb in E_verbs :
                    e = "e"
                else :
                    e = ""
                if verb in AT_verbs :
                    verb += (e + "s") + " at"
                else :
                    verb += e + "s"
                print(smtab + (O_SWING % verb) + owmsg + "..." + NEW_LINE)
                if roll(ohit) :
                    if roll(dge) :
                        print(TAB + DGE + NEW_LINE)
                    else :
                        if roll(ocrt) :
                            odmg *= CRIT_MULT
                            print(TAB + (O_CRT % owmsg) + NEW_LINE)
                        if BLOCK :
                            odmg *= BDMG_FRAC
                            print(TAB + BL + NEW_LINE)
                        odmg = max(0, round(odmg - dfn))
                        player.take_damage(npc, odmg)
                        print(TAB + ( O_HIT % (owmsg, odmg) ) + NEW_LINE)
                else :
                    print(TAB + ( MISS % (npcName + "'s") ) + NEW_LINE)
                if player.points[0] == 0 :  #.check for player death
                    ALIVE = False
                    print( (DEATH % ("You have")) + NEW_LINE)
                    return ALIVE    #.return 'False' upon death
        #.#  end fight loop   #.#

    # function for handling "what" inputs
    def what_input(self, player, ob, it = None) :
##        npcs = list(map( str.lower, player.area.npcs() ))    #.list of npcs in area
        list_lower = lambda l : tuple(map( str.lower, l ))      #.inline function to lower() a list of strings
        npcs = list_lower( list(MY_NPCS.keys()) )    #.list of all npcs
        itms = list_lower( list(MY_ITEMS.keys()) )    #.list of all items
        if it == None :
            thing = player
        elif it in npcs :
            thing = self.find_npc(it)
        else :
            print(MESSAGES["FAIL"])
            return
        ps = []                                         #.list of labels (updated below)
        #.generic description function
        def describe(lst, labels, head = True) :            
            if head :
                print(thing.get_name() + "'s " + ob + ":")
            for s in labels :
                si = labels.index(s)
                if (type(lst[si]) == str or type(lst[si]) == int or type(lst[si]) == float) :
                    print(s + str(lst[si]))
                else :
                    print(s + lst[si].name() + self._VALUE_SEP + "valued @ " + str(lst[si].value()) )
            print(BLANK)
            return
        #.check if something exists (e.g. has items), describe() if so
        def check_empty(lst, obj = ob, head = True, name = thing.get_name()) :
            li = len(lst)
            if li > 0 :
                ps = [("  " + str(x) + ":\t") for x in range(1, 1 + li)]
                describe(lst, ps, head)
            else :
                print(name + " has no " + obj + END_LINE)
        #.modified "WHAT_BANK" for looping over essential attributes
        MOD_BANK = ( x for x in WHAT_BANK if (x not in ("self", "me", "moneys", "money", "status")) )
        #.case-handling for each request
        if ob == "self" or ob == "me" :
            for label in MOD_BANK :
                self.what_input(player, label)
        elif ob == player.get_name().lower() :
            self.what_input(player, "self")
        elif ob in npcs :
            for label in MOD_BANK :
                self.what_input(player, label, ob)
        elif ob in itms :
            i = itms.index(ob)
            itm = list(MY_ITEMS.values())[i]
            print("The " + itm.name() + " has" + ":")
            describe( [itm.value(), itm.damage(), itm.desc()], ["  value:  ", "  damage: ", " "], False)
        elif ob == "points" :
            ps = ["  hp:     ", "  stress: ", "  money:  "]
            describe(thing.points, ps)
        elif ob == "moneys" or ob == "money" :
            describe(thing.points[2:], [thing.get_name() + "'s " + " money:  "], False)
        elif ob == "status" :
            describe(thing.points[0:2], ["  hp:     ", "  stress: "])
        elif ob == "items" :
            check_empty(thing.items)
        #.disabled until associations are meaningful
        #elif ob == "associations" :            
            #check_empty(thing.assoc)
        elif ob == "area" :
            print(thing.get_name() + "'s " + ob + " (" + thing.area.name() + "):")
            print((BLANK * 2) + "items:")
            if "grab" in thing.area.ACTIONS :
                aitems = thing.area.ACTIONS["grab"]
            else :
                aitems = []
            check_empty(aitems, "items", False, "The " + thing.area.name())
            print((BLANK * 2) + "characters:")
            check_empty(thing.area.CHARS, "characters", False, thing.area.name())
            if thing.get_name() == PLAYER[0] :
                print(thing.area.DESC)
                for key in thing.area.ACTIONS :
                    print(thing.area.allow_message(key))
            print(BLANK)
        return

    # function for handling player input (possible verbs & resultant actions)
    def handle_input(self, player) :
        #.set up variables to indicate a good verb / object / item
        found_vb = False
        found_ob = False
        found_it = False
        #.max number of reinput attempts (display 'HELP' message after so many)
        MAXINPUTS = 4
        #.function for incrementing and displaying appropriate messages
        def reinput() :
            self._reinputs += 1
            print(MESSAGES["REINPUT"])
            if self._reinputs >= MAXINPUTS :
                print(MESSAGES["HELP"])
                self._reinputs = 0
            return
        #.input string from the player
        p_input = input(self._INDENT + player.get_name() + self._PROMPT)
        p_raw_list = p_input.split(" ")
        p_list = (p_input.lower()).split(" ")   #.split into a list of words
        #!#.words in p_list should be translated at this point (alternate verb names)
        for vb in p_list :                      #.scan the list for any good verbs
            for k in VERB_DICT:
                if vb in VERB_DICT[k]:
                    orig_vb = vb
                    vb = k
                    break
            if ( (vb in player.VERBS) and (vb in player.area.ACTIONS) ) :
                found_vb = True
                if len(p_list) == 1 :
                    if vb == "quit" :
                        print(MESSAGES["QUIT"])
                        return SUCCESS
                    else :
                        reinput()
                        return
                else :
                    sindex = 1 + p_list.index(orig_vb)
                    p_list_s = p_list[sindex:]
                    p_doubles_s = self.lst_doubles(p_list_s)
                    for ob in p_doubles_s + p_list_s :     #.look for matching objects (allow two-word names)
                        if ob in p_list_s :
                            obindex = p_list.index(ob)
                        else :
                            obindex = p_list.index(ob.split(" ")[0])
                        vbindex = p_list.index(orig_vb)
                        if ob in tuple(map(str.lower, player.area.ACTIONS[vb])) :
                            found_ob = True
                            #.check for any item (as in "hit bob with fist"), handle "for" case
                            if (len(p_list) > 3) :
                                p_list_o = p_list[obindex:]
                                if (p_list_o.count("with") > 0) :
                                    withindex = p_list_o.index("with")
                                    p_list_w = p_list_o[withindex + 1 :]
                                    p_doubles_w = self.lst_doubles(p_list_w)
                                    itms = tuple(map(str.lower, MY_ITEMS.keys() ))
                                    for it in p_doubles_w + p_list_w :
                                        if it in itms :
                                            found_it = True
                                            break
                                        else:
                                            try:
                                                it = int(it)
                                            except ValueError:
                                                it = it
                                            if type(it) == int:
                                                it = str(it)
                                                found_it = True
                                                break
                                                
                                    if not found_it :
                                        if (len(p_list_w) == 1) :
                                            it = p_list_w[0]
                                        else :
                                            it = p_doubles_w[0]
                                        print("There is no item:   '%s'" % it)
                                        return
                                        
                                elif (p_list_o.count("for") > 0) and vb == "trade" :
                                    print("You cannot request something"
                                          + " at the start of a trade"
                                          + " -- try making an offer first" + END_LINE)
                                    return

                                elif (p_list_o.count("and") > 0) and vb == "grab" :
                                    andindex = p_list_o.index("and")
                                    p_list_and = p_list_o[andindex + 1 :]
                                    p_doubles_and = self.lst_doubles(p_list_and)
                                    area_itms = tuple(map(str.lower, player.area.ACTIONS[vb]))
                                    for it in p_doubles_and + p_list_and :
                                        if (it in area_itms) and (it != ob) :
                                            found_it = True
                                            break
                            else :
                                it = None
                            #.do the corresponding action (vb) on the object (ob), with item (it)
                            print("You " + p_input + END_LINE)
                            #print("You " + p_raw_list[vbindex] + BLANK
                            #      + p_raw_list[obindex] + END_LINE)
                            
                            self.do_input(player, vb, ob, it)
                            self._reinputs = 0                #.restart the reinput counter
                            self._turn_state == "SHOP"  #.set to shop's turn after player action
                            return
                    if found_vb and not found_ob :
                        print("You cannot " + p_input + " here: " + player.area.name() + END_LINE)
                        #print("You cannot " + p_raw_list[vbindex] + BLANK + p_raw_list[obindex]
                        #      + " here: " + player.area.NAME + END_LINE)
                        return
            elif vb == "what" :
                found_vb = True
                print(BLANK)
                if len(p_list) == 1 :
                    # "what" same as "what self"
                    self.what_input(player, "self")
                    return
                else:
                    sindex = 1 + p_list.index(vb)
##                    npcs = list(map( str.lower, player.area.npcs() ))    #.list of npcs in area
                    npcs = list(map( str.lower, list(MY_NPCS.keys()) ))    #.list of all npcs
                    itms = list(map( str.lower, list(MY_ITEMS.keys()) ))    #.list of all items
                    found_ob = False
                    p_doubles_s = self.lst_doubles(p_list[sindex:])
                    for ob in p_doubles_s + p_list[sindex:] :     #.look for matching objects
                        ob_main = (ob in WHAT_BANK) or (ob == player.get_name().lower())
                        ob_lists = (ob in npcs) or (ob in itms)
                        if ob_main or ob_lists :
                            found_ob = True
                            oindex = 1 + p_list.index(ob.split(" ")[0])
                            if len(p_list) > 2 :
                                found_it = False
                                for it in p_list[oindex:] :
                                    if (it in WHAT_BANK) and (ob in npcs) :
                                        found_it = True
                                        self.what_input(player, it, ob)
                                        return
                                    elif (it in npcs) and (ob in WHAT_BANK) :
                                        found_it = True
                                        self.what_input(player, ob, it)
                                        return
                                if not found_it :
                                    self.what_input(player, ob)
                                    return
                                else :
                                    print(MESSAGES["FAIL"])
                                    return FAILURE
                            else :
                                self.what_input(player, ob)
                                return
                    if not found_ob :
                        print(MESSAGES["REINPUT"])
                break
            elif vb == "help" :
                found_vb = True
                print(NEW_LINE + MESSAGES["HELP"])
                return
##            else :
##                break
        if not found_vb :
            if p_raw_list[0] in VERB_BANK :
                print("There is no way to " + p_raw_list[0] + " here: "
                      + player.area.NAME + END_LINE)
            else :
                reinput()
        return

    # begin() function - used to access & begin the game
    def begin(self, player, init_area) :
        # the game begins
        if self._game_state != "NEW" :
            print(MESSAGES["FAIL"])
            return FAILURE
        else :
            # initialize the map ("move" directions, grid check)
            if not self.map_init() :
                return FAILURE
            # welcome/intro messages and initial setup
            print(MESSAGES["WELCOME"])
            p_name = input(MESSAGES["NAME"])    #.ask for a name
            player.set_name(p_name)
            print(NEW_LINE + MESSAGES["HELLO"] + player.get_name() + DOT + NEW_LINE * 2)
            print(MESSAGES["INTRO"])
            print(MESSAGES["HELP"] + NEW_LINE)
            
            self._game_state = "PLAYING"
            player.set_area(init_area)
            player.set_position(init_area)
            if player.area.enter() == FAILURE :
                return FAILURE
            ### GAME LOOP ###
            while 1 :
                if self._game_state == "PLAYING" :
                    # handle normal (inert) case - movement, inspection, etc.
                    if self._turn_state == "PLAYER" :
                        result = self.handle_input(player)
                        if result == SUCCESS :  #.return upon quitting
                            return SUCCESS
                        for item in player.items :
                            if item.win() :
                                print(MESSAGES["WIN"])
                                return SUCCESS
                    elif self._turn_state == "SHOP" :
                        self._turn_state = "PATRON"
                    elif self._turn_state == "PATRON" :
                        self._turn_state = "PLAYER"
                    else :
                        print(MESSAGES["FAIL"])
                        return FAILURE
                elif self._game_state == "DEAD" :
                    print(MESSAGES["DEATH"])
                    return SUCCESS
                else :
                    print(MESSAGES["FAIL"])
                    return FAILURE
                

# Locations (areas) need a class to store: name, description, possible actions, position, characters

class Area :
    def __init__(self, name, desc, items, position) :
        MY_MAP.update({ name : (self, position)})   #.add the area to the map upon creation
        self.NAME = name            #.name of area (e.g. "coffee bar")
        self.DESC = desc + NEW_LINE #.description of area
                                    # (e.g. "There are some stools at a high countertop.")
        self.X = position[0]        #.x coordinate : placement of area onto a grid (given a tuple 'position')
        self.Y = position[1]        #.y coordinate
        self.ACTIONS = {}           #.dictionary of actions on the area (only "grab" should be explicit)
                                    # (e.g. {"move":ALL_DIRECTIONS, "grab":("mug","fork"),...})
        if len(items) > 0 :         #.add "grab" if there are items
            self.ACTIONS.update({"grab":[ it.name() for it in items ]})
        self.ACTIONS.update({"move":()})    #.add the option to "move" (directions are added separately)
        self.ACTIONS.update({"quit":""})    #.make sure to always have "quit"
        self.ENTERED = 0            #.number of times the area has been entered
        self.CHARS = []             #.characters (player or patrons) currently in the area (initially empty)

    def name(self) :                #.name accessor
        return self.NAME
    def position(self) :            #.position accessor
        return (self.X, self.Y)
    def neighbor(self, direction) : #.return the neighboring area lying in the given direction (e.g. North)
        dr = direction.lower()
        xother = self.X + GRID_DIRECTION[dr][0]
        yother = self.Y + GRID_DIRECTION[dr][1]
        for area_name in MY_MAP :
            if MY_MAP[area_name][1] == (xother, yother) :
                return MY_MAP[area_name][0]
##        print("<: Warning - no neighbor found in the direction: " + direction + " :>" + NEW_LINE)
        return None
    def add_directions(self) :      #.add possible "move" directions to the dictionary
        dirs = []
        for d in ALL_DIRECTIONS :
            if self.neighbor(d) != None :
                dirs.append(d)
        self.ACTIONS["move"] = tuple(dirs)
        return

    def npcs(self) :                #.internal function for getting NPCs in the area
        c = self.CHARS[:]           #.must use list slicing to preserve the original (CHARS)
##        print("temp chars and the player: " + str(c) + ", " + PLAYER[0])
        if PLAYER[0] in c :
            c.remove(PLAYER[0])
##            print("After removing the player: " + str(c))
        return c

    def add_char(self, char_name) : #.add and remove characters
        if char_name not in self.CHARS :
            self.CHARS.append(char_name)
            c = self.npcs()
            l = len(c)
            if l > 0 and char_name in c :
                #.check for items (or money) for trading
                if len(MY_NPCS[char_name].items) > 0 or MY_NPCS[char_name].points[2] > 0 :
                    if "trade" not in self.ACTIONS :
                        q = self.ACTIONS.popitem()
                        self.ACTIONS.update({"trade":c, q[0]:q[1]})
                    elif char_name not in self.ACTIONS["trade"] :
                        self.ACTIONS["trade"].append(char_name)
                if "attack" not in self.ACTIONS :
                    q = self.ACTIONS.popitem()
                    self.ACTIONS.update({"attack":c, q[0]:q[1]})
                elif char_name not in self.ACTIONS["attack"] :
                    self.ACTIONS["attack"].append(char_name)
        return
    def rem_char(self, char_name, action = 1) :
        aList = ["trade", "attack"]
        if action == 1 :        #.if removing the character entirely
            self.CHARS.remove(char_name)
            aDict = {"trade" : True, "attack" : True}
        elif action in aList :  #.if removing the character only from a given list
            aList = [action]
            char = MY_NPCS[char_name]
            char_hp = char.points[0]
            char_money = char.points[2]
            char_item = char.items
            char_dead = char_hp == 0
            char_broke = (char_money == 0 and len(char_item) == 0 )
            aDict = {"trade" : char_broke, "attack" : char_dead}
            if char_dead and action == "attack" :
                self.CHARS.remove(char_name)
        else :
            print(MESSAGES["FAIL"])
            return
        c = self.npcs()
        l = len(c)
        if l == 0 :
            for a in aList :
                if a in self.ACTIONS and aDict[a] :
                    del self.ACTIONS[a]
        elif l > 0 and char_name not in PLAYER :
            if ("trade" in aList) and ("trade" in self.ACTIONS) and aDict["trade"] :
                if char_name in self.ACTIONS["trade"] :
                    if len(self.ACTIONS["trade"]) > 1 and (char_name in self.ACTIONS["trade"]) :
                        self.ACTIONS["trade"].remove(char_name)
                    else :
                        del self.ACTIONS["trade"]
            if ("attack" in aList) and aDict["attack"] and (char_name in self.ACTIONS["attack"]) :
                self.ACTIONS["attack"].remove(char_name)
        return

    def add_item(self, item_name) :      #.add and remove items
        if "grab" in self.ACTIONS :         #.if "grab" is there, then just add to the list of items
            self.ACTIONS["grab"].append(item_name)
            return
        else :                              #.if no items, take out "quit", add "grab", and put back "quit"
            q = self.ACTIONS.popitem()
            self.ACTIONS.update({"grab":[item_name], q[0]:q[1]})
            return
    def rem_item(self, item_name) :
        if "grab" in self.ACTIONS :             #.check for a "grab"
            if item_name in self.ACTIONS["grab"] :   #.check for the item
                if len(self.ACTIONS["grab"]) == 1 :
                    del self.ACTIONS["grab"]    #.delete "grab" action if there was only one item
                    return
                else :
                    self.ACTIONS["grab"].remove(item_name)   #.remove the item from the "grab" list
                    return
            else :
                print(MESSAGES["FAIL"])
                return
        else :
            print(MESSAGES["FAIL"])
            return
        
    def npc_greeting(self) :        #.function for printing the appropriate greetings of any NPCs in the area
        c = self.npcs()
        for npc_name in c :
            npc = MY_NPCS[npc_name]
            npc.greeting()
        return

    def enter_message(self, mkey) :  #.message printed upon entry (or re-entry)
        name = self.name()
        if name != "outside" :
            if mkey == "ENTER" :
                name = "at the " + name
            elif mkey == "RETURN" :
                name = "the " + name
        return (MESSAGES[mkey] + name + END_LINE)

    def allow_message(self, akey) : #.message printed upon first entry - allowed actions in area
        act = self.ACTIONS[akey]
        l = len(act)
        if akey == "move" :         #.special case for moving (add neighbors)
            def _add_neighbor(st) : #.add the neighbor to the string - e.g. "north to the entrance"
                try :
                    if self.neighbor(st).name() != "outside" :
                        the = "the "
                    else :
                        the = ""
                    return (st + " to " + the + self.neighbor(st).name())
                except AttributeError :
                    print(MESSAGES["FAIL"])
                    return FAILURE
            act = tuple(map(_add_neighbor, act))
        elif akey == "trade" :      #.special case for trading (add "with")
            akey = akey + " with"   #.e.g. "trade with bob"
        try :
            if l == 1 :                 #.we should print objects of action with one of "or", ","
                s = BLANK + act[0]
            elif l == 2 :
                s = BLANK + " or ".join(act)
            elif l >= 3 :
                s = BLANK + ", ".join(act[0:(l-1)]) + ", or " + act[-1]
            elif l == 0 :
                s = ""
            else :
                print(MESSAGES["FAIL"])
                return FAILURE
        except TypeError :
            print(MESSAGES["FAIL"])
            return FAILURE
        return (MESSAGES["ALLOW"] + akey + s + DOT)

    def enter(self) :             #.handle entry (and re-entry)
        if self.ENTERED == 0 :
            print(self.enter_message("ENTER"))
            print(self.DESC)
            self.npc_greeting()
            for key in self.ACTIONS :
                msg = self.allow_message(key)
                if type(msg) == str :
                    print(msg)
                else :
                    return FAILURE
            print(BLANK)
        elif self.ENTERED > 0 :
            print(self.enter_message("RETURN"))
            self.npc_greeting()
        self.ENTERED += 1
        return


            
