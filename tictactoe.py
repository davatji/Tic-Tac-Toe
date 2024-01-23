import tkinter as tk
import random

'''
General Overview

Creating basic tic tac toe game using toolkit interface through creating grid consisting of 9 buttons that mimics tic tac toe's button.
Each button has its 2 dimensional index that corresponds to 2D list that holds the value of each cell (X, O, or None). 
By the time the player press the button, the program will determine which turn is it and "populate" the grid with X or O, depending on the turn.
After pressing the button, the program will check whether the state (the game) is on terminal state (state where the game has ended) and determine the winner.
The check of terminal state is done by checking the 2D list, whether there are 3-straight Xs or Os, or all the cell has been populated.

The opponent of the game is a computer. The computer will decide the move by implementing minimax algorithm. Essentially, the computer will put itself on
the opponent shoes recursively, as if it overlooked on every move possibilities and decide the one that guarantee the computer to win or at least draw

'''

#class for each cell in the grid for ease in adressing the cells by its index and storing X or O value
class _Cell(tk.Button):
    def def_coord(self, x, y):
        self.x = x
        self.y = y
        self._value = None
        self._is_filled = False
    
    def fill(self, value):
        if not self._is_filled:
            self._value = value
            self._is_filled = True

    def get_value(self):
        return self._value
    
    def is_filled(self):
        return self._is_filled
    
    def clear(self):
        self._value = None
        self._is_filled = False
        self.config(text = "")

#"action" refers to what move is done (consisting of indexes of the move in the grid)
class _Action:
    def __init__(self, x, y):
        self.x = x
        self.y = y

