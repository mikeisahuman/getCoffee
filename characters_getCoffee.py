############ getCoffee  -  text-based RPG in a coffee house ############
#
#.... Characters - player, patrons, workers. / Items - napkins ....#

import game_getCoffee
import math

VOID = game_getCoffee.Area("The Void", "You see nothing but blackness all around...", {}, (-2,-2))

# Some default values for various types of characters
PLAYER_DEF = {"STATS":(5, 2, 1), "POINTS":[25,1,0],
              "VERBS":("move","grab","trade","attack","quit"), "ASSOC":[], "ITEMS":[]}
PATRON_DEF = {"STATS":(2, 1, 0), "POINTS":[25,1,0],
              "VERBS":("move"), "ASSOC":[], "ITEMS":[], "PARS":(0, 1, 5)}



# We make a generic character class, from which the player and NPCs will be derived

class Character :
    def __init__(self, name = "No Name", stats = (0,0,0),
                 points = [0,0,0], verbs = (), assoc = [], items = [], init_area = VOID) :
        self._NAME = str(name)  #.every character begins with a name
        self._STATS = stats     #.will have (static) stats - base damage, defense, dodge
        self._MAX_STRESS = 10   #.maximum number of stress points
        self.points = points    #.will have (dynamic) points - hit points, stress level, and moneys
        self.VERBS = verbs      #.will have possible actions (e.g. "move", "say", "flee") - static
        self.assoc = assoc      #.may have associations (e.g. "in bike club", "in line") - dynamic
        self.items = items      #.may possess some items at a given moment - dynamic
        self.area = init_area   #.will have some current area / location - dynamic
        self.area.add_char(self._NAME)  #.add character to area's list upon creation / initialization
        pos = self.area.position()      #.set position to that of initial area
        self.x = pos[0]         #.current x coordinate on map (coordinates in addition to area names)
        self.y = pos[1]         #.current y coordinate
        #.function for applying a stress modification to accuracy (fighting only) - same for all characters
        mid_acc = 3/4       #.accuracy at half-stress (5 out of 10 normally)
        full_acc = 1/3      #.accuracy at full stress (max 10 default)
        p = math.log2( (mid_acc/full_acc) * ((1 - full_acc)/(1 - mid_acc)) ) #.power/rate of change
        a = ( full_acc / (1 - full_acc) ) * ( self._MAX_STRESS ** p )   #.'offset' of function
        self.accMod = lambda stress : a / ( ( stress ** p ) + a )       #.actual function (not to be changed)
        #.function for allowing a chance to deliver a critical hit (fighting only - increases with stress
        base_crit = 2/100   #.base critical hit chance (at zero stress)
        max_crit = 6/10     #.maximum critical hit chance (at max stress, default 10)
        p = 0.5             #.power of dependence (should be <=1)
        self.critMod = lambda stress : base_crit + (max_crit - base_crit) * ((stress/self._MAX_STRESS)**p)

    # basic accessors
    def get_name(self) :
        return self._NAME
    def get_stats(self) :
        return self._STATS
    def set_area(self, area) :
        self.area.rem_char(self.get_name()) #.remove the character from the area's list
        self.area = area                    #.set the character's area
        self.area.add_char(self.get_name()) #.add the character to the new area's list
        return
    def get_position(self) :
        return (self.x, self.y)
    def set_position(self, area) :
        pos = game_getCoffee.MY_MAP[area.name()][1]   #.grid position comes from the map
        self.x = pos[0]
        self.y = pos[1]
        return        
##    def set_position(self, pos) :
##        self.x = pos[0]
##        self.y = pos[1]
##        return

    # some things will cause an increase / decrease in stress
    def mod_stress(self, mod_num) :
        MAX_STRESS = self._MAX_STRESS
        st = self.points[1]
        st += mod_num
        st = round(st)
        if st < 0 :
            st = 0
        elif st > MAX_STRESS :
            st = MAX_STRESS
        self.points[1] = st
        return

    # take damage upon getting hit, and increase stress ['self' takes 'damage' from 'other']
    def take_damage(self, other, damage) :
        STS_FRAC = 1 / 2
        hp = self.points[0]
        self.points[0] = max(0, hp - damage)
        sts_mod = math.ceil( STS_FRAC * damage )
        self.mod_stress(sts_mod)
        other.mod_stress(-sts_mod)
        return

    # function for moving
    def move(self, direction) :
        pos = game_getCoffee.GRID_DIRECTION[direction]
        self.x += pos[0]
        self.y += pos[1]
        for area_name in game_getCoffee.MY_MAP :
            if game_getCoffee.MY_MAP[area_name][1] == self.get_position() :
                self.set_area(game_getCoffee.MY_MAP[area_name][0])
                break
        return


# The player class is very special - takes only a name, and has additional player-specific methods (e.g. grab)

class Player(Character) :
    def __init__(self, name) :
        #.add placeholder name for the player
        game_getCoffee.PLAYER = (str(name),)
        #.the Player is a Character, starting with some attributes, possible verbs, items...
        super().__init__(name, PLAYER_DEF["STATS"], PLAYER_DEF["POINTS"],
                           PLAYER_DEF["VERBS"], PLAYER_DEF["ASSOC"], PLAYER_DEF["ITEMS"])
