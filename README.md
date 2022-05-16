# getCoffee
A simple text-based coffee-themed game!

### main_getCoffee
- This is the file you should run if you want to play the game.
- Depends upon 'game' (mechanics) and 'characters' (player/NPCs, items).
- Items, Areas, and Characters are all defined here to initialize the game.
- Feel free to check / edit as you see fit.
  - Play with options!  Try adding your own Items / Characters!  (Be sure to place them in some Area.)
  - EXCEPT: 'theGame' and 'thePlayer' objects should be left alone.
- Game is launched with 'theGame.begin()'

### characters_getCoffee
- Defines how all game characters behave.
- Each has hit points, stress, money, and some inventory.
- Base 'Character' class is defined.  
    - 'Player' and 'Patron' derive from there, for player and NPCs, respectively.

### game_getCoffee
- Defines all game mechanics, all input/output, and other details in 'Game' class. 
- Also defines 'Area' class for map building / tracking.
