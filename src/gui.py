import datetime
import tkinter as tk
from tkinter import font as tkfont
from os.path import dirname
import game
from exceptions import CannotMoveException
from game import Game
from board import Board
from enums import InitialBoardState
from enums import MoveDirection
from enums import GameMode
from enums import PieceType
from statespacegenerator import StateSpaceGenerator
import random

PATH = dirname(__file__)
bgcolor = '#FFFAF0'
options = {'bg': bgcolor, 'font': (None, 15, 'bold')}


def marble_tuple_to_string(marble_tuple):
    marble_str = ""
    count = 0
    for item in marble_tuple:
        marble_str += ''.join(str(i) for i in item)
        count += 1
    return marble_str


def destroy_widget(to_destroy):
    if to_destroy is not None:
        to_destroy.place_forget()
        if to_destroy is not None:
            to_destroy.destroy()


class MainWindow(tk.Tk):
    """
    Main window of application
    """

    def __init__(self):
        super().__init__()
        self.game_settings = {}
        self.board_operation = None
        self.operation = None
        self.output = None
        self.current_turn_info = None
        self.move_time_elapsed = 0
        self._game = None
        self.countdown_timer = None
        self.best_move = None
        self.game_over_screen = None
        self.settings = SettingsPage(self)  # This will be shown upon launch
        self.settings.pack(fill="both", expand=True)

    def start_game_ui(self):
        """
        Called after settings' start game button is clicked, will show the actual game ("second page") UI ,
        and set all the game configs.
        """
        self._game = Game()
        self._game.set_game_parameters(**self.game_settings)
        self._game.start_game()
        self.settings.destroy()

        # MUST separate the place and constructor calls, otherwise assignment will not be properly made
        self.countdown_timer = CountdownTimer(self)
        self.countdown_timer.place(x=30, y=80)

        self.best_move = BestMove(self)
        self.best_move.place(x=340, y=50)

        self.current_turn_info = CurrentTurnInfo(self)
        self.current_turn_info.place(x=30, y=50)

        self.board_operation = BoardOperation(self)
        self.board_operation.place(x=30, y=150)
        self.board_operation.suggest_first_random_move()  # Suggests the first random move if computer is black

        self.output = Output(self)
        self.output.place(x=630, y=155)

        self.operation = Operation(self)
        self.operation.place(x=600, y=50)

        self.game_over_screen = GameOver(self)

    def get_game(self):
        """
        Returns game
        :return: Game
        """
        return self._game

    def check_for_game_won(self, piece_type):
        """
        Checks if the game has been won by the given piece type, and shows game over frame accordingly
        :param piece_type: PieceType enum
        """
        if self._game.has_piece_type_won(piece_type):
            if piece_type is piece_type.BLACK:
                self.game_over_screen.show_winner_text("Black")
            else:
                self.game_over_screen.show_winner_text("White")


