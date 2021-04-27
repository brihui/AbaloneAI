import copy
from utilities import Clock, MoveInfo
from utilities import gen_move_numbers
from utilities import MoveHistory
from enums import GameMode, MoveDirection
from enums import PlayerType
from enums import PieceType
from enums import InitialBoardState
from board import Board
import gui


class Game:
    def __init__(self):
        """
        Represents a game object.
        :param layout: enum, initial board game layout
        :param mode: enum, game mode
        """
        self._layout_type = None
        self._mode = None
        self._move_num_gen = gen_move_numbers()
        self._current_turn_color = PieceType.BLACK
        self._board = None
        self._previous_board = None  # Board for the previous move
        self._black_player = None  # Goes first
        self._white_player = None
        self._human_piece_type = None  # flag to be used by GUI
        self._starting_amount_pieces = 14   # Hardcoded since won't change

    @property
    def board(self):
        return self._board

    @property
    def current_turn_color(self):
        return self._current_turn_color

    @property
    def black_player(self):
        return self._black_player

    @property
    def white_player(self):
        return self._white_player

    @property
    def human_piece_type(self):
        return self._human_piece_type

    def has_piece_type_won(self, piece_type):
        self._board.update_marble_counts()
        winner = self._board.has_won()
        if winner is piece_type:
            return True
        else:
            return False

    def is_human_piece_black(self):
        """
        Returns if human piece is black
        :return:
        """
        return self._human_piece_type is PieceType.BLACK

    def get_human_player(self):
        """
        Gets human player
        :return: a Player
        """
        if self.is_human_piece_black():
            return self._black_player
        else:
            return self._white_player

    def get_comp_player(self):
        """
        Gets computer player
        :return: a Player
        """
        if self.is_human_piece_black():
            return self._white_player
        else:
            return self._black_player

    def set_game_parameters(self, **kwargs):
        """
        Sets game parameters
        :param kwargs:
        """
        self._layout_type = kwargs["layout"]
        self._mode = kwargs["mode"]
        self.set_up_players(kwargs["move_limit"], kwargs["human_time"], kwargs["pc_time"], kwargs["player_color"])

    def set_up_players(self, move_limit, human_time_limit, pc_time_limit, player_color):
        """
        Sets up game players
        """
        if self._mode == GameMode.HumanVsPC:  # Not necessary as this only mode, but for future maybe
            if player_color is PieceType.BLACK:  # Human selects player color
                self._human_piece_type = PieceType.BLACK
                self._black_player = Player(PlayerType.HUMAN, PieceType.BLACK, move_limit, human_time_limit)
                self._white_player = Player(PlayerType.PC, PieceType.WHITE, move_limit, pc_time_limit)
            else:
                self._human_piece_type = PieceType.WHITE
                self._black_player = Player(PlayerType.PC, PieceType.BLACK, move_limit, pc_time_limit)
                self._white_player = Player(PlayerType.HUMAN, PieceType.WHITE, move_limit, human_time_limit)

    def assign_white_score(self):
        """
        Assigns white player's game score
        """
        self.white_player.game_score = self._starting_amount_pieces - self._board.get_black_marbles()

    def assign_black_score(self):
        """
        Assigns black player's game score
        """
        self.black_player.game_score = self._starting_amount_pieces - self._board.get_white_marbles()

    def get_black_move_history(self):
        """
        Geter for black move history
        :return: move history
        """
        return self._black_player.move_history

    def get_white_move_history(self):
        """
        Geter for white move history
        :return: move history
        """
        return self._white_player.move_history

    def start_game(self):
        """
        Starts game.
        :precondition: set_game_parameters is called beforehand
        """
        self._board = Board(self._layout_type)

    def get_move_limit(self):
        """
        Gets game move limit from player
        :return:
        """
        return self._black_player.game_move_limit  # Since each player has same value doesn't matter which you take

    def has_a_player_exceed_move_limit(self):
        """
        Returns a player if they have exceeded their move limit, else None
        :return:
        """
        if self._black_player.is_exceeding_move_limit():
            return PieceType.BLACK
        elif self._white_player.is_exceeding_move_limit():
            return PieceType.WHITE
        else:
            return None

    def next_turn(self):
        """
        Takes next game turn, records moves and sets new move number.
        """
        if self._current_turn_color is PieceType.BLACK:
            self._black_player.make_move()
        else:
            self.white_player.make_move()
        self.switch_current_turn_player()

    def switch_current_turn_player(self):
        if self._current_turn_color is PieceType.BLACK:
            self._current_turn_color = PieceType.WHITE
        else:
            self._current_turn_color = PieceType.BLACK

    def get_layout_type(self):
        """
        Getter for layout type
        :return: layout
        """
        return self._layout_type

    def add_human_test_moves(self):
        """
        Just using this to test in GUI functionality
        """
        player = self.get_human_player()
        player.record_move_to_history("A1,A2,A3", "A2,A3,A4", MoveDirection.RIGHT, 2, False, player.piece_type)
        player.record_move_to_history("A1,A2,A3", "B2,B3,B4", MoveDirection.UP_RIGHT, 2, False, player.piece_type)
        player.record_move_to_history("A1,A2,A3", "B2,B3,B4", MoveDirection.UP_RIGHT, 4, False, player.piece_type)
        player.record_move_to_history("A1,A2", "B2,B3", MoveDirection.UP_RIGHT, 2, True, player.piece_type)
        player.record_move_to_history("A1", "B2", MoveDirection.UP_RIGHT, 5, True, player.piece_type)
        player.record_move_to_history("A1", "B2", MoveDirection.UP_RIGHT, 5, True, player.piece_type)
        player.record_move_to_history("A1", "B2", MoveDirection.UP_RIGHT, 5, True, player.piece_type)
        player.record_move_to_history("A1,A2,A3", "B2,B3,B4", MoveDirection.DOWN_LEFT, 6, False, player.piece_type)

    def stop_game(self):
        pass

    def pause_game(self):
        pass

    def reset_game(self):
        self._board = Board(self._layout_type.value)

    def make_move(self, direction, selected_marbles):
        tmp = Board(board=self._board)
        self._board.move_piece(direction, selected_marbles)
        self._previous_board = tmp

    def undo_move(self):
        self._board = Board(board=self._previous_board)
        # gui.BoardOperation.board = self._board

    def finish_game(self):
        """
        Finishes game
        """
        pass