#application class. create a window / root and its widgets and computer entity using minimax algorithm to form a Tic Tac Toe game interface
class TicTacToe:

    _background_color = "#666666"

    _grid_length_in_cell = 3
    _cell_length = 2

    #during initialization: initializing inst. vars -> creating widgets -> run the app -> user press buttons, invoking methods to modify the tic tac toe game
    def __init__(self, autoplay = False):
        self._master = tk.Tk()
        self._run_game = False
        self._winner = None
        self._state = [[None, None, None],
                        [None, None, None],
                        [None, None, None]]
        
        self._configure_master()

        self._create_controller()
        self._create_grid()
        self._create_additional_widgets()

        self._disable_grid()

        if autoplay:
            #start the game if autoplay mode
            self._initialize_game()
        
        self._run_app()

    #modifying master for visual appealance purpose
    def _configure_master(self):
        self._master.geometry("510x480")
        self._master.title("Tic Tac Toe")
        self._master.configure(background = TicTacToe._background_color)

    #controller panel, allowing user to set the parameters necessary for algorithm implementation and how the game is run
    def _create_controller(self):
        
        self._controller_frame = tk.Frame(self._master, 
                                          width = 180,
                                          background = TicTacToe._background_color)
        self._controller_frame.grid(column = 0, row = 1, rowspan = 3, sticky = "ns", padx = 15)

        #allowing user to choose their player representation, which are X or O
        self._choose_player_repr_label = tk.Label(self._controller_frame, 
                                                  text = "Choose player:", 
                                                  font = ("Verdana", 12),
                                                  background = TicTacToe._background_color)
        self._choose_player_repr_label.grid(column = 0, row = 0)

        player_repr_options = ["X", "O"]

        #the code will exploit the functionality of powerful StringVar object, as the change in StringVar would be reflected on the widgets during the mainloop method
        self._chosen_player_repr = tk.StringVar(self._controller_frame, value = player_repr_options[0])

        for index in range(len(player_repr_options)):
            option = tk.Radiobutton(self._controller_frame,
                                    value = player_repr_options[index],
                                    text = f"{player_repr_options[index]} player",
                                    variable = self._chosen_player_repr,
                                    background = TicTacToe._background_color,
                                    activebackground = TicTacToe._background_color)
            
            option.grid(column = 0, row = index + 1)

        #placeholder to create an empty space in-between sections
        tk.Label(self._controller_frame, font = ("Verdana", 12), background = TicTacToe._background_color).grid(column = 0, row = 3)

        #allowing users to decide which agent makes the first move: computer or themselves
        self._first_agent_label = tk.Label(self._controller_frame, 
                                           text = "First turn:", 
                                           font = ("Verdana", 12),
                                           background = TicTacToe._background_color)
        self._first_agent_label.grid(column = 0, row = 4)

        agents = ["Human", "Computer"]

        self._first_agent = tk.StringVar(self._controller_frame, value = agents[0])

        for index in range(len(agents)):
            option = tk.Radiobutton(self._controller_frame,
                                    value = agents[index],
                                    text = agents[index],
                                    variable = self._first_agent,
                                    background = TicTacToe._background_color,
                                    activebackground = TicTacToe._background_color)
            option.grid(column = 0, row = index + 5)

        #placeholder
        tk.Label(self._controller_frame, font = ("Verdana", 12), background = TicTacToe._background_color).grid(column = 0, row = 7)

        #allowing users to choose game difficulties. the game difficulty determine how often does the computer use the minimax algorithm
        #normal difficulty means that the computer uses minimax algorithm 80% of the time. hard: 95%. impossible: 100%
        self._difficulty_label = tk.Label(self._controller_frame, 
                                          text = "Difficulty:", 
                                          font = ("Verdana", 12),
                                          background = TicTacToe._background_color)
        self._difficulty_label.grid(column = 0, row = 8)
        
        difficulties = ["Normal", "Hard", "Impossible"]

        self._difficulty = tk.StringVar(self._controller_frame, value = difficulties[0])

        for index in range(len(difficulties)):
            option = tk.Radiobutton(self._controller_frame,
                                    value = difficulties[index],
                                    text = difficulties[index],
                                    variable = self._difficulty,
                                    background = TicTacToe._background_color,
                                    activebackground = TicTacToe._background_color)
            option.grid(column = 0, row = index + 9)

    #initializing grid widget, consisting of 9 clickable cells (subclass of button). clicking cell == choosing which X or O to put at
    def _create_grid(self):

        self._grid = []
        for y in range(self._grid_length_in_cell):
            row = []
            for x in range(self._grid_length_in_cell):
                cell = _Cell(master = self._master,
                             height = self._cell_length,
                             width = self._cell_length * 2,
                             text = "",
                             font = ("Verdana", 25),
                             padx = 0, pady = 0)
                
                cell.def_coord(x, y)
                cell.config(command = lambda x = cell.x, y = cell.y: self._move(x, y))
            
                cell.grid(column = x + 1, row = y + 1)
                row.append(cell)

            self._grid.append(row)
    
    #additional widgets such as the game title and play / restart button
    def _create_additional_widgets(self):
        self._label_string = tk.StringVar(self._master, "Tic Tac Toe Game")
        self._label_indicator = tk.Label(textvariable = self._label_string, 
                                         font = ("Verdana", 22), 
                                         pady = 20, 
                                         background = TicTacToe._background_color)
        
        self._label_indicator.grid(column = 1, columnspan = 3, row = 0)
        self._play_button = tk.Button(self._master, text = "Play", height = 3, width = 10, command = self._initialize_game)
        self._play_button.grid(column = 2, row = 4)
    
    def _run_app(self):
        self._master.mainloop()

    #will be run whenever play / restart button is clicked. effectively restarting all the game state to initial value     
    #invoked when autoplay mode is on or play / restart button is clicked 
    def _initialize_game(self):
        self._run_game = True
        self._winner = None
        self._label_string.set("Tic Tac Toe Game")
        self._clear_grid()
        self._clear_state()
        self._enable_grid()

        self._play_button.config(text = "Restart")

        human_repr = self._chosen_player_repr.get()
        computer_repr = "X" if human_repr == "O" else "O"

        if self._first_agent.get() == "Computer":
            self._initial_repr = computer_repr
            self._move_computer()
        else:
            self._initial_repr = human_repr
    
    #method invoked when the player makes a move (pressing the cell). modifying the button that is being clicked and the 2D list (game state)
    def _move(self, x, y):
        cell = self._grid[y][x]

        #the method is only effective when the cell hasn't already been occupied
        if not cell.is_filled() and self._run_game:
            player = TicTacToe._player(self._state, self._initial_repr)
            cell.fill(player)
            cell.config(text = player)

            self._state[y][x] = player 

            post_game_state = TicTacToe._check_terminal_state(self._state)
            is_terminal_state = post_game_state[0]
            score = post_game_state[1]

            #if the resulting state is the terminal state, declare the winner
            if is_terminal_state:
                self._winner = TicTacToe._get_winner(score)

                if self._winner == "Draw":
                    self._label_string.set(self._winner)
                else:
                    self._label_string.set(f"{self._winner} Wins")

                self._run_game = False
                self._disable_grid()

            #if the game is still continuable, it's time for the computer to take move
            else:
                self._move_computer()

    #invoked when computer makes a move, which happens during the game initialization when the computer is set to take the first turn or after the human's move
    def _move_computer(self):
        if self._run_game:

            #computer probably takes some time to make move, thus the grid is temporarily disabled to prevent user from making move 
            self._disable_grid()

            #getting turn, calculating the amount of x and o in the grid. output: X or O
            player = TicTacToe._player(self._state, self._initial_repr)

            difficulty = self._difficulty.get()

            #getting the game difficulty that determines the threshold that decides how often does the computer use minimax algorithm
            if difficulty == "Normal":
                threshold = 0.2
            elif difficulty == "Hard":
                threshold = 0.05
            else:
                threshold = 0
            
            random_determinator = random.randint(0, 100)
            normalized_random_determinator = random_determinator / 100

            if normalized_random_determinator >= threshold:
                #minimax algorithm. translating the concept of winning into 1, 0, and -1. conventially, X win refers to 1, O win refers to -1, and draw refers to 0
                #the decision of algorithm depends on which player does the computer use. if the computer's objective is to gain score 1 (player X), it will use max alg. & vica versa
                if player == "X":
                    decision = TicTacToe._max_value(self._state, self._initial_repr)
                else:
                    decision = TicTacToe._min_value(self._state, self._initial_repr)

                action = decision[1]
            else:
                action = random.choice(TicTacToe._get_actions(self._state))

            #modiying cells as a visual indicator that the cell has been populated with X or O
            cell = self._grid[action.y][action.x]
            cell.fill(player)
            cell.config(text = player)

            self._state[action.y][action.x] = player

            self._enable_grid()

            post_game_state = TicTacToe._check_terminal_state(self._state)
            is_terminal_state = post_game_state[0]
            score = post_game_state[1]

            #if the resulting state is the terminal state: declare the winner
            if is_terminal_state:
                self._winner = TicTacToe._get_winner(score)

                if self._winner == "Draw":
                    self._label_string.set(self._winner)
                else:
                    self._label_string.set(f"{self._winner} Wins")

                self._run_game = False
                self._disable_grid()
            
    def _enable_grid(self):
        for row in self._grid:
            for cell in row:
                cell.config(state = "active")

    def _disable_grid(self):
        for row in self._grid:
            for cell in row:
                cell.config(state = "disabled")

    def _clear_grid(self):
        for row in self._grid:
            for cell in row:
                cell.clear()

    def _clear_state(self):
        for y in range(len(self._state)):
            for x in range(len(self._state[0])):
                self._state[y][x] = None
            
    #checking whether the current state is a terminal state (where the game ends with or without winner)
    def _check_terminal_state(state):
        score = None

        #checking horizontally the consecutive 3 Xs or Os
        for row in state:
            xs = row.count("X")
            os = row.count("O")
            if xs == 3:
                return (True, 1)
            elif os == 3:
                return (True, -1)
                
        #checking vertically
        for x in range(len(state[0])):
            if state[0][x] != None and state[0][x] == state[1][x] == state[2][x]:
                score = 1 if state[0][x] == "X" else -1
                return (True, score)
            
        #checking diagonally 
        if state[0][0] != None and state[0][0] == state[1][1] == state[2][2]:
            score = 1 if state[0][0] == "X" else -1
            return (True, score)
        
        if state[2][0] != None and state[2][0] == state[1][1] == state[0][2]:
            score =  1 if state[2][0] == "X" else -1
            return (True, score)

        #check whether the game has ended by circumstance where all cells have been filled
        for rows in state:
            for cell in rows:
                if cell == None:
                    #if one of the cell hasn't yet been filled, it is implied that the game hasn't yet ended (since at this point, consecutive 3 Xs or Os conditions aren't met) 
                    return (False, score)
        score = 0

        return (True, score)
    
    '''
    Minimax algorithm documentation

    Initially, the computer will find all the possible actions / moves to choose. 
    The potential actions / moves then are applied to the clone of state (copy of 2D list), resulting in the new state.
    How does the computer know whether an action / move is the best move? The computer will put itself on the opponent's shoes.
    Assuming that the computer player is X. It will implement max_value method and put itself on the opponent perspective to evaluate each projected / new state.
    The evaluation of each new state is done by implementing the opposite logic: min_value method, since the opponent has opposite objective to the computer.
    This process will be done recursively until it hits the base case where the min_value or max_value methods return the terminal state score (when the game hits terminal state).
    The value get from base case then will be pased all the way up to the original method (the first method to be called) and this method will return the best score with its action.
    With best action known, the computer use that action to make the move.
    '''

    #additionally passing initial_repr. meaning: which player makes the turn (X or O) to be passed on the player method
    def _max_value(state, initial_repr):

        game_state = TicTacToe._check_terminal_state(state)
        
        is_terminal_state = game_state[0]

        score = game_state[1]

        #base case where the state is the terminal state. plainly returns the score (1, 0, or -1)
        if is_terminal_state:
            return (score, None)
        
        player = TicTacToe._player(state, initial_repr)
        
        possible_actions = TicTacToe._get_actions(state)

        #minus infinity to ensure that the algorithm runs nevertheless how little is the value of an action
        max_value = float("-inf")
        chosen_action = None

        for action in possible_actions:
            projected_state = TicTacToe._deep_copy(state)

            #modify state: projected state for each action
            projected_state[action.y][action.x] = player

            #putting the agent on the opponent shoes, reversing the algorithm until it hits base case
            action_value = TicTacToe._min_value(projected_state, initial_repr)[0]

            #choosing the best action among all possible actions 
            if action_value > max_value:
                max_value = action_value
                chosen_action = action

        #returning max value and chosen action. max value is necessary for recursion, while chosen action is necessary to know which action is the best
        return (max_value, chosen_action)

    #same general principle, exactly opposite logic
    def _min_value(state, initial_repr):
        game_state = TicTacToe._check_terminal_state(state)
        is_terminal_state = game_state[0]
        score = game_state[1]

        if is_terminal_state:
            return (score, None)

        player = TicTacToe._player(state, initial_repr)
        
        possible_actions = TicTacToe._get_actions(state)

        min_value = float("inf")
        chosen_action = None

        for action in possible_actions:
            projected_state = TicTacToe._deep_copy(state)
            #modify state: projected state for each action
            projected_state[action.y][action.x] = player

            #putting the agent on the opponent shoes, reversing the algorithm
            action_value = TicTacToe._max_value(projected_state, initial_repr)[0]

            if action_value < min_value:
                min_value = action_value
                chosen_action = action
                
        return (min_value, chosen_action)
    
    #determining which turn it is based on the current game state and who goes first
    def _player(state, initial_value):

        #calculating the amount of x and o. if one is bigger than the other, put the other as the current turn
        x = sum(row.count("X") for row in state)
        o = sum(row.count("O") for row in state)

        if x < o:
            return "X"
        elif x > o:
            return "O"
        
        #case where the number of Xs and Os are the same: the turn belongs to the one who took the initial turn
        else:
            return initial_value

    #getting all the possible actions / moves in given state
    def _get_actions(state):
        actions = []

        for y in range(len(state)):
            for x in range(len(state[0])):
                if state[y][x] == None:
                    actions.append(_Action(x, y))

        return actions
    
    #converting score to qualitative value: name of the winner player
    def _get_winner(score):
        if score == 1:
            return "X"
        elif score == -1:
            return "O"
        elif score == 0:
            return "Draw"
        else:
            return None
    
    #defining deep copy method to clone the state so that when projecting potential moves to the state in the minimax algorithm, the original state 2D list won't be modified 
    def _deep_copy(state):
        state_copy = []

        for row in state:
            row_copy = []

            for value in row:
                row_copy.append(value)

            state_copy.append(row_copy)
        
        return state_copy

def main():
    TicTacToe()

if __name__ == "__main__":
    main()