class GameOver(tk.Frame):
    """
    Represents a game over frame to show once win condition has been met
    """

    def __init__(self, parent):
        super().__init__(bg=bgcolor)
        self.parent = parent
        self.game_over_lbl = tk.Label(self, text="Game Over!", bg=bgcolor,
                                      font=(None, 50, 'bold')).grid(row=0, column=0, columnspan=2, sticky="W")
        self.game_winner_lbl = None
        self.winner_text_val = None
        self.winner_lbl = None
        self.exit_lbl = None

        self.game_draw_lbl = None
        self.comp_time_lbl = None
        self.comp_time_val = tk.StringVar(self, value="0 s")
        self.comp_time = None

        self.human_score_lbl = None
        self.comp_score_lbl = None

        self.human_score_val = tk.IntVar(0)
        self.comp_score_val = tk.IntVar(0)
        self.human_score = None
        self.comp_score = None

    def show_winner_text(self, winner):
        """
        Sets then shows the winner text value as the winning piece color
        :param winner: a string
        """
        self.game_winner_lbl = tk.Label(self, text="Winner is ...", bg=bgcolor,
                                        font=(None, 40, 'bold')).grid(row=1, column=0, sticky="W")
        self.winner_text_val = tk.StringVar(self, "Black")
        self.winner_lbl = tk.Label(self, textvariable=self.winner_text_val, bg=bgcolor,
                                   font=(None, 40, 'bold')).grid(row=1, column=1, sticky="W")
        self.exit_lbl = tk.Label(self, text="You may exit the game", bg=bgcolor,
                                 font=(None, 40, 'bold')).grid(row=2, column=0, columnspan=2, sticky="W")
        self.winner_text_val.set(winner)
        self.place(relx=.5, rely=.5, anchor="center")

    def show_draw_stats(self):
        """
        Sets the game draw stats, and shows on screen
        :return:
        """
        self.game_draw_lbl = tk.Label(self, text="It is a draw", bg=bgcolor,
                                      font=(None, 40, 'bold')).grid(row=1, column=0, sticky="W")
        self.comp_time_lbl = tk.Label(self, text="Computer cumulative move time: ", bg=bgcolor,
                                      font=(None, 20, 'bold')).grid(row=2, column=0, sticky="W")
        time_taken = str(round(self.parent.get_game().get_comp_player().get_cumulative_move_time(), 2)) + "s"
        self.comp_time_val.set(time_taken)
        self.comp_time = tk.Label(self, textvariable=self.comp_time_val, bg=bgcolor, fg="red",
                                  font=(None, 20, 'bold')).grid(row=2, column=1, sticky="W")

        human_lbl_text = "Human(White) Score"
        comp_lbl_text = "Computer(Black) Score"
        if self.parent.get_game().is_human_piece_black():  # Set player color labels accordingly
            human_lbl_text = "Human(Black) Score"
            comp_lbl_text = "Computer(White) Score"

        self.human_score_lbl = tk.Label(self, text=human_lbl_text, bg=bgcolor,
                                        font=(None, 20, 'bold')).grid(row=3, column=0, sticky="W")
        self.comp_score_lbl = tk.Label(self, text=comp_lbl_text, bg=bgcolor,
                                       font=(None, 20, 'bold')).grid(row=4, column=0, sticky="W")

        self.human_score_val.set(self.parent.get_game().get_human_player().game_score)
        self.comp_score_val.set(self.parent.get_game().get_comp_player().game_score)
        self.human_score = tk.Label(self, textvariable=self.human_score_val, font=(None, 20, 'bold'), fg="purple",
                                    bg=bgcolor)
        self.human_score.grid(row=3, column=1, sticky="W")
        self.comp_score = tk.Label(self, textvariable=self.comp_score_val, font=(None, 20, 'bold'), fg="purple",
                                   bg=bgcolor)
        self.comp_score.grid(row=4, column=1, sticky="W")

        self.place(relx=.5, rely=.5, anchor="center")


class BestMove(tk.Frame):
    def __init__(self, parent):
        super().__init__(bg=bgcolor)
        self.parent = parent
        self.best_move_lbl = tk.Label(self, text="Suggested Move:", bg=bgcolor, font=(None, 20, 'bold'))
        self.best_move_val = tk.Label(self, text="", bg=bgcolor, fg="purple", font=(None, 20, 'bold'))
        self.best_move_lbl.grid(row=0, column=0, sticky="W")
        self.best_move_val.grid(row=1, column=0, sticky="W")
        self.statespacegenerator = StateSpaceGenerator()

    def best_move_to_string(self, best_move_tuple):
        """
        Converts a best movee tuple to a nicely formatted string
        :param best_move_tuple:
        :return:
        """
        best_move_str = ""
        count = 0
        for item in best_move_tuple:
            if count < len(best_move_tuple) - 1:
                best_move_str += ''.join(str(i) for i in item)
            else:
                best_move_str += " " + item.name
            count += 1
        print(best_move_str)
        self.parent.best_move.best_move_val.configure(text=best_move_str)

    def hide_best_move_val(self):
        self.best_move_val.grid_remove()

    def show_best_move_val(self):
        self.best_move_val.grid()