##        print(self.items)

    def set_name(self, name) :
        self.area.rem_char(self.get_name()) #.remove old name from area's list
        self._NAME = str(name)              #.set to new name
        game_getCoffee.PLAYER = (self.get_name(),)   #.make sure the PLAYER tuple is updated
        self.area.add_char(self.get_name()) #.add new name to area's list
        return

    def grab(self, item) :
        self.area.rem_item(item.name())
        self.items.append(item)
        return

    def trade(self, other, myItem, npcItem) :
        if type(myItem) == int and type(npcItem) != int :
            # "buy"
            #.take item from npc
            self.items.append(npcItem)
            other.items.remove(npcItem)
            #.give money
            self.points[2] -= myItem
            other.points[2] += myItem
        elif type(npcItem) == int and type(myItem) != int :
            # "sell"
            #.give item to npc
            self.items.remove(myItem)
            other.items.append(myItem)
            #.take money
            self.points[2] += npcItem
            other.points[2] -= npcItem
        elif type(myItem) != int and type(npcItem) != int :
            # "trade"
            #.take item from npc
            self.items.append(npcItem)
            other.items.remove(npcItem)
            #.give item to npc
            self.items.remove(myItem)
            other.items.append(myItem)
        else :
            #.cannot trade money for money
            print(game_getCoffee.MESSAGES["FAIL"])
            return game_getCoffee.FAILURE
        return
    

# The NPCs, a.k.a. Patrons, will have their own generic behavior

class Patron(Character) :
    def __init__(self, name, area = VOID, greeting = "", repeat = "", items = PATRON_DEF["ITEMS"],
                 verbs = PATRON_DEF["VERBS"], assoc = PATRON_DEF["ASSOC"],
                 stats = PATRON_DEF["STATS"], points = PATRON_DEF["POINTS"],
                 trade_pars = PATRON_DEF["PARS"]) :
        #.add Patron to the list of NPCs
        game_getCoffee.MY_NPCS.update({ str(name) : self })
        #.the Patron is a Character as well
        super().__init__(name, stats, points, verbs, assoc, items, area)
        #.greeting, repeat message, and a counter to track number of times encountered
        self.GREETING = greeting
        self.R_GREETING = repeat
        self.ENCOUNTER = 0
        #.trade parameters decide the effects of stress on trade / item values
        amplitude = trade_pars[0]   #.overall maximum size of effect (between -1 and 1)
        scale = trade_pars[1]       #.x-scale factor to adjust impact of each stress point (at least 1)
        offset = trade_pars[2]      #."offset" number to decide critical [scaled] stress value (at least 1)
        if abs(amplitude) > 1 or scale < 1 or offset < 1 :
            print(game_getCoffee.MESSAGES["FAIL"], "\n\t-->  BAD character parameters for:", name)
        self.tradeMod = lambda stress : amplitude * (scale * stress) / ((scale * stress) + offset )

    def encounter(self) :                       #.increase encounter count
        self.ENCOUNTER += 1                 
        return

    def drop_items(self) :                      #.drop all items at the current area
        itms = self.items.copy()
        for itm in itms :
            self.area.add_item(itm.name())
            self.items.remove(itm)
        return
    def drop_money(self, other) :               #.give money to the one who killed
        moneys = self.points[2] 
        if moneys > 0 :
            other.points[2] += moneys
            self.points[2] = 0
            return moneys
        else :
            return 0

    def death(self) :                           #.move to VOID and delete upon death
        self.set_area(VOID)
        del self
        return

    def greeting(self) :                        #.print the appropriate greeting
        if self.ENCOUNTER == 0 :         #.check number of encounters with the patron
            s = self.GREETING
        else :
            s = self.R_GREETING
        #.print the greeting message
        print("< " + self.get_name() + " says: " + s + " >" + game_getCoffee.NEW_LINE)
        self.encounter()                 #.increase the encounter number
        return
    #.modify values of given NPC (self) items, separately from those of others (player)
    def self_value(self, item_value) :
        iv = item_value
        iv += iv * self.tradeMod(self.points[1])
        return round(iv)
    def other_value(self, item_value) :
        iv = item_value
        iv -= iv * self.tradeMod(self.points[1])
        return round(iv)


# Items should have their own class with: name, base value, base damage, "win" item (e.g. coffee)

class Item :
    def __init__(self, name, description = "an item", value = 0, damage = 0, win = False) :
        #.add Item to the list of items
        game_getCoffee.MY_ITEMS.update({ str(name) : self })
        #.initialize attributes
        self.NAME = str(name)
        self.DESC = str(description)
        self.VALUE = int(value)
        self.DAMAGE = int(damage)
        #.specify as "win" item if it's possession should end the game
        self.WIN = win

    def name(self) :
        return self.NAME
    def desc(self) :
        return self.DESC
    def value(self) :
        return self.VALUE
    def damage(self) :
        return self.DAMAGE
    def win(self) :
        return self.WIN
    
    #.allow for copying (make many objects with the same properties, optionally with a new name)
    def copy(self, new_name = None) :
        if new_name == None :
            nm = self.name()
        elif type(new_name) == str :
            nm = new_name
        else :
            print(game_getCoffee.MESSAGES["FAIL"])
            return game_getCoffee.FAILURE
        return Item( nm , self.desc(), self.value(), self.damage(), self.win())