def convert_moves_to_gui_format(moves):
    """
    Converts move info objects to a formatted string for gui's history
    :param moves: list of MoveInfo
    """
    formatted_moves = []
    for m in moves:
        formatted_moves.append(m.get_as_history_format())
    return '\n'.join(formatted_moves)


class Player:
    """
    Represents a player.
    """
    def __init__(self, player_type, piece_type, move_limit, time_limit):
        self._player_type = player_type
        self._piece_type = piece_type
        self._game_move_limit = move_limit
        self._move_time_limit = time_limit
        self._move_history = MoveHistory()
        self._move_num_gen = gen_move_numbers(1, (move_limit + 1))
        self._original_num_marbles = 14  # Default 14 marbles per player
        self._next_move = None
        self.last_move = None
        self._game_score = 0  # how many pieces pushed off per player

    def get_cumulative_move_time(self):
        """
        Returns the cumulative time of all moves
        :return:
        """
        time = 0.0
        for move in self._move_history.history:
            time += move.time
        return time

    def record_move_to_history(self, from_pos, to_pos, move_type, time_taken, sumito=False, color=PieceType.BLACK):
        """
        Records move to history, by taking params and adding to history
        :param from_pos:
        :param to_pos:
        :param move_type:
        :param time_taken:
        :param sumito:
        :param color:
        :return:
        """
        self.add_to_history(MoveInfo(from_pos, to_pos, move_type, time_taken, sumito, color))

    def add_to_history(self, move):
        """
        Adds move to move history
        :param move:
        """
        self._move_history.add_move(move)

    def remove_recent_move(self):
        """
        Removes recent move from move history
        :return: MoveInfo
        """
        return self._move_history.remove_last_move()

    def get_last_x_history_moves(self, last_x):
        """
        Gets the last x amount of moves from move history
        :param last_x: an int, amount to remove
        :return: list of MoveInfo
        """
        return self._move_history.get_last_x_moves(last_x)

    def is_exceeding_move_limit(self):
        """
        Returns if player has exceeded game move limit
        :return: bool
        """
        return self.game_move_limit < self._get_amount_moves_taken()

    def get_moves_left(self):
        """
        Returns the amount of moves left
        :return: an int
        """
        return self._game_move_limit - self._get_amount_moves_taken()

    def _get_amount_moves_taken(self):
        """
        Returns amount of moves taken
        :return: an int
        """
        return self._move_history.get_amount_of_moves()


    @property
    def move_history(self):
        return self._move_history

    @property
    def player_type(self):
        return self._player_type

    @property
    def piece_type(self):
        return self._piece_type

    @property
    def move_time_limit(self):
        return self._move_time_limit

    @property
    def game_move_limit(self):
        return self._game_move_limit

    @property
    def game_score(self):
        return self._game_score

    @game_score.setter
    def game_score(self, score):
        self._game_score = score

    @property
    def next_move(self):
        return self._next_move

    @property
    def last_move(self):
        return self._last_move

    @last_move.setter
    def last_move(self, move):
        self._last_move = move

    def calculate_game_score(self, enemy_marbles):
        """
        Calculates game score of current player
        :param enemy_marbles: amount of enemy marbles
        """
        self._game_score = self._original_num_marbles - enemy_marbles