class CountdownTimer(tk.Frame):
    """
    Display (frame) for the counterdown timer
    """

    def __init__(self, parent):
        super().__init__(bg=bgcolor)
        self.parent = parent
        self.game = parent.get_game()
        self.countdown_lbl = tk.Label(self, text="Time left(s):", bg=bgcolor, font=(None, 20, 'bold'))
        self.countdown_time = tk.Label(self, text="", bg=bgcolor, font=(None, 30, 'bold'), fg="red")
        self.countdown_lbl.grid(row=0, column=0)
        self.countdown_time.grid(row=0, column=1)

        self.black_move_time = self.game.black_player.move_time_limit
        self.white_move_time = self.game.white_player.move_time_limit

        self.start_timer = False
        self.starting_secs = self.game.black_player.move_time_limit  # Starts with black's move time
        self.countdown_secs = 0

    def change_starting_time(self, start_time):
        """
        Changes the starting countdown time -> then start_countdown again
        :param start_time: int
        """
        self.starting_secs = start_time

    def countdown(self):
        """
        Counts down the time of timer.
        """
        if self.start_timer:
            if self.countdown_secs == 0:
                self.countdown_time.configure(text="Time's Up!")
                self.start_timer = False
            else:
                self.countdown_time.configure(text="%d" % self.countdown_secs)
                self.countdown_secs -= 1
                self.after(1000, self.countdown)

    def reset_start_time_val(self):
        """
        Resets timer value to starting time
        """
        self.countdown_time.configure(text="%d" % self.starting_secs)

    def start_countdown(self):
        """
        Starts the countdown timer and sets parent time started
        :return:
        """
        if not self.start_timer:
            self.start_timer = True
            self.countdown_secs = self.starting_secs
            self.countdown()

    def pause_countdown(self):
        """
        Pauses the countdown timer and sets parent move_time_elapsed
        :return:
        """
        if self.start_timer:
            self.start_timer = False
            self.starting_secs = self.countdown_secs
            self.parent.move_time_elapsed = self.get_time_elapsed(PieceType.BLACK)
            # hardcoded for now
            print(f"time expired: {self.parent.move_time_elapsed}")  # just showing time elapsed updated in parent

    def reset_countdown(self, piece_type=PieceType.BLACK):
        """
        Resets countdown timer according to piece type passed in
        :param piece_type: PieceType
        """
        if piece_type is PieceType.BLACK:
            self.starting_secs = self.black_move_time
        else:
            self.starting_secs = self.white_move_time
        self.reset_start_time_val()  # Reset start time amount as well

    def get_time_elapsed(self, piece_type=PieceType.BLACK):
        """
        Call this to get the time elapsed
        :return: time elapsed for timer
        """
        if piece_type is PieceType.BLACK:
            return self.black_move_time - self.countdown_secs
        else:
            return self.white_move_time - self.countdown_secs


