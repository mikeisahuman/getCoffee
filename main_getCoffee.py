############ getCoffee  -  text-based RPG in a coffee house ############
#
#.... Entry Point / Main File - create essential objects, then begin() the game! ....#

import game_getCoffee as game
import characters_getCoffee as char

#.main game object
theGame = game.Game()

#.main player object
thePlayer = char.Player(name="player")                                       #.placeholder name

#!!#  use value of coffee drinks as difficulty?? (input w/ name)

# items : each item has value and damage; at least one should "win" (can copy an item using <Item>.copy())
coffee = char.Item(name="coffee",                                           #.item name
                   description="The deep black charmer.",                   #.item description
                   value=100,                                               #.base value
                   damage=5,                                                #.base damage
                   win="win")                                               #.win (default = False)
coffee2 = coffee.copy()
coffee3 = coffee.copy()
latte = char.Item(name="latte", description="Milky and strong.", value=150, damage=6, win="win")
espresso = char.Item(name="espresso", description="Black Gold.", value=120, damage=4, win="win")
espresso2 = espresso.copy()
espresso3 = espresso.copy()

sugars = char.Item(name="sugar packs", description="A handful of paper packages of that good sugar",
                   value=5, damage=1)
napkin = char.Item(name="napkin", description="A normal little napkin.", value=1, damage=0)
napkin2 = napkin.copy()
fork  = char.Item(name="fork", description="A three-pronged fork.", value=6, damage=3)
fork2 = fork.copy()
bknife = char.Item(name="butter knife", description="A knife for butchering scones.", value=6, damage=2)
bknife2 = bknife.copy()
key_chain = char.Item(name="key chain", description="Maybe this belongs in the lost-and-found box?",
                      value=8, damage=1)
key_chain2 = key_chain.copy()
sblade = char.Item(name="switchblade", description="An illegal fighting knife.", value=85, damage=10)

novel = char.Item(name="novel", description="A fictional book from a nameless author.", value=20, damage=4)
phone_charger = char.Item(name="phone charger", description="Doesn't someone need this?", value=21, damage=6)
textbook = char.Item(name="textbook", description="Looks pretty mathy...", value=120, damage=10)
pen = char.Item(name="pen", description="A simple pen from a common brand.", value=12, damage=4)
pen2 = pen.copy()
pen3 = pen.copy()
workbelt = char.Item(name="workbelt", description="Has everything you need to get the job done.",
                      value=45, damage=4)
odd_spoon = char.Item(name="odd spoon", description="How exactly do you use this?", value=17, damage=5)
odd_spoon2 = odd_spoon.copy()
magic_fork = char.Item(name="magic fork", description="Where did this come from?", value=100, damage=9)
silly_hat = char.Item(name="silly hat", description="Too silly to be worn.", value=25, damage=1)
hippie_headband = char.Item(name="hippie headband", description="You probably shouldn't touch this...",
                            value=35, damage=3)
hipster_hat = char.Item(name="hipster hat", description="It costs way more than it looks.",
                            value=55, damage=8)
scarf = char.Item(name="nice scarf", description="A high-quality warm scarf, made of gortex!",
                            value=40, damage=-1)
scarf2 = scarf.copy()
sunglasses = char.Item(name="sunglasses", description="Some pretty nice, dark-tinted sunglasses.",
                            value=30, damage=3)
mug = char.Item(name="mug", description="A mug with a single drop of coffee remaining.", value=6, damage=2)
mug2 = mug.copy()
mug3 = mug.copy()
dmug = char.Item(name="dirty mug", description="This mug has survived a cruel adventure...",
                 value=1, damage=4)
dmug2 = dmug.copy()
watch = char.Item(name="watch", description="This watch is pretty nice.", value=50, damage=2)
fancy_pen = char.Item(name="fancy pen", description="They don't make 'em like this anymore!",
                      value=80, damage=7)
