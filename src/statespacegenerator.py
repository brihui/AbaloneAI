from enum import Enum

from board import Board
from enums import MoveDirection, HeuristicWeight
from enums import PieceType
import time


class StateSpaceGenerator:
    """
    A class that generates all possible legal next moves and the resulting game
    board configuration of each move.
    """

    MIN = -3000
    MAX = 3000

    starting_marbles = 14

    TRANSPOSITION_TABLE = {}

    def __init__(self):
        # Board configuration read in
        self._board_configuration = None
        # List of pieces for both players
        self._pieces = []
        # Player acting's colour
        self._player_type = None
        # List of pieces for the player acting
        self._ally_pieces = []
        # List of pieces for the other player not acting
        self._enemy_pieces = []
        # Number of sumit moves
        self._num_sumito = 0

    @property
    def pieces(self):
        """
        Property to get all pieces on the board
        :return: a List of pieces on the board represented by Tuples
        """
        return self._pieces

    @property
    def player(self):
        """
        Property to get which player is acting
        :return: a PieceType enum
        """
        return self._player_type

    @player.setter
    def player(self, team):
        """
        Property to set which player is acting
        :param team: a PieceType enum
        """
        self._player_type = team

    def read_board(self, board, team):
        """
        Takes in a Board object and instantiates all instance variables.
        :param board: a Board object representing the current board state.
        :param team: a PieceType enum representing the team to move
        """

        self._player_type = team
        tile_values = board.get_tiles_values()

        self._pieces.clear()
        self._ally_pieces.clear()
        self._enemy_pieces.clear()

        for x in range(len(tile_values)):
            for y in range(len(tile_values[x])):
                if tile_values[x][y]:
                    self._pieces.append((x, y, PieceType.WHITE))
                    if self._player_type is PieceType.BLACK:
                        self._enemy_pieces.append((x, y, PieceType.WHITE))
                    else:
                        self._ally_pieces.append((x, y, PieceType.WHITE))
                elif tile_values[x][y] is False:
                    self._pieces.append((x, y, PieceType.BLACK))
                    if self._player_type is PieceType.BLACK:
                        self._ally_pieces.append((x, y, PieceType.BLACK))
                    else:
                        self._enemy_pieces.append((x, y, PieceType.BLACK))

    def read_input_file(self, file_name):
        """
        Reads a file for two lines of information, first line saying which player
        has the next move and second line containing the current board configuration.
        Once retrieved they are stored into the instance variables.
        :param file_name a String containing the name of the file to be read
        :precondition: file_name must be in the root directory
        """
        with open(file_name, mode='r', encoding='utf-8') as input_file:
            # Read the whole file as 2 lines
            whole_file = input_file.read().splitlines()

            # Set the player colour to the corresponding Enum
            if whole_file[0] == 'b':
                self._player_type = PieceType.BLACK
            else:
                self._player_type = PieceType.WHITE

            self._board_configuration = whole_file[1]
            # Uses a generator method to generate all pieces as array
            # indexes corresponding to our State Representation
            piece_generator = self._piece_generator()
            self._pieces = [piece for piece in piece_generator]
            # Separate lists for ally and enemy pieces for ease of search
            self._ally_pieces = [piece for piece in self._pieces if piece[2] == self._player_type]
            self._enemy_pieces = [piece for piece in self._pieces if piece[2] != self._player_type]

    def _piece_generator(self):
        """
        A generator method which uses the board configuration and converts it
        into a 2D array index corresponding to our State Representation.
        :return: a Tuple with the x, y Array index and player color
        """
        # Create a list of pieces from board configuration by splicing
        board_string_list = self._board_configuration.split(",")
        for piece_string in board_string_list:
            # Generate array index using function from Board class
            index = Board.position_to_index((piece_string[0], int(piece_string[1])))
            x = index[0]
            y = index[1]
            if piece_string[2] == 'b':
                player = PieceType.BLACK
            else:
                player = PieceType.WHITE
            yield x, y, player

    def find_triple_pieces(self):
        """
        Finds all ally pieces which can be grouped as a 'three'.
        :return: a List containing all groups of 'two' as tuples.
        """
        # List to store triple pieces
        triples = []
        # Loop through all 'ally' pieces
        for piece in self._ally_pieces:
            # Loop through all moves for each piece
            for move in MoveDirection:
                # Create an ally piece (if it exists, returns None if not)
                adjacent_piece = self._is_ally(piece, move)
                if adjacent_piece is not None:
                    # Repeat the check for the next in-line piece
                    next_adjacent_piece = self._is_ally(adjacent_piece, move)
                    if next_adjacent_piece is not None:
                        # Check if the move has been added already in another order of pieces
                        existing = False
                        for trips in triples:
                            if piece in trips and tuple(adjacent_piece) in trips and tuple(next_adjacent_piece) in trips:
                                existing = True
                                break
                        # Add to list of triplets if none already exists
                        if not existing:
                            triples.append((piece, tuple(adjacent_piece), tuple(next_adjacent_piece)))
        return triples

    def find_triple_pieces_enemy(self):
        """
        Finds all ally pieces which can be grouped as a 'three'.
        :return: a List containing all groups of 'two' as tuples.
        """
        # List to store triple pieces
        triples = []
        # Loop through all 'ally' pieces
        for piece in self._enemy_pieces:
            # Loop through all moves for each piece
            for move in MoveDirection:
                # Create an ally piece (if it exists, returns None if not)
                adjacent_piece = self._is_enemy(piece, move)
                if adjacent_piece is not None:
                    # Repeat the check for the next in-line piece
                    next_adjacent_piece = self._is_enemy(adjacent_piece, move)
                    if next_adjacent_piece is not None:
                        # Check if the move has been added already in another order of pieces
                        existing = False
                        for trips in triples:
                            if piece in trips and tuple(adjacent_piece) in trips and tuple(next_adjacent_piece) in trips:
                                existing = True
                                break
                        # Add to list of triplets if none already exists
                        if not existing:
                            triples.append((piece, tuple(adjacent_piece), tuple(next_adjacent_piece)))
        return triples

    def find_three_piece_moves(self, groups):
        """
        Finds all legal moves for groups of three pieces.
        :param groups: a List of Tuples containing all valid groups of three pieces for the player.
        :return: a List of Tuples containing all legal moves
        """
        # List to store the legal moves
        legal_moves = []
        # Loop through all groups of three
        for trips in groups:
            # Loop through all moves for each group
            for move in MoveDirection:
                # Create local reference of each piece for readability (and speed)
                piece_one = trips[0]
                piece_two = trips[1]
                piece_three = trips[2]
                # Check if move is in-line by calling function from Board class
                if Board.is_inline(piece_one, piece_two, move):
                    # Checks for an empty space or a valid sumito move in the direction of movement
                    sumito = self._is_sumito(trips, move)
                    empty = self._is_empty(trips, move)
                    if empty or sumito:
                        existing = False
                        # Create the board position for each piece (e.g A1)
                        board_position_one = Board.index_to_position(piece_one)
                        board_position_two = Board.index_to_position(piece_two)
                        board_position_three = Board.index_to_position(piece_three)
                        # Check if the move has already been added in different order of pieces
                        for legal_move in legal_moves:
                            if board_position_one in legal_move and board_position_two in legal_move and board_position_three in legal_move and move in legal_move:
                                existing = True
                                break
                        # Add to list if not found
                        if not existing:
                            if sumito:
                                self._num_sumito += 1
                            legal_moves.append((board_position_one, board_position_two, board_position_three, move))
                # Side-step move if not in-line
                else:
                    # Checks if there is empty space for a sidestep move
                    if self._check_valid_sidestep(trips, move):
                        # Repeat from in-line
                        existing = False
                        board_position_one = Board.index_to_position(piece_one)
                        board_position_two = Board.index_to_position(piece_two)
                        board_position_three = Board.index_to_position(piece_three)
                        for legal_move in legal_moves:
                            if board_position_one in legal_move and board_position_two in legal_move and board_position_three in legal_move and move in legal_move:
                                existing = True
                                break
                        if not existing:
                            legal_moves.append((board_position_one, board_position_two, board_position_three, move))
        return legal_moves

    def find_double_pieces(self):
        """
        Finds all ally pieces which can be grouped as a 'two'.
        :return: a List containing all groups of 'two' as tuples.
        """
        # List to store double pieces
        twos = []
        # Loop through all moves for each piece
        for piece in self._ally_pieces:
            # Loop through all moves for each piece
            for move in MoveDirection:
                # Create an ally piece (if it exists, returns None if not)
                adjacent_piece = self._is_ally(piece, move)
                if adjacent_piece is not None:
                    # Check if the move has already been added in another order of pieces
                    existing = False
                    for double in twos:
                        if adjacent_piece in double and piece in double:
                            existing = True
                            break
                    if not existing:
                        # Add to list if not found
                        twos.append((piece, tuple(adjacent_piece)))
        return twos

    def find_double_pieces_enemy(self):
        """
        Finds all enemy pieces which can be grouped as a 'two'.
        :return: a List containing all groups of 'two' as tuples.
        """
        # List to store double pieces
        twos = []
        # Loop through all moves for each piece
        for piece in self._enemy_pieces:
            # Loop through all moves for each piece
            for move in MoveDirection:
                # Create an ally piece (if it exists, returns None if not)
                adjacent_piece = self._is_enemy(piece, move)
                if adjacent_piece is not None:
                    # Check if the move has already been added in another order of pieces
                    existing = False
                    for double in twos:
                        if adjacent_piece in double and piece in double:
                            existing = True
                            break
                    if not existing:
                        # Add to list if not found
                        twos.append((piece, tuple(adjacent_piece)))
        return twos

    def _is_ally(self, index, direction):
        """
        Returns the piece if an ally piece is found in the adjacent index of the direction
        to search in. Used to find a row or column of marbles to move.
        :param index: a List representing the index position of the origin piece
        :param direction: a MoveDirection enum representing the direction to look in
        :return: a List representing the piece if an ally is found, None otherwise
        """
        adjacent_piece = StateSpaceGenerator.apply_movement(index, direction)

        # If adjacent piece is in the list of allies, return the piece
        if tuple(adjacent_piece) in self._ally_pieces:
            return adjacent_piece
        # Returns None if not an ally or no piece found
        else:
            return None

    def _is_enemy(self, index, direction):
        """
        Returns the piece if an enemy piece is found in the adjacent index of the direction
        to search in. Used to find a row or column of marbles to move.
        :param index: a List representing the index position of the origin piece
        :param direction: a MoveDirection enum representing the direction to look in
        :return: a List representing the piece if an ally is found, None otherwise
        """
        adjacent_piece = StateSpaceGenerator.apply_movement(index, direction)

        # If adjacent piece is in the list of allies, return the piece
        if tuple(adjacent_piece) in self._enemy_pieces:
            return adjacent_piece
        # Returns None if not an ally or no piece found
        else:
            return None

    def find_two_piece_moves(self, groups):
        """
        Finds all legal moves for groups of two pieces.
        :param groups: a List of Tuples containing all valid groups of two pieces for the player.
        :return: a List of Tuples containing all legal moves
        """
        # List to store all legal moves
        legal_moves = []
        # Loop through all groups of two pieces
        for double in groups:
            # Loop through all moves for each group of two
            for move in MoveDirection:
                # Create local reference of each piece for readability (and speed)
                piece_one = double[0]
                piece_two = double[1]
                # Check if move is in-line by calling function from Board class
                if Board.is_inline(piece_one, piece_two, move):
                    # Checks for an empty space or a valid sumito move in the direction of movement
                    sumito = self._is_sumito(double, move)
                    empty = self._is_empty(double, move)
                    if empty or sumito:
                        existing = False
                        # Create the board position for each piece (e.g A1)
                        board_position_one = Board.index_to_position(piece_one)
                        board_position_two = Board.index_to_position(piece_two)
                        # Check if the move has already been added in different order of pieces
                        for legal_move in legal_moves:
                            if board_position_one in legal_move and board_position_two in legal_move and move in legal_move:
                                existing = True
                                break
                        # Add to list if not found
                        if not existing:
                            if sumito:
                                self._num_sumito += 1
                            legal_moves.append((board_position_one, board_position_two, move))
                # Side-step move if not in-line
                else:
                    # Checks if there is empty space for a sidestep move
                    if self._check_valid_sidestep(double, move):
                        # Repeat from in-line
                        existing = False
                        board_position_one = Board.index_to_position(piece_one)
                        board_position_two = Board.index_to_position(piece_two)
                        for legal_move in legal_moves:
                            if board_position_one in legal_move and board_position_two in legal_move and move in legal_move:
                                existing = True
                                break
                        if not existing:
                            legal_moves.append((board_position_one, board_position_two, move))
        return legal_moves

    def _check_valid_sidestep(self, pieces, move):
        """
        Finds out if a column/row of pieces moving in the indicated move direction
        is a valid side-step move, checks whether space is empty and not out of bounds.
        :param pieces: a List representing the column/row of pieces to move.
        :param move: a MoveDirection enum indicating the direction of the move.
        :return: True if move is a valid side-step, False otherwise.
        """
        # Create list for new position of pieces
        moved_pieces = []
        # Move 2 or 3 pieces to new position and add to list
        if len(pieces) == 2:
            moved_pieces.append(StateSpaceGenerator.apply_movement(pieces[0], move))
            moved_pieces.append(StateSpaceGenerator.apply_movement(pieces[1], move))
        else:
            moved_pieces.append(StateSpaceGenerator.apply_movement(pieces[0], move))
            moved_pieces.append(StateSpaceGenerator.apply_movement(pieces[1], move))
            moved_pieces.append(StateSpaceGenerator.apply_movement(pieces[2], move))

        # Returns False if new position has already been taken by other pieces
        if self._tile_taken(moved_pieces, len(moved_pieces)):
            return False

        for piece in moved_pieces:
            # Return False if any of the pieces are out of bounds
            if not self._check_piece_bounds(piece):
                return False
        # Sidestep is valid otherwise
        else:
            return True

    def _is_sumito(self, pieces, move):
        """
        Finds out if a column/row of pieces moving in the indicated move direction is a valid sumito.
        :param pieces: a List representing the column/row of pieces to move.
        :param move: a MoveDirection enum indicating the direction of the move.
        :return: True if move is a valid sumito, False otherwise.
        """
        # Number of pieces moving (which is the power of the sumito)
        num_ally_pieces = len(pieces)
        # Keep track of number of enemy pieces we need to push
        num_enemy_pieces = 0

        moved_piece = None
        # Loop through all the pieces and move it
        for piece in pieces:
            moved_piece = StateSpaceGenerator.apply_movement(piece, move)
            # Head piece found if the new position isn't already taken up
            if tuple(moved_piece) not in pieces:
                break
        # *NOTE* moved_piece = head piece - sorry not very clear

        # Create an enemy piece at the head piece's location in order to search
        # for it in the enemy's list of pieces
        dummy_piece = moved_piece.copy()
        if self._player_type == PieceType.W:
            dummy_piece[2] = PieceType.B
        else:
            dummy_piece[2] = PieceType.W
        # Check if dummy piece exists in enemy's pieces
        if tuple(dummy_piece) in self._enemy_pieces:
            num_enemy_pieces += 1
        else:
            # Piece is either ally or empty space, no need to proceed
            return False

        # Copy from Board.calculate_sumito()
        while True:
            # Move dummy piece (enemy) and ally piece to the next in-line position
            dummy_piece = StateSpaceGenerator.apply_movement(dummy_piece, move)
            moved_piece = StateSpaceGenerator.apply_movement(moved_piece, move)

            # Check if this position is still taken up by the enemy
            if tuple(dummy_piece) in self._enemy_pieces:
                num_enemy_pieces += 1
            # If piece is an ally, cannot move a sandwiched piece
            elif tuple(moved_piece) in self._ally_pieces:
                return False
            # Breaks loop at empty space otherwise
            else:
                break

        # Sumito is true if number of marbles to push is less than number of our marbles
        if num_enemy_pieces < num_ally_pieces:
            return True
        else:
            return False

    def _is_empty(self, pieces, move):
        """
        Checks if there is an empty space adjacent to the piece(s) given in the direction given.
        :param pieces: a List of pieces to be moved in-line
        :param move: a MoveDirection enum to represent the direction of the in-line move
        :return: True if there is an empty space, False otherwise
        """

        moved_piece = None
        # Find the head piece
        for piece in pieces:
            moved_piece = StateSpaceGenerator.apply_movement(piece, move)
            # Head piece found if the new position isn't already taken up
            if tuple(moved_piece) not in pieces:
                break
        # *NOTE* moved_piece = head piece - sorry not very clear

        # Check if new position is taken up by any other pieces on the board
        if self._tile_taken(moved_piece, 1):
            return False
        # Check if new position is out of bounds
        elif not self._check_piece_bounds(moved_piece):
            return False
        # Is an empty space if both of those are not True
        else:
            return True

    def find_single_piece_moves(self):
        """
        Finds all legal moves for single pieces.
        :return: a List containing all legal moves and marble as a Tuple
        """
        # Create a list for all the legal moves
        legal_moves = []
        # Loop through all the ally pieces
        for piece in self._ally_pieces:
            # Loop through all moves for each piece
            for move in MoveDirection:
                # Check if move in that direction is valid by looking for an empty space
                if self._validate_one_marble_move(move, piece):
                    # Create the board position for piece (e.g A1)
                    piece_as_position = Board.index_to_position(piece)
                    # Add to the list of moves
                    legal_moves.append((piece_as_position, move))
        return legal_moves

    def _validate_one_marble_move(self, move, piece):
        """
        Checks if the move direction is legal for the piece given.
        :param move: an Enum representing the direction of move
        :param piece: a List representing the piece
        :return: True if move is legal, False otherwise
        """
        # Create a dummy piece to store the moved location of piece
        moved_piece = StateSpaceGenerator.apply_movement(piece, move)

        # Check if piece is out of bounds
        if not StateSpaceGenerator._check_piece_bounds(moved_piece):
            return False

        if self._tile_taken(moved_piece, 1):
            return False
        # Finally return true if piece is not invalid in any way
        return True

    def _tile_taken(self, new_pieces, num_pieces):
        """
        Checks if new position for given pieces have already been taken up on the board.
        :param new_pieces: a List of new pieces.
        :return: True if positions have already been taken, False otherwise.
        """

        # No need for loop if there is only 1 piece
        if num_pieces == 1:
            # Check if position is taken up by an ally piece
            if tuple(new_pieces) in self._ally_pieces:
                return True
            # Convert piece to enemy's colour
            if self._player_type == PieceType.B:
                new_pieces[2] = PieceType.WHITE
            else:
                new_pieces[2] = PieceType.BLACK
            # Check if position is taken up by enemy piece
            if tuple(new_pieces) in self._enemy_pieces:
                return True
        # Loop through all pieces if more than 1 piece
        else:
            for new_piece in new_pieces:
                # Check if position of piece is taken up by ally piece
                if tuple(new_piece) in self._ally_pieces:
                    return True
                # Convert piece to enemy's colour
                if self._player_type == PieceType.B:
                    new_piece[2] = PieceType.WHITE
                else:
                    new_piece[2] = PieceType.BLACK
                # Check if position is taken up by enemy piece
                if tuple(new_piece) in self._enemy_pieces:
                    return True
        return False

    @staticmethod
    def apply_movement(piece, direction):
        """
        Applies the move direction to the given piece and returns the new coordinates.
        :param piece: a List representing the index of the piece on the Board
        :param direction: a MoveDirection enum
        :return: a new piece with the move applied
        """
        # Get the MoveDirection as the Move Notation value (e.g (1,0))
        movement = direction.value

        # # Gets the current position as a Letter and Number eg. [A, 5]
        # current_position = list(Board.index_to_position(piece))
        # # Apply movement to the Letter and Number
        # current_position[0] = chr(ord(current_position[0]) + movement[0])
        # current_position[1] = current_position[1] + movement[1]
        # # Get the index of the new position and build a new piece
        # new_index = Board.position_to_index(current_position)

        new_index = Board.add_direction(piece, direction)
        new_piece = [new_index[0], new_index[1], piece[2]]

        return new_piece

    @staticmethod
    def evaluate(board, team):
        """
        Evaluates a boards heuristic score
        :param board: The board to evaluate as a Board
        :param team: The team to evaluate for as a PieceType enum
        :return: The heuristic score
        """

        points_for_groups = StateSpaceGenerator.points_for_groups(board, team)
        points_for_center = StateSpaceGenerator.points_for_spaces_from_center(board, team)
        points_for_pieces = StateSpaceGenerator.points_for_pieces(board, team)
        points_for_center_enemy = StateSpaceGenerator.points_for_spaces_from_center_enemy(board, team)
        # points_for_opponent_groups = StateSpaceGenerator.points_for_opponent_groups(board, team)
        # points_for_sumito = StateSpaceGenerator.points_for_sumito(board, team)
        # points_for_three_piece_moves = StateSpaceGenerator.points_for_three_piece_moves(board, team)
        # print(f"Groups: {points_for_groups}, Center: {points_for_center}, Pieces: {points_for_pieces}, Sumito: {points_for_sumito}")
        score = points_for_groups + points_for_center + points_for_pieces + points_for_center_enemy
        # print(score)
        return score

    @staticmethod
    def points_for_spaces_from_center(board, team):
        """
        Evaluates a board and returns the score based on how far the pieces are from the centre.
        Utilizes the HeuristicWeight(DISTANCE_WEIGHT) enum to give weights to each distance from the middle.
        :param board: The board to evaluate as a Board
        :param team: The team to evaluate for as a PieceType enum
        :return: The points given to the board for how far a players pieces are from the centre.
        """
        points = 0

        tile_distance_value = HeuristicWeight.DISTANCE_TILE_ARRAY.value

        tiles = board.get_tiles()

        y_pos = 0
        x_pos = 0

        for y in tiles:
            for x in y:
                if x == team:
                    points += tile_distance_value[y_pos][x_pos]

                x_pos += 1

            x_pos = 0
            y_pos += 1

        return points

    @staticmethod
    def points_for_spaces_from_center_enemy(board, team):
        """
        Evaluates a board and returns the score based on how far the pieces are from the centre.
        Utilizes the HeuristicWeight(DISTANCE_WEIGHT) enum to give weights to each distance from the middle.
        :param board: The board to evaluate as a Board
        :param team: The team to evaluate for as a PieceType enum
        :return: The points given to the board for how far a players pieces are from the centre.
        """
        points = 0

        tile_distance_value = HeuristicWeight.ENEMY_DISTANCE_TILE_ARRAY.value

        tiles = board.get_tiles()

        if team == PieceType.WHITE:
            enemy_team = PieceType.BLACK
        else:
            enemy_team = PieceType.WHITE

        y_pos = 0
        x_pos = 0

        for y in tiles:
            for x in y:
                if x == enemy_team:
                    points += tile_distance_value[y_pos][x_pos]

                x_pos += 1

            x_pos = 0
            y_pos += 1

        return points

    @staticmethod
    def points_for_groups(board, team):
        """
        Evaluates a board and returns the score based on how many groups of pieces there are.
        Utilizes the HeuristicWeight(GROUP_WEIGHT) enum to give weights to each size of group.
        :param board: The board to evaluate as a Board
        :param team: The team to evaluate for as a PieceType enum
        :return: The points given to the board for groups of pieces.
        """
        points = 0

        group_values = HeuristicWeight.GROUP_WEIGHT.value
        # SSG for moving team
        state_space_generator = StateSpaceGenerator.build_state_space_generator(board, team)

        triple_pieces = state_space_generator.find_triple_pieces()
        double_pieces = state_space_generator.find_double_pieces()

        return len(triple_pieces) * group_values[2] + len(double_pieces) * group_values[1]

    @staticmethod
    def points_for_three_piece_moves(board, team):

        state_space_generator = StateSpaceGenerator.build_state_space_generator(board, team)
        # Generating all legal moves will give me all valid groups of marbles
        legal_moves = state_space_generator.generate_all_legal_moves()
        unique_groups = []
        points = 0

        for move in legal_moves:
            group = []
            for item in move:
                # Break when we reach the MoveDirection
                if isinstance(item, MoveDirection):
                    break
                else:
                    group.append(Board.position_to_index(item))
            if group not in unique_groups:
                unique_groups.append(group)

        for group in unique_groups:
            if len(group) == 3:
                points += 5

        return points

    # @staticmethod
    # def points_for_opponent_groups(board, team):
    #     points = 0
    #
    #     group_values = HeuristicWeight.GROUP_WEIGHT.value
    #
    #     # SSG for moving team
    #     state_space_generator = None
    #     if team == PieceType.WHITE:
    #         state_space_generator = StateSpaceGenerator.build_state_space_generator(board, PieceType.BLACK)
    #     else:
    #         state_space_generator = StateSpaceGenerator.build_state_space_generator(board, PieceType.WHITE)
    #
    #     # Generating all legal moves will give me all valid groups of marbles
    #     legal_moves = state_space_generator.generate_all_legal_moves()
    #     unique_groups = []
    #
    #     for move in legal_moves:
    #         group = []
    #         for item in move:
    #             # Break when we reach the MoveDirection
    #             if isinstance(item, MoveDirection):
    #                 break
    #             else:
    #                 group.append(Board.position_to_index(item))
    #         if group not in unique_groups:
    #             unique_groups.append(group)
    #
    #     for group in unique_groups:
    #         if len(group) == 3:
    #             points = points + (group_values[2] * 2)
    #         elif len(group) == 2:
    #             points += group_values[1]
    #
    #     return points * -1

    @staticmethod
    def points_for_pieces(board, team):
        """
        Evaluates a board and returns the score based on how pieces there are.
        Utilizes the HeuristicWeight(PIECE_WEIGHT) enum to give weights to each piece.
        :param board: The board to evaluate as a Board
        :param team: The team to evaluate for as a PieceType enum
        :return: The points given to the board for the number of pieces.
        """
        if team == PieceType.W:
            if board.black_marbles <= 8:
                return HeuristicWeight.WIN_WEIGHT.value
            own_marbles = board.white_marbles
            opponent_marbles = board.black_marbles
            return ((StateSpaceGenerator.starting_marbles - opponent_marbles) * HeuristicWeight.PIECE_WEIGHT.value) - (StateSpaceGenerator.starting_marbles - own_marbles) * (HeuristicWeight.PIECE_WEIGHT.value * 10)
        else:
            if board.white_marbles <= 8:
                return HeuristicWeight.WIN_WEIGHT.value
            own_marbles = board.black_marbles
            opponent_marbles = board.white_marbles
            return ((StateSpaceGenerator.starting_marbles - opponent_marbles) * HeuristicWeight.PIECE_WEIGHT.value) - (StateSpaceGenerator.starting_marbles - own_marbles) * (HeuristicWeight.PIECE_WEIGHT.value * 10)

    @staticmethod
    def points_for_sumito(board, team):
        state_space_generator = StateSpaceGenerator.build_state_space_generator(board, team)
        triple_pieces = state_space_generator.find_triple_pieces()
        state_space_generator.find_three_piece_moves(triple_pieces)
        double_pieces = state_space_generator.find_double_pieces()
        state_space_generator.find_two_piece_moves(double_pieces)
        # enemy_state_space_generator = None
        # if team == PieceType.WHITE:
        #     enemy_state_space_generator = StateSpaceGenerator.build_state_space_generator(board, PieceType.BLACK)
        # else:
        #     enemy_state_space_generator = StateSpaceGenerator.build_state_space_generator(board, PieceType.WHITE)
        # enemy_triple_pieces = enemy_state_space_generator.find_triple_pieces()
        # enemy_state_space_generator.find_three_piece_moves(enemy_triple_pieces)
        # enemy_double_pieces = enemy_state_space_generator.find_double_pieces()
        # enemy_state_space_generator.find_two_piece_moves(enemy_double_pieces)

        return state_space_generator._num_sumito * 10

    @staticmethod
    def build_board(state_space_generator):
        """
        Builds a board given a StateSpaceGenerator's _board_configuration variable
        :param pieces: The _pieces variable from the StateSpaceGenerator object
        :return: A Board object set up like the StateSpaceGenerator
        """
        pieces = state_space_generator._pieces

        if state_space_generator.player == PieceType.W:
            white_marbles = len(state_space_generator._ally_pieces)
            black_marbles = len(state_space_generator._enemy_pieces)
        else:
            white_marbles = len(state_space_generator._enemy_pieces)
            black_marbles = len(state_space_generator._ally_pieces)

        board = Board()

        board.white_marbles = white_marbles
        board.black_marbles = black_marbles

        for piece_data in pieces:
            board.set_tile_value(piece_data[2].value, tuple((piece_data[0], piece_data[1])))
        return board

    def minimax(self, board, depth, alpha, beta, team):
        """
        The minimax function evaluates the resulting board states of the given
        board to the depth level given, for each state it generates all legal
        next ply moves and explores the nodes not pruned via alpha-beta pruning.
        :param board: a Board representing the current board state
        :param depth: an int representing the depth to search the tree
        :param team: a PieceType enum representing the player to evaluate the score for.
        :return: an int representing the score of the board.
        """

        # Terminate if depth limit has been reached
        if depth == 0:
            # Get the score for this board
            score = self.evaluate(board, self._player_type)
            return score
        # # Terminate if BLACK has won (we need to set a positive threshold?)
        # if score > 2000:
        #     return score
        # # Terminate if WHITE has won (set a negative threshold?)
        # if score < -2000:
        #     return score

        # Create a State Space Generator to generate all legal moves of
        # the resulting board state
        state_space_gen = self.build_state_space_generator(board, team)
        all_legal_moves = state_space_gen.generate_all_legal_moves()

        # If player to move is MAX
        if team == self._player_type:
            # Variable to store the best possible score for this Node
            max_eval = StateSpaceGenerator.MIN

            # Loop through all legal moves in the resulting state and find the
            # best move by recursively calling minimax
            for move in all_legal_moves:
                # Create a board object to create child node
                max_board = StateSpaceGenerator.build_board(state_space_gen)

                # Create a list for pieces to be moved in this move notation
                pieces_to_move = []
                # Get move direction as local variable
                move_enum = move[len(move) - 1]

                # Get all the pieces to be moved (exclude the move direction enum)
                for i in range(len(move) - 1):
                    pieces_to_move.append(move[i])

                # Move the piece
                max_board.move_piece(move_enum, pieces_to_move)

                board_configuration = StateSpaceGenerator.generate_board_configuration(max_board)

                if self._player_type == PieceType.WHITE:
                    transposition_key = 'w ' + board_configuration
                else:
                    transposition_key = 'b ' + board_configuration

                # Check if this state exists in Transposition table
                if transposition_key in StateSpaceGenerator.TRANSPOSITION_TABLE:
                    eval = StateSpaceGenerator.TRANSPOSITION_TABLE.get(transposition_key)

                    max_eval = max(max_eval, eval)

                    # Alpha-Beta pruning
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                else:
                    # Find the minimax score for resulting board state
                    if self._player_type == PieceType.WHITE:
                        eval = self.minimax(max_board, depth - 1, alpha, beta, PieceType.BLACK)
                    else:
                        eval = self.minimax(max_board, depth - 1, alpha, beta, PieceType.WHITE)

                    # Add heuristic score to transposition table
                    StateSpaceGenerator.TRANSPOSITION_TABLE[transposition_key] = eval

                    # Set best to eval if it is greater
                    max_eval = max(max_eval, eval)

                    # Alpha-Beta pruning
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break

            return max_eval
        # If player is MIN
        else:
            minEval = StateSpaceGenerator.MAX

            for move in all_legal_moves:
                # Create a board object to create child node
                min_board = StateSpaceGenerator.build_board(state_space_gen)

                # Create a list for pieces to be moved in this move notation
                pieces_to_move = []
                # Get move direction as local variable
                move_enum = move[len(move) - 1]

                # Get all the pieces to be moved (exclude the move direction enum)
                for i in range(len(move) - 1):
                    pieces_to_move.append(move[i])

                # Move the piece
                min_board.move_piece(move_enum, pieces_to_move)

                board_configuration = StateSpaceGenerator.generate_board_configuration(min_board)

                if self._player_type == PieceType.WHITE:
                    transposition_key = 'b ' + board_configuration
                else:
                    transposition_key = 'w ' + board_configuration

                # Check if this state exists in Transposition table
                if transposition_key in StateSpaceGenerator.TRANSPOSITION_TABLE:
                    eval = StateSpaceGenerator.TRANSPOSITION_TABLE.get(transposition_key)

                    minEval = min(minEval, eval)

                    # Alpha-Beta pruning
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                else:
                    # Find the minimax score for resulting board state
                    if self._player_type == PieceType.WHITE:
                        eval = self.minimax(min_board, depth - 1, alpha, beta, PieceType.WHITE)
                    else:
                        eval = self.minimax(min_board, depth - 1, alpha, beta, PieceType.BLACK)

                    # Add heuristic score to transposition table
                    StateSpaceGenerator.TRANSPOSITION_TABLE[transposition_key] = eval

                    # Set minEval to eval if lesser
                    minEval = min(minEval, eval)

                    # Alpha-Beta pruning
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break

            return minEval

    def generate_all_legal_moves(self):
        """
        Generates a List of legal next ply moves of current board configuration.
        Moves are generated by three marbles first, then two marbles and lastly
        single marbles, since three marble moves are generally better.
        :return: a List of all legal moves
        """

        # Create list to store all legal moves
        all_moves = []

        # Get all triple marble combinations
        three_marble_combos = self.find_triple_pieces()
        # Get list of all triple marble moves
        three_marble_moves = self.find_three_piece_moves(three_marble_combos)
        all_moves.extend(three_marble_moves)

        # Get list of all legal single marble moves
        single_marble_moves = self.find_single_piece_moves()
        all_moves.extend(single_marble_moves)

        # Get all double marble combinations
        double_pieces = self.find_double_pieces()
        # Get list of all legal double marble moves
        two_marble_moves = self.find_two_piece_moves(double_pieces)
        all_moves.extend(two_marble_moves)

        return all_moves

    def generate_three_piece_moves(self):
        """
        Generates a List of legal moves for three piece marble combinations only.
        :return: a List of moves.
        """
        # Get all triple marble combinations
        three_marble_combos = self.find_triple_pieces()
        # Get list of all triple marble moves
        three_marble_moves = self.find_three_piece_moves(three_marble_combos)
        return three_marble_moves

    def find_best_move(self, depth, time_given):
        """
        Finds the best move for the given board state and team acting.
        :param depth: the depth to search the tree as an int
        :param time_given: int representing the number of seconds given to search for move
        :return: a Move Notation representing the best move
        """

        # Start time
        start_time = time.time()
        # Take 0.5 seconds off of time given for buffer
        safe_time_given = time_given - 0.5

        # Generate a state space generator
        all_legal_moves = self.generate_all_legal_moves()

        # Initiate best heuristic score as MIN, and best move as None
        best_value = StateSpaceGenerator.MIN
        best_move = None

        for move in all_legal_moves:
            move_board = StateSpaceGenerator.build_board(self)

            # Create a list for pieces to be moved in this move notation
            pieces_to_move = []
            # Get move direction as local variable
            move_enum = move[len(move) - 1]

            # Get all the pieces to be moved (exclude the move direction enum)
            for i in range(len(move) - 1):
                pieces_to_move.append(move[i])

            # Move the piece
            move_board.move_piece(move_enum, pieces_to_move)

            # Find minimax value for move
            if self._player_type == PieceType.WHITE:
                move_value = self.minimax(move_board, depth, StateSpaceGenerator.MIN, StateSpaceGenerator.MAX, PieceType.BLACK)
            else:
                move_value = self.minimax(move_board, depth, StateSpaceGenerator.MIN, StateSpaceGenerator.MAX, PieceType.WHITE)
            print(move)
            print(move_value)

            # Update best move/value if better than current
            if move_value > best_value:
                best_move = move
                best_value = move_value

            # # End time for each loop
            end_time = time.time()
            if end_time - start_time >= safe_time_given:
                # print("Time is up")
                # print(f"Stopped search at {end_time - start_time}")
                break

        print(f"The best move is {best_move} at a value of {best_value}")
        return best_move

    @staticmethod
    def generate_board_configuration(board):
        """
        Generates a board configuration string given a Board object.
        :param board: a Board object
        :return: a String as the Board Configuration
        """
        # Final string for board configuration
        board_configuration_string = ""
        # String for black pieces
        black_pieces = ""
        # String for white pieces
        white_pieces = ""

        tile_values = board.get_tiles_values()

        # Loop the board from bottom up (visually, A-I)
        for i in range(len(tile_values) - 1, -1, -1):
            # Loop the board from left to right
            for j in range(len(tile_values[i])):
                # Store the piece locally
                piece = tile_values[i][j]
                # Convert index position to board position (e.g A1)
                piece_tuple = Board.index_to_position((i, j))

                # Append 'b' or 'w' accordingly and add to corresponding string
                if piece == PieceType.BLACK.value:
                    piece_as_string = piece_tuple[0] + str(
                        piece_tuple[1]) + 'b'
                    black_pieces += piece_as_string
                    black_pieces += ','
                elif piece == PieceType.WHITE.value:
                    piece_as_string = piece_tuple[0] + str(
                        piece_tuple[1]) + 'w'
                    white_pieces += piece_as_string
                    white_pieces += ','

        # Add black pieces first, then white
        board_configuration_string += black_pieces
        board_configuration_string += white_pieces
        # Remove the extra comma and add to the list
        return board_configuration_string[:-1]

    @staticmethod
    def build_state_space_generator(board, team):
        """
        Creates a StateSpaceGenerator using a provided board and team
        :param board: The Board to build the StateSpaceGenerator with
        :param team: The PieceType to set as the ally piece in the StateSpaceGenerator
        :return: The StateSpaceGenerator object built using the board
        """
        state_space_generator = StateSpaceGenerator()

        input_formatted_string = ""

        tiles = board.get_tiles_values()

        y_pos = 0
        x_pos = 0

        # Construct a string similar to the input file using the board tiles
        for y in tiles:
            for x in y:
                if x is not None:
                    temp_piece_pos = Board.index_to_position(tuple((y_pos, x_pos)))
                    temp_piece_team = "w" if x else "b"
                    input_formatted_string += f"{temp_piece_pos[0]}{temp_piece_pos[1]}{temp_piece_team},"

                x_pos += 1

            x_pos = 0
            y_pos += 1

        input_formatted_string = input_formatted_string[:-1]

        # Set the player colour to the corresponding Enum
        state_space_generator._player_type = team

        state_space_generator._board_configuration = input_formatted_string
        # Uses a generator method to generate all pieces as array
        # indexes corresponding to our State Representation
        piece_generator = state_space_generator._piece_generator()
        state_space_generator._pieces = [piece for piece in piece_generator]
        # Separate lists for ally and enemy pieces for ease of search
        state_space_generator._ally_pieces = \
            [piece for piece in state_space_generator._pieces if piece[2] == state_space_generator._player_type]
        state_space_generator._enemy_pieces = \
            [piece for piece in state_space_generator._pieces if piece[2] != state_space_generator._player_type]

        return state_space_generator

    @staticmethod
    def _check_piece_bounds(piece):
        """
        Given a piece, check if the x-y coordinates are within the board bounds.
        :param piece: a List representing the x-y coordinates and colour of piece
            on the board.
        :return: True if in bounds, False otherwise.
        """

        # If x or y is negative it must be out of bounds
        if piece[0] < 0 or piece[1] < 0:
            return False
        elif piece[0] > 8:
            return False

        # Max x index of E-I is y + 4
        if piece[0] < 5:
            if piece[1] > piece[0] + 4:
                return False
        # Max x index of the rest hard coded
        elif piece[0] == 5:
            if piece[1] > 7:
                return False
        elif piece[0] == 6:
            if piece[1] > 6:
                return False
        elif piece[0] == 7:
            if piece[1] > 5:
                return False
        elif piece[0] == 8:
            if piece[1] > 4:
                return False

        return True

    @staticmethod
    def create_move_list(single_moves, double_moves, triple_moves):
        """
        Creates a Tuple of the moves given represented by our group's determined
        move notation.
        :param single_moves: List of single marble moves
        :param double_moves: List of double marble moves
        :param triple_moves: List of triple marble moves
        :return: Tuple containing all moves converted to our move notation
        """

        move_list = []
        # Add all single moves into the list as a Tuple
        for single_move in single_moves:
            move_list.append((single_move[0], single_move[1]))
        # Add all double moves into the list as a Tuple
        for double_move in double_moves:
            move_list.append((double_move[0], double_move[1], double_move[2]))
        # Add all triple moves into the list as a Tuple
        for triple_move in triple_moves:
            move_list.append((triple_move[0], triple_move[1], triple_move[2], triple_move[3]))

        return move_list