class SettingsPage(tk.Frame):
    """
    Page (frame) for settings initial page.
    """

    def __init__(self, parent):
        super().__init__(bg='teal')
        paddings = {'padx': 10, 'ipadx': 5, "ipady": 5}
        options1 = {'bg': 'teal', 'fg': bgcolor, 'font': (None, 20, 'bold')}

        self.parent = parent  # Setting the parent(Window) to be referenced
        title_font = tkfont.Font(family='Helvetica', size=25, weight="bold")
        self.layout_option = tk.IntVar(self, 0)
        self.player_color = tk.IntVar(self, 0)
        self.mode_def_val = tk.IntVar(self, value=1)

        self.title_lbl = tk.Label(self, text="Welcome to Abalone AI", font=(None, 40, "bold"), bg='teal',
                                  fg=bgcolor).grid(row=0, column=0, columnspan=5, pady=(15, 15))
        self.title_lbl = tk.Label(self, text="Please set the match settings, then press start game", font=title_font,
                                  bg='teal', fg=bgcolor).grid(row=1, column=0, columnspan=5, pady=(0, 35))

        self.game_mode_lbl = tk.Label(self, text="Game Mode ", **options1).grid(row=2, column=0, sticky="W", **paddings)
        self.game_mode_btn = tk.Radiobutton(self, text="Human vs Computer", variable=self.mode_def_val, value=1,
                                            **options1).grid(row=2, column=1, sticky="W", **paddings)

        self.player_color_lbl = tk.Label(self, text="Human Piece Color ", **options1).grid(row=3, column=0, sticky="W",
                                                                                           **paddings)
        self.black_rb = tk.Radiobutton(self, text="Black", value=0, variable=self.player_color,
                                       **options1).grid(row=3, column=1, sticky="W", **paddings)
        self.white_rb = tk.Radiobutton(self, text="White", value=1, variable=self.player_color,
                                       **options1).grid(row=3, column=2, sticky="W", **paddings)

        def is_a_number(char):
            """
            Used to check whether input character into Entry is a digit
            """
            return char.isdigit()

        validation = self.register(is_a_number)
        self.move_lbl = tk.Label(self, text="Move limit ", **options1).grid(row=4, column=0, sticky="W", **paddings)
        self.move_entry = tk.Entry(self, validate="key", validatecommand=(validation, '%S'), **options1)
        self.move_entry.grid(row=4, column=1, sticky="W", padx=5)

        self.time_limit_lbl = tk.Label(self, text="Time limit per move(s) ", **options1).grid(row=5, column=0,
                                                                                              sticky="W", **paddings)
        self.human_lbl = tk.Label(self, text="Human", **options1).grid(row=5, column=1, sticky="W", **paddings)
        self.human_entry = tk.Entry(self, validate="key", validatecommand=(validation, '%S'), **options1)
        self.human_entry.grid(row=5, column=2, sticky="W", padx=5)

        self.pc_lbl = tk.Label(self, text="Computer", **options1).grid(row=6, column=1, sticky="W", **paddings)
        self.pc_entry = tk.Entry(self, validate="key", validatecommand=(validation, '%S'), **options1)
        self.pc_entry.grid(row=6, column=2, sticky="W", padx=5)

        self.layout_lbl = tk.Label(self, text="Layout ", **options1).grid(row=7, column=0, sticky="W", **paddings)
        self.standard_rb = tk.Radiobutton(self, text="Standard", value=0, variable=self.layout_option,
                                          **options1).grid(row=7, column=1, sticky="W", **paddings)
        self.belgian_rb = tk.Radiobutton(self, text="Belgian Daisy", value=1, variable=self.layout_option,
                                         **options1).grid(row=7, column=2, sticky="W", **paddings)
        self.german_rb = tk.Radiobutton(self, text="German Daisy", value=2, variable=self.layout_option,
                                        **options1).grid(row=7, column=3, sticky="W", **paddings)

        def start_game_click(frame, window):
            """
            On button click event handler for start game clicked, gathers settings info and calls window's start_game_ui
            :param frame: Frame to get data from (i.e. settings)
            :param window: Parent (Window) that will be sent data/called upon
            """
            window.game_settings = SettingsPage.convert_game_choices(frame.player_color.get(), frame.move_entry.get(),
                                                                     frame.human_entry.get(), frame.pc_entry.get(),
                                                                     frame.layout_option.get())
            window.start_game_ui()

        self.start_btn = tk.Button(self, text="Start Game", command=lambda: start_game_click(self, self.parent),
                                   bg=bgcolor, fg='teal', font=(None, 25, 'bold')).grid(row=8, column=1, sticky='E'
                                                                                        , pady=40)

    @staticmethod
    def convert_game_choices(piece_type, move_limit, human_time, pc_time, layout_choice):
        """
        Converts the settings' page game choices into the corresponding working values
        :return: a dict, of the game settings and their values
        """
        move = int(move_limit)
        color = PieceType.BLACK
        human = int(human_time)
        pc = int(pc_time)
        layout = InitialBoardState.DEFAULT

        if piece_type == 1:
            color = PieceType.WHITE
        else:
            color = PieceType.BLACK

        if layout_choice == 1:
            layout = InitialBoardState.BELGIAN
        elif layout_choice == 2:
            layout = InitialBoardState.GERMAN
        else:
            layout = InitialBoardState.DEFAULT

        settings = {"mode": GameMode.HumanVsPC, "player_color": color, "move_limit": move, "human_time": human,
                    "pc_time": pc, "layout": layout}

        return settings


