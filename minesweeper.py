# Minröjare 
# Marcus Lord T-22

# Imported liberies
from datetime import *
from tkinter import *
import random
from collections import deque

# Global variables
level = 0 # Game level 1-4
number_of_mines = 0 # Amount of mines
game_height = 0 # Board width
game_width = 0 # Board height
start_time = 0 # For timer
status_normal = 0 # Status for tile that is not clicked
status_clicked = 1 # Status for tile that is clicked
status_flaged = 2 # Status for tile that is flaged (right clicked)

# Class for game
class Minesweeper:
    # Accessing global variabels
    global number_of_mines, game_height, game_width, status_normal, status_clicked, status_flaged

    # Initiation function for Minesweeper
    def __init__(self, tk):
        # Importing game images
        self.images = {'plain': PhotoImage(file = 'images/gräs.png'), 'clicked': PhotoImage(file = 'images/jord.png'), 'mine': PhotoImage(file = 'images/mina.png'), 'flag': PhotoImage(file = 'images/flagga.png'), 'wrong': PhotoImage(file = 'images/fel_flagga.png'), 'numbers': []}

        for i in range(1, 9):  
            self.images['numbers'].append(PhotoImage(file = 'images/'+str(i)+'.png'))

        # Set up frame for game
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # Set up labels
        self.labels = {'mines': Label(self.frame, text = 'Mines: 0'), 'flags': Label(self.frame, text = 'Flags: 0')}
        # Bottom left
        self.labels['mines'].grid(row = game_height+1, column = 0, columnspan = int(game_width/2)) 
        # Bottom right
        self.labels['flags'].grid(row = game_height+1, column = int(game_width/2)-1, columnspan = int(game_width/2)) 

        # Start game
        self.setup()
        self.refresh_labels()

    # Function for setting up game board
    def setup(self):
        # Create flag and clicked tile variables
        self.flag_count = 0
        self.correct_flag_count = 0
        self.clicked_count = 0

        # Create buttons for every tile
        self.tiles = dict({})
        self.mines = number_of_mines

        # Amount of tiles is board height times width
        tiles = game_width * game_height

        # Used to store mines positions
        mine_pos = []
        i = 0
        pos_in_grid = 0

        # Randomizing mine position
        while i < number_of_mines:
            pos = random.randint(0, tiles)
            # If this position is already taken, i is not iterated and the loop is done again
            if pos in mine_pos:
                i += 0
            # The randomized position is not taken so the position is appended and i is iterated
            else:
                mine_pos.append(pos)
                i += 1

        for x in range(0, game_height):
            for y in range(0, game_width):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + '_' + str(y)

                # Checks if current tile is a tile with a mine on
                if pos_in_grid in mine_pos:
                    is_it_mine = True
                else:
                    is_it_mine = False

                # This is calculated after grid is built
                tile = {'id': id, 'is_it_mine': is_it_mine, 'state': status_normal, 'coords':{ 'x': x, 'y': y}, 'button': Button(self.frame, image = self.images['plain']), 'mines': 0}

                # Tile is bind function when left clicked
                tile['button'].bind('<Button-1>', self.on_click_wrapper(x, y))
                # Tile is bind to function right clicked
                tile['button'].bind('<Button-2>', self.on_right_click_wrapper(x, y))
                tile['button'].grid( row = x, column = y )

                self.tiles[x][y] = tile

                # This is iterated and tells which tile number we are on
                pos_in_grid += 1

        # Loop again to find nearby mines and display number on tile
        for x in range(0, game_height):
            for y in range(0, game_width):
                mc = 0
                for n in self.get_neighbors(x, y):
                    mc += 1 if n['is_it_mine'] else 0
                self.tiles[x][y]['mines'] = mc

    def refresh_labels(self):
        self.labels['flags'].config(text = 'Flags: '+str(self.flag_count))
        self.labels['mines'].config(text = 'Mines: '+str(self.mines))

    def game_over(self, won):
        for x in range(0, game_height):
            for y in range(0, game_width):
                if self.tiles[x][y]['is_it_mine'] == False and self.tiles[x][y]['state'] == status_flaged:
                    self.tiles[x][y]['button'].config(image = self.images['wrong'])
                if self.tiles[x][y]['is_it_mine'] == True and self.tiles[x][y]['state'] != status_flaged:
                    self.tiles[x][y]['button'].config(image = self.images['mine'])

        self.tk.update()

        # Calling game result, sending win or loss status
        if won == True:
            game_result(1)
        else:
            game_result(0)

    def get_neighbors(self, x, y):
        neighbors = []

        # Coordinates for nearby tiles
        coords = [
            {'x': x-1,  'y': y-1},  # Top right
            {'x': x-1,  'y': y},    # Top middle
            {'x': x-1,  'y': y+1},  # Top left
            {'x': x,    'y': y-1},  # Left
            {'x': x,    'y': y+1},  # Right
            {'x': x+1,  'y': y-1},  # Bottom right
            {'x': x+1,  'y': y},    # Bottom middle
            {'x': x+1,  'y': y+1},  # Bottom left
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n['x']][n['y']])
            except KeyError:
                pass
        return neighbors

    def on_click_wrapper(self, x, y):
        return lambda Button: self.on_click(self.tiles[x][y])

    def on_right_click_wrapper(self, x, y):
        return lambda Button: self.on_right_click(self.tiles[x][y])

    def on_click(self, tile):
        # Checks if you click on mine
        if tile['is_it_mine']:
            self.game_over(False)
            return

        # Change image if tile is not mine
        if tile['mines'] == 0:
            tile['button'].config(image = self.images['clicked'])
            self.surrounding_sweeper(tile['id'])
        else:
            tile['button'].config(image = self.images['numbers'][tile['mines']-1])

        # If not already set as clicked, change state and count
        if tile['state'] != status_clicked:
            tile['state'] = status_clicked
            self.clicked_count += 1
        if self.clicked_count == (game_height * game_width) - self.mines:
            self.game_over(True)

    def on_right_click(self, tile):
        # If not clicked
        if tile['state'] == status_normal:
            tile['button'].config(image = self.images['flag'])
            tile['state'] = status_flaged
            tile['button'].unbind('<Button-1>')
            # If tile contains a mine
            if tile['is_it_mine'] == True:
                self.correct_flag_count += 1
            self.flag_count += 1
            self.refresh_labels()

        # Toggle if already flaged
        elif tile['state'] == 2:
            tile['button'].config(image = self.images['plain'])
            tile['state'] = 0
            tile['button'].bind('<Button-1>', self.on_click_wrapper(tile['coords']['x'], tile['coords']['y']))
            
            # If tile contains a mine
            if tile['is_it_mine'] == True:
                self.correct_flag_count -= 1
            self.flag_count -= 1
            self.refresh_labels()

    def surrounding_sweeper(self, id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split('_')
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.get_neighbors(x, y):
                self.sweeper(tile, queue)

    def sweeper(self, tile, queue):
        if tile['state'] != status_normal:
            return

        if tile['mines'] == 0:
            tile['button'].config(image = self.images['clicked'])
            queue.append(tile['id'])
        else:
            tile['button'].config(image = self.images['numbers'][tile['mines']-1])

        tile['state'] = status_clicked
        self.clicked_count += 1

def create_high_score_file():
    fr = open('high_score_minesweeper.txt', 'w+')
    # Writes every item in list on newline
    for i in range(10):
        fr.write('Easy O:OO:OO OO/OO/OOOO\n')
        fr.write('Medium O:OO:OO OO/OO/OOOO\n')
        fr.write('Hard O:OO:OO OO/OO/OOOO\n')
        fr.write('Extreme O:OO:OO OO/OO/OOOO\n')

# Importing former result from high score file and making lists
def list_maker(list_write, labels):
    list_in = []

    try:
        fr = open('high_score_minesweeper.txt', 'r')
            
    except:
        create_high_score_file()
        fr = open('high_score_minesweeper.txt', 'r')

    for line in fr:
        list_in.append(line.strip())

    i = 0
    for j in labels:
        for k in list_in:
            if (k.find(j) == 0):
                list_write[i].append(k)
        i += 1

    # Empties the high score text file
    fw = open('high_score_minesweeper.txt', 'w')
    fw.truncate(0) 

# Writing top 10 results into high score file
def write_high_score (list_write):
    f = open('high_score_minesweeper.txt', 'a')
    # Writes every item in list on newline
    f.write('\n'.join(list_write[0:10]))
    f.write('\n')

# Function for combining functions called in button
def combine_functions(*funcs):
    def combine_functions(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combine_functions

def level_choice(level_choise):
    global level, number_of_mines, game_height, game_width
    
    level = level_choise

    # Have to be "hård kodat" because game board does not follow a mathematic pattern
    if level == 0:
        number_of_mines = 10
        game_height = 10
        game_width = 10
    elif level == 1:
        number_of_mines = 20
        game_height = 16
        game_width = 16
    elif level == 2:
        number_of_mines = 50
        game_height = 16
        game_width = 22
    elif level == 3:
        number_of_mines = 100
        game_height = 16
        game_width = 30

def game_setup():
    # Create tkinter game_window for game_setup
    game_setup_game_window = Tk()

    # Set game_window size
    game_setup_game_window.geometry('600x300')
    # Set titel
    game_setup_game_window.title('Minesweeper: Rules and Setup')

    # Insert text with game rules
    text = Text(game_setup_game_window, height=12, width=60, font=('Usual',15))
    text.insert(INSERT, '''Welcome to Minesweeper!

Use the left click to select a space on the grid. If you hit a bomb, you lose.
The numbers on the board represent how many bombs are adjacent to a square. 
For example, if a square has a '3' on it, then there are 3 bombs next to that square. 
The bombs could be above, below, right left, or diagonal to the square. 
Avoid all the bombs and expose all the empty spaces to win Minesweeper. 
You can right click a square with the mouse to place a flag where you think a 
bomb is. This allows you to avoid that spot. 

Choose your level and write your name and choose level below, good luck!''')

    # Text box placement
    text.place(x=0, y=0)
    text['state'] = 'disabled'
    
    # Button box creation and placement
    button = Button(game_setup_game_window, text='Easy', width=6, font=('Usual',30), fg='#17FF00', command=lambda: combine_functions(level_choice(0), game_setup_game_window.destroy()))
    button.place(x=0, y=240)

    button = Button(game_setup_game_window, text='Medium',width=6, font=('Usual',30), fg='#FFC100', command=lambda: combine_functions(level_choice(1), game_setup_game_window.destroy()))
    button.place(x=150, y=240)

    button = Button(game_setup_game_window, text='Hard', width=6, font=('Usual',30), fg='#FF6400', command=lambda: combine_functions(level_choice(2), game_setup_game_window.destroy()))
    button.place(x=300, y=240)

    button = Button(game_setup_game_window, text='Extreme', width=6, font=('Usual',30), fg='#FF0400', command=lambda: combine_functions(level_choice(3), game_setup_game_window.destroy()))
    button.place(x=450, y=240)

    game_setup_game_window.mainloop()

# Called after game over, variabel in is 1 for win or 0 for loss
def game_result(winner):
    # Accessing global variabels
    global start_time, result, level

    # Stoping time
    stop = datetime.now().strftime('%H:%M:%S')
    stop_time = datetime.strptime(stop, '%H:%M:%S')
    
    # Calculating total game time
    total_gametime = (stop_time - start_time)

    # List for 10 best scores
    high_score_list_easy = []
    high_score_list_medium = []
    high_score_list_hard = []
    high_score_list_extreme = []

    # All list in one list for eaier access
    level_list = [high_score_list_easy, high_score_list_medium, high_score_list_hard, high_score_list_extreme]
    level_lables = ['Easy', 'Medium', 'Hard', 'Extreme']

    # Calling function that reads from high score file and makes a list
    list_maker(level_list, level_lables)

    # Create tkinter game_window result
    game_result_window = Tk()

    # Set game_window size
    game_result_window.geometry('300x350')

    # Set titel
    game_result_window.title('Minesweeper: Result')

    # If you won the game
    if winner:
        level_label = level_lables[level]

        todays_date = datetime.now().strftime('%d/%m/%Y')
        result = level_label + ' ' + str(total_gametime) + ' ' + str(todays_date)

        # Adding result from game and sorting
        level_list[level].append(result)
        level_list[level].sort()
        display_list = level_list[level]

        for i in (level_list):
            write_high_score(i)
        
        # Insert text with game rules
        text = Text(game_result_window, height=14, width=30, font=('Usual',15))
        text.insert(INSERT, 'Top 10 result:\n')
        for i in range(0, 10):
            text.insert(INSERT, display_list[i])
            text.insert(INSERT, '\n')
        text.insert(INSERT, '\nYour result: ')
        text.insert(INSERT, result)

        text.place(x=0, y=0)
        text['state'] = 'disabled'

        button = Button(game_result_window, text='Quit', width=6, font=('Usual',30), fg='#FF6400', command=lambda: exit(0))
        button.place(x=70, y=300)

        game_result_window.mainloop()

    # Else if you lost
    else:
        for i in (level_list):
            write_high_score(i)

        display_list = level_list[level]

        # Insert text with game rules
        text = Text(game_result_window, height=16, width=30, font=('Usual',15))
        text.insert(INSERT, 'Top 10 result:\n')
        for i in range(0, 10):
            # If error occurs on this line, the high score file is probably empty
            # Please restore the high score file or delete it!
            text.insert(INSERT, display_list[i])
            text.insert(INSERT, '\n')
        text.insert(INSERT, '\n\nGame over, you died!\nRestart the program and try again!')

        text.place(x=0, y=0)
        text['state'] = 'disabled'

        button = Button(game_result_window, text='Quit', width=6, font=('Usual',30), fg='#FF6400', command=lambda: exit(0))
        button.place(x=70, y=300)

        game_result_window.mainloop()

def main_game_loop():
    # Calling function for game setup and rules
    game_setup()

    # Needs to be global, is accesed in diffrent functions
    global start_time

    # Starting timer
    start = datetime.now().strftime('%H:%M:%S')
    start_time = datetime.strptime(start, '%H:%M:%S')

    # Create Tk instance
    game_window = Tk()
    # Set program title
    game_window.title('Minesweeper')

    Minesweeper(game_window)
    # Run event loop
    game_window.mainloop()
    
main_game_loop()