def read_board_file(file_name):
    """
    Reads the board file in and generates a List of all board configurations.
    :param file_name: a String containing the file name
    :return: a List of all board configurations on separate lines
    """
    try:
        with open(file_name, mode='r', encoding='utf-8') as input_file:
            return input_file.read().splitlines()
    except FileNotFoundError:
        print(f"File {file_name} cannot be found")


def user_file_prompt():
    """
    Prompts user for file name
    :return:
    """
    while True:
        try:
            return input("Please enter file name you'd like to test without extension, i.e. Test2: ")
        except IOError:
            print("Invalid input, try again.")


def main():
    """
    Driver method of State Space Generator Module
    """
    test_file = ""

    # Create the state space generator object, call method to read input file
    state_space_generator = StateSpaceGenerator()
    while True:
        try:
            test_file = user_file_prompt()
            state_space_generator.read_input_file(test_file + ".input")
            break
        except FileNotFoundError:
            print(f"File name {test_file} cannot be found. Try again")

    # Get list of all legal single marble moves
    single_marble_moves = state_space_generator.find_single_piece_moves()

    # Get all double marble combinations
    double_pieces = state_space_generator.find_double_pieces()
    # Get list of all legal double marble moves
    two_marble_moves = state_space_generator.find_two_piece_moves(double_pieces)

    # Get all triple marble combinations
    three_marble_combos = state_space_generator.find_triple_pieces()
    # Get list of all triple marble moves
    three_marble_moves = state_space_generator.find_three_piece_moves(three_marble_combos)

    # Create a board object using the pieces given in input file
    # Getting a list of all pieces representing by array indexes
    pieces_on_board = state_space_generator.pieces
    # Convert array indexes to to position on board as a list(e.g A1)
    pieces_on_board_position = [(piece[2], Board.index_to_position(piece)) for piece in pieces_on_board]
    board = Board()
    # Add all pieces to the board
    for piece in pieces_on_board_position:
        board.set_tile(piece[0], piece[1])

    # Convert all moves to our Move Notation as a List of Tuples
    move_notation_tuple = StateSpaceGenerator.create_move_list(single_marble_moves, two_marble_moves, three_marble_moves)

    # Create a Board object for each move in order to print board configuration
    # Create list for all resulting board objects
    resulting_boards = []

    # Apply move to board object and insert it to list
    for move in move_notation_tuple:
        # Create a list for pieces to be moved in this move notation
        pieces_to_move = []
        # Get move direction as local variable
        move_enum = move[len(move) - 1]

        # Get all the pieces to be moved (exclude the move direction enum)
        for i in range(len(move) - 1):
            pieces_to_move.append(move[i])

        # Move the piece
        board.move_piece(move_enum, pieces_to_move)
        # Add the board state as a 2D array to the List
        resulting_boards.append(board.get_tiles_values())

        # Reset the board
        board.clear_tiles()
        # Add the original state of the board back
        for piece in pieces_on_board_position:
            board.set_tile(piece[0], piece[1])

    # Create list for board configuration
    board_configuration_generated = []

    # state_space_generator.points_for_groups()

    # Generate the board configuration as the ordered String
    for board in resulting_boards:
        # Final string for board configuration
        board_configuration_string = ""
        # String for black pieces
        black_pieces = ""
        # String for white pieces
        white_pieces = ""

        # Loop the board from bottom up (visually, A-I)
        for i in range(len(board) - 1, -1, -1):
            # Loop the board from left to right
            for j in range(len(board[i])):
                # Store the piece locally
                piece = board[i][j]
                # Convert index position to board position (e.g A1)
                piece_tuple = Board.index_to_position((i, j))

                # Append 'b' or 'w' accordingly and add to corresponding string
                if piece == PieceType.BLACK.value:
                    piece_as_string = piece_tuple[0] + str(
                        piece_tuple[1]) + 'b'
                    black_pieces += piece_as_string
                    black_pieces += ','
                elif piece == PieceType.WHITE.value:
                    piece_as_string = piece_tuple[0] + str(
                        piece_tuple[1]) + 'w'
                    white_pieces += piece_as_string
                    white_pieces += ','

        # Add black pieces first, then white
        board_configuration_string += black_pieces
        board_configuration_string += white_pieces
        # Remove the extra comma and add to the list
        board_configuration_string = board_configuration_string[:-1]
        board_configuration_generated.append(board_configuration_string)

    """
    # FOR TESTING PURPOSES
    # Read in the board configurations from Chi En
    board_configurations_master = read_board_file("Test4.board")

    # Count the number of matches, Test1 has 32 board configs and Test2 has 53
    match = 0
    for board_config in board_configuration_generated:
        if board_config in board_configurations_master:
            match += 1
    print(match)
    """

    # Generated plain text file for board configuration
    with open(test_file + ".board", mode='w', encoding='utf-8') as board_file:
        for board_config in board_configuration_generated:
            board_file.write(board_config + "\n")

    # Convert MoveDirection enum to value only to match Move Notation
    output_move_notation = []
    for move in move_notation_tuple:
        move = list(move)
        move[len(move) - 1] = move[len(move) - 1].value
        output_move_notation.append(move)

    # Generate plain text file for move notation
    with open(test_file + ".move", mode='w', encoding='utf-8') as move_file:
        for move in output_move_notation:
            move_file.write(str(move) + "\n")