class BoardOperation(tk.Frame):
    """
    GUI for board operations
    """
    # a Board object
    board = None
    # a list of marble index that are selected
    selected_list = []

    def __init__(self, parent):
        super().__init__(bg=bgcolor)
        options1 = {'font': (None, 20, 'bold'), 'fg': 'blue', 'background': 'lightblue', 'width': 12}
        paddings = {'padx': 10, 'ipadx': 5, "ipady": 5}
        self.parent = parent
        self.game = self.parent.get_game()

        self.canvas = tk.Canvas(self, bg='darkseagreen3', width=560, height=550)
        self.canvas.grid(row=0, column=0, rowspan=20, pady=10)
        self.draw_board()
        self.canvas.bind("<Button-1>", self.update_selection)
        self.draw_board()
        self.UL_btn = tk.Button(self, text="Up-left", command=lambda: self.move(MoveDirection.UL),
                                **options1).grid(row=17, column=1, **paddings)
        self.UR_btn = tk.Button(self, text="Up-right", command=lambda: self.move(MoveDirection.UR),
                                **options1).grid(row=17, column=2, **paddings)
        self.L_btn = tk.Button(self, text="Left", command=lambda: self.move(MoveDirection.L),
                               **options1).grid(row=18, column=1, **paddings)
        self.R_btn = tk.Button(self, text="Right", command=lambda: self.move(MoveDirection.R),
                               **options1).grid(row=18, column=2, **paddings)
        self.DL_btn = tk.Button(self, text="Down-left", command=lambda: self.move(MoveDirection.DL),
                                **options1).grid(row=19, column=1, **paddings)
        self.DR_btn = tk.Button(self, text="Down-right", command=lambda: self.move(MoveDirection.DR),
                                **options1).grid(row=19, column=2, **paddings)

    def update_selection(self, pos):
        """
        if the selected marble is not opponent's marble or empty, draw a red circle around it
        if click a selected marble, all selected marbles will be deselected
        :param pos: pos.x, pos.y are coordinates of a mouse click relative to the Canvas.
        :return: None
        """
        x, y = -1, -1
        x_pos = pos.x
        y_pos = pos.y
        # print(x_pos, y_pos)

        # x is index of row, y is index of column
        x = (y_pos - 50) // 50
        # y0 is the y-coord and x0 is the x-coord if we select a marble and draw a circle around it
        y0 = (x + 1) * 50
        x0 = -1
        if x == 4:
            y = (x_pos - 35) // 54
            x0 = y * 55 + 35
        elif x == 0 or x == 8:
            y = (x_pos - 145) // 54
            x0 = y * 55 + 145
        elif x == 1 or x == 7:
            y = (x_pos - 115) // 54
            x0 = y * 55 + 115
        elif x == 2 or x == 6:
            y = (x_pos - 90) // 54
            x0 = y * 55 + 90
        elif x == 3 or x == 5:
            y = (x_pos - 60) // 54
            x0 = y * 55 + 60
        selected_marble = [x, y]

        if x > -1 and y > -1:
            if selected_marble in BoardOperation.selected_list:
                BoardOperation.selected_list.clear()
                self.canvas.delete("selected")
                print(BoardOperation.selected_list)
            elif self.same_team_selection(selected_marble) and len(BoardOperation.selected_list) < 3:
                self.canvas.create_oval(x0, y0, x0 + 50, y0 + 50, outline="red", width=3, tags="selected")
                BoardOperation.selected_list.append(selected_marble)
                print(BoardOperation.selected_list)

    def same_team_selection(self, marble):
        """
        Checks if the marble is part of the same team
        :param marble:
        :return: a bool
        """
        if self.game.board.get_tile_value(marble) is not None \
                and self.game.board.get_tile_value(marble) == self.game.current_turn_color.value:
            return True
        return False

    def draw_board(self):
        """
        Draw board according to Board layout
        """
        print("draw_board is called")
        layout = self.game.board.get_tiles_values()
        self.canvas.delete('all')
        d = 50
        padding = 5
        x0 = 170
        i = 0
        total = 8
        for row in layout:
            letter = chr(65 + total)
            if i < 5:
                x0 = x0 - 0.5 * d - 0.5 * padding
                start = 5 - i
            else:
                x0 = x0 + 0.5 * d + 0.5 * padding
                start = 1
            y0 = i * d
            i += 1
            j = 0
            total -= 1
            digit = start
            for piece in row:
                x = x0 + j * d + j * padding
                y = y0 + d

                if piece:
                    color = 'white'
                elif piece is not None:
                    color = 'black'
                else:
                    color = 'grey70'

                self.canvas.create_oval(x, y, x + d, y + d, fill=color)
                position = letter + str(digit)
                tk.Label(self.canvas, text=position, font=(None, 10, 'bold'), fg="red", bg=color) \
                    .place(x=x + 8, y=y + 8)
                j += 1
                digit += 1

    def move(self, direction):
        """
        Handles user piece movement
        :param direction: MoveDirection
        """
        self.canvas.delete("selected")

        if not self.valid_selection_list():
            BoardOperation.selected_list = []
            print("**** invalid selection ****")
            return False

        selected_marbles = []
        new_marbles = []
        for marble in BoardOperation.selected_list:
            new_marble = list(Board.add_direction(marble, direction))
            new_marble = Board.index_to_position(new_marble)
            new_marbles.append(new_marble)

            marble = Board.index_to_position(marble)
            selected_marbles.append(marble)

        try:
            # board.move_piece(direction, selected_marbles)
            self.game.make_move(direction, selected_marbles)
            # print(board)
        except CannotMoveException as e:
            print(e)
            print("invalid move")
        except IndexError as e:
            print(e)
        else:
            self.parent.check_for_game_won(self.game.current_turn_color)
            self.draw_board()

            player_human = self.game.get_human_player()
            player_comp = self.game.get_comp_player()
            move_type = direction.name
            from_pos = marble_tuple_to_string(selected_marbles)
            to_pos = marble_tuple_to_string(new_marbles)
            color_human = player_human.piece_type
            color_comp = player_comp.piece_type
            time_taken = self.update_suggested_move()
            sumito = False

            # if it is human's turn
            if self.game.current_turn_color == self.game.human_piece_type:
                # update score, moves left and history
                player_human.record_move_to_history(from_pos, to_pos, move_type, time_taken, sumito, color_human)
                self.parent.output.update_human_output()
            # if it is computer's turn
            else:
                player_comp.record_move_to_history(from_pos, to_pos, move_type, time_taken, sumito, color_comp)
                self.parent.output.update_comp_output()

            # update current_turn to another player
            self.game.next_turn()
            self.parent.current_turn_info.update_current_turn()
            # Only run if human is black (as suggested move not showing on first turn bug only happens then)
            self.update_suggested_move()

        BoardOperation.selected_list = []

    def suggest_first_random_move(self):
        """
        Suggests first random legal move to make if comp is black
        :return: float
        """
        if self.game.human_piece_type != PieceType.BLACK:  # COMP is first move
            start_time = datetime.datetime.now()
            board = self.game.board
            self.parent.best_move.statespacegenerator.read_board(board, self.game.current_turn_color)
            moves = self.parent.best_move.statespacegenerator.generate_three_piece_moves()
            rand_index = random.randint(0, (len(moves) - 1))
            move = moves[rand_index]
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
            elapsed_seconds = elapsed_time.total_seconds()
            print(f"elapsed time in seconds {elapsed_seconds}")
            self.parent.best_move.best_move_to_string(move)
            return elapsed_seconds

    def update_suggested_move(self):
        """
        Suggests move for the computer to make, and returns the amount of time it took
        :return: float
        """
        if self.game.current_turn_color != self.game.human_piece_type:
            board = self.game.board
            self.parent.best_move.statespacegenerator.read_board(board, self.game.current_turn_color)
            # it returns a tuple: (('C', 3), ('B', 2), ('A', 1), <MoveDirection.UP_RIGHT: (1, 1)>)
            time_given = self.game.get_comp_player().move_time_limit
            start_time = datetime.datetime.now()
            best_move_tuple = self.parent.best_move.statespacegenerator.find_best_move(1, time_given)
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
            elapsed_seconds = elapsed_time.total_seconds()
            print(f"elapsed time in seconds {elapsed_seconds}")
            # convert tuple to "C3B2A1 UP_RIGHT" and display it in gui
            self.parent.best_move.best_move_to_string(best_move_tuple)
            return elapsed_seconds

    def valid_selection_list(self):
        """
        Validate selected list. Return false if the selection is invalid (adjacent in column)
        :return: boolean
        """
        test_list = BoardOperation.selected_list
        if len(test_list) == 1:
            return True
        if len(test_list) == 3 and \
                self.game.board.is_valid_column(test_list):
            return True
        if len(test_list) == 2:
            marble1 = Board.index_to_position(test_list[0])
            marble2 = Board.index_to_position(test_list[1])
            if marble1[0] == marble2[0] and marble1[1] - marble2[1] in [-1, 1]:
                return True
            elif marble1[1] == marble2[1] and ord(marble1[0]) - ord(marble2[0]) in [-1, 1]:
                return True
            elif ord(marble1[0]) - ord(marble2[0]) == 1 and marble1[1] - marble2[1] == 1:
                return True
            elif ord(marble1[0]) - ord(marble2[0]) == -1 and marble1[1] - marble2[1] == -1:
                return True
        return False