bracelet = char.Item(name="bracelet", description="A rough, hand-made bracelet", value=10, damage=1)
bracelet2 = bracelet.copy()
bracelet3 = bracelet.copy()

# areas : begin with the outside
outside = game.Area(name="outside",                                                 #.area name
                    desc=("The door into the coffee shop is within reach.\n" +      #.description
                          "The smell is alluring..."),                              #.
                    items=[ ],                                                      #.list of items
                    position=(0,-1))                                                #.location on map grid

# other areas : make sure to build a consistent map grid
entrance = game.Area(name="entrance",
                    desc="The inside has coffee-based modern art pieces scattered throughout.",
                    items=[key_chain],
                    position=(0, 0))
merch = game.Area(name="merch zone",
                     desc="A few shelves are stocked with merchandise suitable for coffee addicts.",
                     items=[mug, odd_spoon],
                     position=(2, 0))
sm_table = game.Area(name="small table",
                     desc="There is an unbelievably small table outfitted with two chairs.",
                     items=[fork, napkin],
                     position=(1, 0))
wait_bench = game.Area(name="waiting bench",
                       desc="A bench is conveniently placed for to-go orders and tired stalkers.",
                       items=[silly_hat],
                       position=(-1, 0))
sm_bar = game.Area(name="small bar",
                     desc="Bar-like area with a couple of seats.",
                     items=[dmug],
                     position=(-2, 0))
throughway = game.Area(name="throughway",
                    desc="An area designed to help smooth the flow of foot traffic.",
                    items=[ ],
                    position=(0, 1))
fixins = game.Area(name="fixin' zone",
                    desc="The place for coffee fixings: cream, sugar, napkins, ...",
                    items=[bknife2, sugars],
                     position=(2, 1))
line = game.Area(name="line",
                    desc="A gathering area, where people form (something like) a line to get their coffee.",
                    items=[ ],
                     position=(1, 1))
big_table_R = game.Area(name="big table (right side)",
                        desc="The large table is meant to be shared by many.",
                        items=[mug2, napkin2],
                        position=(-1, 1))
big_table_L = game.Area(name="big table (left side)",
                        desc="The large table is meant to be shared by many.",
                        items=[key_chain2, bknife],
                        position=(-2, 1))
counter_edge = game.Area(name="edge of the counter",
                         desc=("The service counter comes to a corner, " +
                               "outfitted with a permanently-vacant high stool."),
                         items=[fork2],   #, magic_fork],
                         position=(0, 2))
counter_pickup = game.Area(name="pickup counter",
                         desc="There's an area to pick up finished beverages.",
                         items=[dmug2, sblade],   #, magic_fork],
                         position=(2, 2))
cash_register = game.Area(name="cash register",
                          desc="People with money can order coffee here.",
                          items=[],
                          position=(1, 2))
old_map = game.Area(name="large old map",
                        desc="A large map hangs on the wall here, obviously quite old.",
                        items=[scarf],
                        position=(-1, 2))
secret_table = game.Area(name="secret table",
                        desc="This area seems to appear only when you're nearby.",
                        items=[novel, phone_charger],
                        position=(-2, 2))

# patrons
jimbo = char.Patron(name="Jimbo",                                           #.patron name
                    area=sm_table,                                          #.initial area 
                    greeting=("Hey man, " +                                 #.greeting message
                              "someone's selling bracelets over there!"),   #.
                    repeat="Hello again.",                                  #.repeat greeting
                    items=[hippie_headband, napkin2, magic_fork],           #.list of items
                    verbs=("move"),                                         #.verbs
                    assoc=[],                                               #.associations
                    stats=(2,1,1),                                          #.stats:
                                                                            #.(atk,def,dodge)
                    points=[25,1,10],                                       #.points:
                                                                            #.[hp,stress,money]
                    trade_pars=(0.5, 5, 7) )                                #.trade parameters:
                                                                            #.(amplitude,scale,offset)