if __name__ == "__main__":
    # main()

    board = Board()
    board.set_tile(PieceType.BLACK, ("C", 5))
    board.set_tile(PieceType.BLACK, ("D", 5))
    board.set_tile(PieceType.BLACK, ("E", 4))
    board.set_tile(PieceType.BLACK, ("E", 5))
    board.set_tile(PieceType.BLACK, ("E", 6))
    board.set_tile(PieceType.BLACK, ("F", 5))
    board.set_tile(PieceType.BLACK, ("F", 6))
    board.set_tile(PieceType.BLACK, ("F", 7))
    board.set_tile(PieceType.BLACK, ("F", 8))
    board.set_tile(PieceType.BLACK, ("G", 6))
    board.set_tile(PieceType.BLACK, ("H", 6))

    board.set_tile(PieceType.WHITE, ("C", 3))
    board.set_tile(PieceType.WHITE, ("C", 4))
    board.set_tile(PieceType.WHITE, ("D", 3))
    board.set_tile(PieceType.WHITE, ("D", 4))
    board.set_tile(PieceType.WHITE, ("D", 6))
    board.set_tile(PieceType.WHITE, ("E", 7))
    board.set_tile(PieceType.WHITE, ("F", 4))
    board.set_tile(PieceType.WHITE, ("G", 5))
    board.set_tile(PieceType.WHITE, ("G", 7))
    board.set_tile(PieceType.WHITE, ("G", 8))
    board.set_tile(PieceType.WHITE, ("G", 9))
    board.set_tile(PieceType.WHITE, ("H", 7))
    board.set_tile(PieceType.WHITE, ("H", 8))
    board.set_tile(PieceType.WHITE, ("H", 9))

    state_space_gen = StateSpaceGenerator.build_state_space_generator(board, PieceType.BLACK)
    # print(board)

    best_move = state_space_gen.find_best_move(2, 100)