class Operation(tk.Frame):
    """
    GUI for game operation buttons
    """

    def __init__(self, parent):
        super().__init__(bg=bgcolor)
        self.parent = parent
        self.game = parent.get_game()
        options1 = {'font': (None, 20, 'bold'), 'fg': 'blue', 'bg': 'lightblue', 'width': 5}
        paddings = {'padx': 10, 'pady': 5, 'ipadx': 5, "ipady": 5}
        self.start_btn = tk.Button(self, text="Start", command=self.start_game,
                                   **options1).grid(row=0, column=0, **paddings, sticky="W")
        self.stop_btn = tk.Button(self, text="Stop", command=self.stop_game,
                                  **options1).grid(row=0, column=1, **paddings, sticky="W")
        self.pause_btn = tk.Button(self, text="Pause", command=self.pause_game,
                                   **options1).grid(row=0, column=2, **paddings, sticky="W")
        self.reset_btn = tk.Button(self, text="Reset", command=self.reset_game,
                                   **options1).grid(row=0, column=4, **paddings, sticky="W")
        self.undo_btn = tk.Button(self, text="Undo", command=self.undo,
                                  **options1).grid(row=0, column=3, **paddings, sticky="W")

    def start_game(self):
        """
        Starts the game/timer
        """
        self.parent.countdown_timer.start_countdown()

    def stop_game(self):
        """
        Stops the game
        """
        self.parent.countdown_timer.pause_countdown()
        self.parent.game_over_screen.show_draw_stats()
        # Other logic to add?

    def pause_game(self):
        """
        Pauses the game
        """
        self.parent.countdown_timer.pause_countdown()
        # Other logic to add?

    def reset_game(self):
        """
        Resets the game
        """
        destroy_widget(self.parent.countdown_timer)
        destroy_widget(self.parent.best_move)
        destroy_widget(self.parent.current_turn_info)
        destroy_widget(self.parent.board_operation)
        destroy_widget(self.parent.output)
        destroy_widget(self.parent.operation)
        destroy_widget(self.parent.game_over_screen)
        self.parent.start_game_ui()  # Board doesn't get reset properly, seems to be a problem with the tiles values,
        # where even the enum InitialLayout's i.e. .DEFAULT.values (where pieces are, T/F) still the same before reset

    def undo(self):
        """
        Undos a move
        """
        self.game.next_turn()  # Switch to previous(next) turn
        self.parent.current_turn_info.update_current_turn()
        try:
            if self.game.current_turn_color == PieceType.BLACK:
                self.game.black_player.remove_recent_move()  # Remove the player's most recent move history
            else:
                self.game.white_player.remove_recent_move()
        except IndexError:
            print("Could not undo move, no previous move to remove")
            self.game.next_turn()  # Revert next turn update
            self.parent.current_turn_info.update_current_turn()
        else:
            self.game.undo_move()
            # The BoardOperation class doesnt seem to be tied to the Game classes board, needs to be manually updated
            self.game.board.update_marble_counts()  # Updating game/board outputs
            self.parent.output.update_human_output()
            self.parent.output.update_comp_output()
            self.parent.board_operation.draw_board()