soccermom = char.Patron(name="Debra", area=line,
                   greeting="Hey, no cutting! I need my coffee!",
                   repeat="You're just not with it...",
                   items=[scarf2, sunglasses], verbs=("move"), assoc=["wealthy"],
                   stats=(3,2,2), points=[23,6,251], trade_pars=(-0.5, 2, 4) )

student = char.Patron(name="Osgood", area=line,
                   greeting="Don't bother me, I have studying to do.",
                   repeat="Yeah, still studying...",
                   items=[textbook, pen], verbs=("move"), assoc=["university"],
                   stats=(2,1,2), points=[20,5,34], trade_pars=(0.6, 2, 6) )

questionable = char.Patron(name="Zapp", area=fixins,
                   greeting="Hey there, would you happen to have any spare change for a latte?",
                   repeat="Any change?",
                   items=[pen2], verbs=("move"), assoc=[""],
                   stats=(3,0,3), points=[25,2,9], trade_pars=(0.8, 1, 12) )

normal = char.Patron(name="Frank", area=counter_pickup,
                   greeting="Hey, you seem nice. Just waiting here for my espresso...",
                   repeat="Where's my espresso?",
                   items=[workbelt, pen3], verbs=("move"), assoc=[],
                   stats=(3,3,0), points=[25,3,57], trade_pars=(-0.4, 3, 10) )

berta = char.Patron(name="Berta", area=counter_edge,
                    greeting="I think this place smells like fish...",
                    repeat="You're still here?",
                    items=[key_chain2, coffee], verbs=("move"), assoc=[],
                    stats=(1,1,3), points=[20,8,23], trade_pars=(-0.8, 2, 17) )

stranger = char.Patron(name="Stranger", area=sm_bar,
                   greeting=".... <looks away>",
                   repeat=".... <stares back>",
                   items=[espresso, odd_spoon2], verbs=("move"), assoc=[""],
                   stats=(4,1,2), points=[25,1,15], trade_pars=(0.1, 2, 5) )

strawb = char.Patron(name="Strawberry", area=big_table_R,
                     greeting="Hey there! Would you like to buy a friendship bracelet?",
                     repeat="Back for the bracelets?",
                     items=[bracelet, bracelet2, bracelet3], verbs=("move"), assoc=[],
                     stats=(1,1,4), points=[22,2,8], trade_pars=(-0.4, 3, 12) )

suit = char.Patron(name="Bob", area=big_table_R,
                   greeting="Please leave me alone, I'm very busy.",
                   repeat="Don't make me have you removed...",
                   items=[watch, fancy_pen, coffee2], verbs=("move"), assoc=["wealthy"],
                   stats=(3,3,1), points=[25,5,387], trade_pars=(0.7, 2, 10) )

hipster = char.Patron(name="Jonarthy", area=big_table_L,
                   greeting="Have you heard of Himalayan truffle super crystals?",
                   repeat="You're just not with it...",
                   items=[espresso2, hipster_hat], verbs=("move"), assoc=["wealthy"],
                   stats=(2,1,1), points=[21,3,107], trade_pars=(-0.6, 2, 10) )

cashier = char.Patron(name="April", area=cash_register,
                      greeting="Hello, do you want to buy something?",
                      repeat="Why don't you get a latte?",
                      items=[latte, coffee3, espresso3, mug3], verbs=("move"), assoc=["worker"],
                      stats=(2,2,2), points=[28,4,42], trade_pars=(0.2, 1, 5) )
                                     

# to begin, we call the method on the game object
theGame.begin(thePlayer, outside)

# collect garbage
del fork, napkin, coffee, napkin2, key_chain2, fork2, coffee2, latte
del silly_hat, magic_fork, hippie_headband, mug, mug2
del watch, fancy_pen, bracelet, bracelet2, bracelet3
del jimbo, berta, strawb, suit, cashier
del thePlayer
del sm_table, entrance, outside, wait_bench, counter_edge, cash_register, big_table_R
del theGame