class CurrentTurnInfo(tk.Frame):
    """
    GUI for current turn information
    """

    def __init__(self, parent):
        super().__init__(bg=bgcolor)
        self.parent = parent
        options1 = {'bg': bgcolor}
        self.turn_text = tk.StringVar()
        self.game = self.parent.get_game()
        self.update_current_turn()

        self.current_turn_lbl = tk.Label(self, text="Current turn: ", font=(None, 20, 'bold'), **options1)
        self.current_turn_lbl.grid(row=0, column=0, sticky="W")
        self.current_turn_val = tk.Label(self, textvariable=self.turn_text, font=(None, 20, 'bold'), fg="blue",
                                         **options1)
        self.current_turn_val.grid(row=0, column=1, sticky="W")

    def update_current_turn(self):
        """
        Updates current turn text based on current turn's piece color
        :return:
        """
        if self.game.current_turn_color is self.game.human_piece_type:
            self.parent.best_move.hide_best_move_val()
        else:
            self.parent.best_move.show_best_move_val()

        if self.game.current_turn_color is PieceType.BLACK:
            self.turn_text.set("Black")
        else:
            self.turn_text.set("White")


class Output(tk.Frame):
    """
    GUI for outputs human and computer game information
    """

    def __init__(self, parent):
        super().__init__(bg=bgcolor)
        self.parent = parent
        self.game = parent.get_game()
        self.move_history_amount_limit = 10
        styles = {'fg': 'green'}

        human_lbl_text = "Human(White)"
        comp_lbl_text = "Computer(Black)"
        if self.game.is_human_piece_black():  # If human is black piece type, change piece colors label accordingly
            human_lbl_text = "Human(Black)"
            comp_lbl_text = "Computer(White)"

        self.human_player_lbl = tk.Label(self, text=human_lbl_text, bg=bgcolor, font=(None, 20, 'bold'), fg="darkblue") \
            .grid(row=0, column=0, sticky="W")
        self.comp_player_lbl = tk.Label(self, text=comp_lbl_text, bg=bgcolor, font=(None, 20, 'bold'), fg="darkblue") \
            .grid(row=0, column=1, sticky="W")

        self.score_val1 = tk.Label(self, text="Score", **options).grid(row=1, column=0, sticky="W")
        self.score_val2 = tk.Label(self, text="Score", **options).grid(row=1, column=1, sticky="W")

        self.human_score_val = tk.IntVar(0)
        self.comp_score_val = tk.IntVar(0)
        self.human_score = tk.Label(self, textvariable=self.human_score_val, font=(None, 25, 'bold'), fg="purple",
                                    bg=bgcolor)
        self.human_score.grid(row=2, column=0, sticky="W")
        self.comp_score = tk.Label(self, textvariable=self.comp_score_val, font=(None, 25, 'bold'), fg="purple",
                                   bg=bgcolor)
        self.comp_score.grid(row=2, column=1, sticky="W")

        self.move_left_lbl1 = tk.Label(self, text="Moves left", **options).grid(row=3, column=0, sticky="W")
        self.move_left_lbl2 = tk.Label(self, text="Moves left", **options).grid(row=3, column=1, sticky="W")

        moves = self.game.get_move_limit()
        self.human_moves_val = tk.IntVar(self, value=moves)
        self.comp_moves_val = tk.IntVar(self, value=moves)
        self.human_moves = tk.Label(self, textvariable=self.human_moves_val, **options, **styles)
        self.human_moves.grid(row=4, column=0, sticky="W")
        self.comp_moves = tk.Label(self, textvariable=self.comp_moves_val, **options, **styles)
        self.comp_moves.grid(row=4, column=1, sticky="W")

        self.history_lbl1 = tk.Label(self, text="---------- History ----------", **options).grid(row=10, column=0,
                                                                                                 sticky="W")
        self.history_lbl2 = tk.Label(self, text="---------- History ----------", **options).grid(row=10, column=1,
                                                                                                 sticky="W")
        self.human_hist_text = tk.StringVar()
        self.human_hist_text.set("")

        self.comp_hist_text = tk.StringVar()
        self.comp_hist_text.set("")

        self.human_history = tk.Label(self, textvariable=self.human_hist_text, **options, **styles)
        self.human_history.grid(row=11, column=0, sticky="W")  # Need to do .grid after so assignment works
        self.computer_history = tk.Label(self, textvariable=self.comp_hist_text, **options, **styles)
        self.computer_history.grid(row=11, column=1, sticky="W")

    def update_human_output(self):
        """
        Call this after human's turn to update their output info
        """
        self.update_human_score()
        self.update_human_moves_left()
        self.update_human_history()

    def update_comp_output(self):
        """
        Call this after computer's turn to update their output info
        """
        self.update_comp_score()
        self.update_comp_moves_left()
        self.update_comp_history()

    def update_human_moves_left(self):
        """
        Updates human moves left
        """
        player = self.game.get_human_player()
        self.human_moves_val.set(player.get_moves_left())

    def update_comp_moves_left(self):
        """
        Updates comp moves left
        """
        player = self.game.get_comp_player()
        self.comp_moves_val.set(player.get_moves_left())

    def update_human_score(self):
        """
        Assigns game score, and then updates values of human
        """
        if self.game.is_human_piece_black():
            self.game.assign_black_score()
            self.human_score_val.set(self.game.black_player.game_score)
        else:
            self.game.assign_white_score()
            self.human_score_val.set(self.game.white_player.game_score)

    def update_comp_score(self):
        """
        Assigns game score, and then updates values of computer
        """
        if self.game.is_human_piece_black():
            self.game.assign_white_score()
            self.comp_score_val.set(self.game.white_player.game_score)
        else:
            self.game.assign_black_score()
            self.comp_score_val.set(self.game.black_player.game_score)

    def update_human_history(self):
        """
        Updates human history
        """
        player = self.game.get_human_player()
        moves = player.get_last_x_history_moves(self.move_history_amount_limit)
        info = game.convert_moves_to_gui_format(moves)
        self.human_hist_text.set(info)

    def update_comp_history(self):
        """
        Updates comp history text
        """
        player = self.game.get_comp_player()
        moves = player.get_last_x_history_moves(self.move_history_amount_limit)
        info = game.convert_moves_to_gui_format(moves)
        self.comp_hist_text.set(info)
