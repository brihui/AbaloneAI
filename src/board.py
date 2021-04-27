from exceptions import CannotMoveException
from exceptions import InvalidParameterException
from enums import PieceType
from enums import InitialBoardState
from enums import MoveDirection
import copy


# noinspection SpellCheckingInspection
class Board:
    """
    A class to represent a Board in the game of Abalone.

    The boards data structure uses a 2D array of values which correspond to the PieceType enum in enums.
    The board uses a coordinate system of [A-I,1-9]. This is implemented as a sequence with a string and an integer.

    The board stores the raw values from the PieceType enum for maximum efficiency. To take advantage of this
    efficiency, uses the functions which end in value (eg. foo_value, bar_values). This avoids converting the contents
    of the board to an enum for abstraction.
    """

    # The size of the Y axis for the tiles array
    max_y = 8

    def __init__(self, layout=None, white_marbles=None, black_marbles=None, board=None, tiles=None):
        """
        Constructs a board.
        :param layout: The layout of the board as an InitialBoardState enum
        :param white_marbles: The number of white marbles on the board
        :param black_marbles: The number of black marbles on the board
        :param board: The board object to set this as a copy of
        """

        if board is not None:
            self._tiles = copy.deepcopy(board.get_tiles_values())
            self.white_marbles = board.white_marbles
            self.black_marbles = board.black_marbles
        else:
            if layout is None and tiles is None:  # If no tiles or layout passed in, just set as empty
                self._tiles = copy.deepcopy(InitialBoardState.EMPTY.value)
            elif tiles is None:
                self._tiles = copy.deepcopy(layout.value)
            else:
                self._tiles = copy.deepcopy(tiles)

            if white_marbles is None:
                self.white_marbles = 0
                for y in self._tiles:
                    for x in y:
                        if x:
                            self.white_marbles += 1

            else:
                self.white_marbles = white_marbles

            if black_marbles is None:
                self.black_marbles = 0
                for y in self._tiles:
                    for x in y:
                        if x is False:
                            self.black_marbles += 1
            else:
                self.black_marbles = black_marbles

    def update_marble_counts(self):
        self.white_marbles = 0
        self.black_marbles = 0
        for y in self._tiles:
            for x in y:
                if x:
                    self.white_marbles += 1
                elif x is False:
                    self.black_marbles += 1

    def has_won(self):
        """
        Returns a PieceType enum of the team that won, otherwise false.
        (Note that both PieceType enums evaluate to true)
        :return: a PieceType enum of the team that won, otherwise false.
        """
        if self.black_marbles <= 8:
            return PieceType.W
        elif self.white_marbles <= 8:
            return PieceType.B
        else:
            return False

    def get_white_marbles(self):
        return self.white_marbles

    def get_black_marbles(self):
        return self.black_marbles

    def clear_tiles(self):
        """
        Makes all tiles None to clear the board
        """
        self._tiles = [[None for tile in row] for row in self._tiles]

    def set_tiles(self, tiles):
        """
        Set the tiles to a 2D array of PieceType enums.
        :param tiles: The tiles array of PieceType enums
        """
        self._tiles = [[tile.value for tile in row] for row in tiles]

    def get_tiles(self):
        """
        Provides the tiles as a 2D array of PieceType enums.
        :return: 2D array containing PieceType enums
        """
        board = [[PieceType(tile) for tile in row] for row in self._tiles]
        return board

    def get_tiles_values(self):
        """
        Provides the tiles as a 2D array of PieceType enum values (True, False or None).

        Significantly more efficient than get_tiles(). Use this for AI calculations.
        :return: 2D array containing True, False or None (see PieceType in enums)
        """
        return self._tiles

    def get_tile(self, position):
        """
        Get a tile on the board
        :param position: A sequence containing a character between A-I followed by a number 1-9.
            Must be a valid board position.
        :return: The piece at the given position as a PieceType enum
        """
        # Convert the coordinate into array indices (see position_to_index for explanation of calculations)
        y, x = Board.position_to_index(position)

        return PieceType(self._tiles[y][x])

    def set_tile(self, piece, position):
        """
        Manually set the piece at a specified position on the board.
        :param piece: An enum from the PieceType enums
        :param position: A sequence containing a character between A-I followed by a number 1-9.
            Must be a valid board position.
        """
        y, x = Board.position_to_index(position)

        self._tiles[y][x] = piece.value

    def get_tile_value(self, index):
        """
        Get a tile on the board as a value of the PieceType enum

        Use this for maximum efficiency.
        Position must be converted to index beforehand using position_to_index
        :param index: Position coordinates converted using position_to_index()
        """
        return self._tiles[index[0]][index[1]]

    def set_tile_value(self, value, index):
        """
        Manually set the value at a specified position on the board.

        Use this for maximum efficiency.
        Position must be converted to index beforehand using position_to_index
        :param value: A value from the PieceType enums
        :param index: Position coordinates converted using position_to_index()
        """
        self._tiles[index[0]][index[1]] = value

    def move_piece(self, direction, marbles):
        """
        Moves a piece or selection of pieces.

        Precondition: The number of pieces are between 1 and 3, and are all in a row.
        Pieces do not need to be in a specific order.

        :param direction: The destination of the pieces movement as a MoveDirection enum
        :param marbles: A list of coordinates for each piece, with each coordinate as a tuple of string, integer
                        corresponding to the row and column. eg. ("A", 1)
        :return: PieceType enum of the marble pushed off
        """
        # Convert position coordinate format to tiles array indices
        marbles = [Board.position_to_index(marble) for marble in marbles]
        # Call _move() as a non-push movement
        marble_pushed_off_value = self._move(direction, marbles, False)

        return PieceType(marble_pushed_off_value)

    def _move(self, direction, marbles, is_push):
        """
        Moves a piece or selection of pieces. Use move_piece() for external use.

        :param direction: The destination of the pieces movement as a MoveDirection enum
        :param marbles: A list of array indices for each marble as a position coordinate after position_to_index()
                        conversion.
        :param is_push: If the marble is being pushed in a legal sumito.
        :return: True if a white marble was pushed off. False if a black marble was pushed off. None otherwise.
        """
        number_of_marbles = len(marbles)

        # Move one marble
        if number_of_marbles == 1:
            current_index = marbles[0]
            # Get the new index for the moved marble, while also validating the move
            new_index = self.calculate_move_marble(direction, current_index, is_push)

            piece_type = self.get_tile_value(current_index)  # Get the piece type

            self.set_tile_value(None, current_index)  # Remove the piece

            # If the marble is not inbounds, dont put it back on the board. Decrement the marble count
            if not Board.is_inbounds(new_index):
                if piece_type:
                    self.white_marbles -= 1
                else:
                    self.black_marbles -= 1
            # Otherwise, marble is inbounds, so place it on the board
            else:
                self.set_tile_value(piece_type, new_index)

            # No marbles pushed off, return None
            return None

        # Moving two or more marbles
        else:
            # Get the new indices for the move, while also validating the move
            new_indices, marbles_to_sumito = self.calculate_move_marbles(direction, marbles, is_push)
            current_indices = marbles  # Make a new array for the marbles to make code more readable

            piece_type = self.get_tile_value(current_indices[0])
            marble_pushed_off = None  # Return statement variable (see param documentation)

            # If there are marbles we need to sumito
            if len(marbles_to_sumito) != 0:
                # Move the marbles without recalculating a sumito
                self._move(direction, marbles_to_sumito, True)

            # Remove the pieces
            for index in current_indices:
                self.set_tile_value(None, index)

            for index in new_indices:
                # If the marble is not inbounds, dont put it back on the board. Decrement the marble count
                if not Board.is_inbounds(index):
                    if piece_type:
                        marble_pushed_off = True
                        self.white_marbles -= 1
                    else:
                        marble_pushed_off = False
                        self.black_marbles -= 1
                # Otherwise, marble is inbounds, so place it on the board
                else:
                    self.set_tile_value(piece_type, index)

            return marble_pushed_off

            # Debug statements
            # print(f"Index of piece 1 before: {current_indices[0]}")
            # print(f"Index of piece 2 before: {current_indices[1]}")
            # print(f"Is the movement inline? {Board.is_inline(current_indices[0], current_indices[1], direction)}")
            # print(f"Index of piece 1 after: {new_indices[0]}")
            # print(f"Index of piece 2 after: {new_indices[1]}")

    def calculate_sumito(self, index, direction, enemy_piece_type, power):
        """
        Calculates and validates a Sumito move. Returns true if move is a sumito.
        :param index: The head of the enemy column of pieces as a tiles index
        :param direction: The movement vector as a MoveDirection enum
        :param enemy_piece_type: The value of the enemy piece type as a PieceType.value (boolean)
        :param power: The number of pieces in the inline column performing the sumito
        """
        ally_piece_type = not enemy_piece_type  # The PieceType.value of the enemy
        search_index = index  # An index to parse through the tiles along the line of sumito
        marbles_to_push = [search_index]  # Keeps track of marbles to move

        # While loop that goes through inline tiles and collects up enemy marbles to sumito
        # I appologise for using while True, it was a bit more efficient. Gotta go fast.
        while True:  # len(marbles_to_push) <= power:
            search_index = Board.add_direction(search_index, direction)

            # Position is out of bounds after pushed
            if not self.is_inbounds(search_index):
                break

            marble_at_index = self.get_tile_value(search_index)

            # Position contains an enemy marble
            if marble_at_index == enemy_piece_type:
                marbles_to_push.append(search_index)
            # Position contains an ally marble
            elif marble_at_index == ally_piece_type:
                raise CannotMoveException()  # Cannot push a sandwiched ally marble
            # Position contains no marble
            else:
                break  # Nothing will be pushed past an empty space

        if len(marbles_to_push) >= power:
            raise CannotMoveException()  # Cannot push more marbles than the inline group's power

        return marbles_to_push
        # self._move(direction, marbles_to_push, True)  # Move the pieces without re-calculating for a possible sumito

    def calculate_move_marbles(self, direction, marbles, is_push):
        """
        Calculates moving a valid column of marbles, and what the new indices of the marbles are in the tiles array.

        Throws a CannotMoveException if the move is invalid.
        :param direction: The destination of the pieces movement as a MoveDirection enum
        :param marbles: A list of array indices for each marble as a position coordinate after position_to_index()
                        conversion.
        :param is_push: If the marble is being pushed in a legal sumito.
        :return: The new indices for each of the marbles to be moved
        """
        # Move two or more marbles
        current_indices = marbles  # Make a new array for the marbles to make code more readable

        # Indices of marbles after movement
        new_indices = [Board.add_direction(marble, direction) for marble in current_indices]

        piece_type = self.get_tile_value(current_indices[0])
        number_of_marbles = len(marbles)
        marbles_to_sumito = []

        # If the movement is inline, push over the other marbles
        if Board.is_inline(current_indices[0], current_indices[1], direction):
            # If the marbles aren't already being pushed, check for sumito
            if not is_push:
                enemy_piece = not piece_type
                valid_move = False

                # Check that the new position has an opponents marble
                for index in new_indices:
                    if not valid_move:

                        new_tile_value = self.get_tile_value(index)
                        # Tile ahead has an opponent piece
                        if new_tile_value == enemy_piece:
                            # Get a list of the marbles to push
                            marbles_to_sumito = self.calculate_sumito(index, direction, enemy_piece, number_of_marbles)
                            valid_move = True
                        # Tile ahead is none
                        elif new_tile_value is None:
                            valid_move = True  # Piece is moving to empty, stop checking new indices

                if not valid_move:
                    # Move is not valid, its trying to push its own piece.
                    raise CannotMoveException()  # Cannot push an ally marble

        # Marbles are not inline, its a sidestep. Validate sidestep
        else:
            for index in new_indices:
                if self.get_tile_value(index) is not None:
                    raise CannotMoveException()  # Marble in the way of sidestep

        return new_indices, marbles_to_sumito

    def calculate_move_marble(self, direction, marble, is_push=False):
        """
        Calculates moving a single marble, and what the new index of the marble is in the tiles array.

        Throws a CannotMoveException if the move is invalid.
        :param direction: The direction to move the marble as a MoveDirection enum
        :param marble: The index of the marble in the Tiles array through position_to_index()
        :param is_push: If the single marble is being pushed in a sumito
        :return: The index where the new marble should be placed
        """
        current_index = marble  # The current position of the piece
        new_index = Board.add_direction(current_index, direction)  # The new position for the piece

        if not Board.is_inbounds(new_index):
            if not is_push:
                raise CannotMoveException()  # Cannot move a marble out of bounds!
            else:
                return new_index  # Piece is being pushed out of bounds, its okay

        if self.get_tile_value(new_index) is not None:
            raise CannotMoveException()  # Cannot move a single marble onto an occupied space

        return new_index

    def __str__(self):
        """
        Returns a string representation of the board.
        """
        string = ""
        i = 0
        for row in self._tiles:
            i += 1

            # Align the board
            if i < 5:
                string += " "*(5 - i)

            # Add the tiles in a row to the string
            for tile in row:
                if tile == PieceType.WHITE.value:
                    string += 'W '
                elif tile == PieceType.BLACK.value:
                    string += 'B '
                else:
                    string += "_ "

            string += "\n"

            # Align the board
            if i >= 5:
                string += " "*(i-4)

        return string

    @staticmethod
    def is_inbounds(index):
        """
        Checks if the index of the tiles array is valid

        :param index: The index of the tiles array as a two int tuple
        :return: True if valid index in the array
        """
        x_offset = index[0] if index[0] < 5 else Board.max_y - index[0]  # Shifting of X values due to board shape
        return 0 <= index[0] <= Board.max_y and 0 <= index[1] <= 4 + x_offset

    @staticmethod
    def position_to_index(position):
        """
        Returns a tuple with the index in the first array followed by the nested array for _tiles
        :param position: A sequence containing a character between A-I followed by a number 1-9.
            Must be a valid board position.
        :return: A tuple containing the index in the first array followed by the index in the second array
        """
        try:
            # Sets the index for the first array, ie the Y axis of the board.
            # eg. A == 0, B == 1, ...
            inverse_y = ord(position[0]) - 65
            y = Board.max_y - inverse_y
            # Calculate the X position by subtracting 1
            # But if its above E on the board, the possible X positions start from (inverse_y - 3)
            x = position[1] - 1 if inverse_y < 5 else position[1] - (inverse_y - 3)
        except TypeError:
            raise InvalidParameterException("Must pass in a position with format (char, int)!")

        return y, x

    @staticmethod
    def index_to_position(index):
        """
        Converts a tiles array index to a position
        :param index: A position converted using position_to_index()
        :return: The position as a sequence containing a character between A-I followed by a number 1-9.
        """
        try:
            # Flipped equations used in position_to_index()
            inverse_y = Board.max_y - index[0]
            y = inverse_y + 65

            x = index[1] + 1 if inverse_y < 5 else index[1] + (inverse_y - 3)
        except TypeError:
            raise InvalidParameterException("Must pass in a tiles array index with format (int, int)!")

        return chr(y), x

    @staticmethod
    def position_difference(a, b):
        """
        Calculates the difference between positions a and b
        :param a: The first position to subtract from converted using position_to_index()
        :param b: The second position to subtract with converted using position_to_index()
        """
        y_diff = b[0] - a[0]
        x_diff = Board.index_to_position(a)[1] - Board.index_to_position(b)[1]

        return y_diff, x_diff

    @staticmethod
    def add_direction(index, direction):
        """
        Adds the direction vector to the coordinate
        :param index: Position coordinates converted using position_to_index()
        :param direction: A MoveDirection enum
        :return: The new coordinate adjusted by adding the direction
        """
        movement = direction.value

        # Old code: Expensive but trustworthy
        # current_position = list(Board.index_to_position(index))
        # # Apply movement to the Letter and Number
        # current_position[0] = chr(ord(current_position[0]) + movement[0])
        # current_position[1] = current_position[1] + movement[1]
        # # Get the index of the new position and build a new piece
        # return Board.position_to_index(current_position)

        prev_y = index[0]
        prev_x = index[1]
        delta_y = movement[0]
        delta_x = movement[1]

        y = prev_y - delta_y
        # Subtract the movement in the y direction to account for x value drifting between E and I
        if prev_y == 3 and y == 4:
            # Special case: If the new Y is in the middle, and we're coming from the row above, we need to subtract one
            x = prev_x + delta_x - delta_y
        else:
            x = prev_x + delta_x if y >= 4 else prev_x + delta_x - delta_y

        return y, x

    @staticmethod
    def is_inline(a, b, direction):
        """
        Checks if two position unit vectors are equal given their indices in the tiles array.
        :param a: The first position converted using position_to_index(). A piece of the selected pieces to move.
        :param b: The second position converted using position_to_index(). A piece of the selected pieces to move.
        :param direction: The direction of the move as a value of a MoveDirection enum
        :return: True if the movement is inline
        """
        difference = Board.position_difference(a, b)

        # Reduce difference components to 1 or 0 or -1, essentially making it a movement unit vector
        try:
            difference_y = difference[0] / difference[0]
        except ZeroDivisionError:
            difference_y = 0
        try:
            difference_x = difference[1] / difference[1]
        except ZeroDivisionError:
            difference_x = 0

        # Check that the direction of movement is equal to the directional difference in pieces
        inline_forwards = difference_y == direction.value[0] and difference_x == direction.value[1]
        # Check that the direction of movement is equal to the opposite directional difference in pieces
        inline_backwards = -difference_y == direction.value[0] and -difference_x == direction.value[1]

        return inline_forwards or inline_backwards

    def is_valid_column(self, marbles):
        """
        Returns true if a list of selected marbles is a valid column of same-team marbles.

        Marbles must be an in order selection (eg. tail to head or head to tail order)

        :param marbles: A list of marble coordinated converted using position_to_index()
        :return: True if valid column of same-team marbles. False otherwise (including if its just one marble)
        """
        length = len(marbles)

        # Must select either 2 or 3 marbles
        if length <= 1 or length > 3:
            return False

        # The PieceType of this selection of marble
        piece_type = self.get_tile_value(marbles[0])

        # If a blank space is seleted, not a column
        if piece_type is None:
            return False

        # Major code overlap with is_inline, should be optomized to not need to recalculate!
        difference = Board.position_difference(marbles[0], marbles[1])

        # Reduce difference components to 1 or 0 or -1, essentially making it a movement unit vector
        try:
            direction_y = difference[0] / difference[0]
        except ZeroDivisionError:
            direction_y = 0
        try:
            direction_x = difference[1] / difference[1]
        except ZeroDivisionError:
            direction_x = 0

        direction = MoveDirection((direction_y, direction_x))

        total_distance = [x for x in difference]  # The total distance between all marbles
        if length == 3:
            second_difference = [x for x in Board.position_difference(marbles[1], marbles[2])]
            total_distance[0] += second_difference[0]
            total_distance[1] += second_difference[1]

        # print(f"Total distance: {total_distance}")
        direction_mult_by_length = [x * (length-1) for x in direction.value]
        # print(f"Direction times length: {direction_mult_by_length}")

        # Should abs them in the first list comprehension above for efficiency
        total_distance = [abs(x) for x in total_distance]
        direction_mult_by_length = [abs(x) for x in direction_mult_by_length]

        # Check if they are side by side
        if total_distance != direction_mult_by_length:
            return False

        i = 0
        for i in range(0, length-1):

            marble1 = marbles[i]
            marble2 = marbles[i+1]

            if not Board.is_inline(marble1, marble2, direction)\
                    or self.get_tile_value(marble1) != piece_type\
                    or self.get_tile_value(marble2) != piece_type:
                return False

        return True


if __name__ == "__main__":
    board = Board()

    # TEST 4
    # board.set_tile(PieceType.BLACK, ("B", 4))
    # board.set_tile(PieceType.BLACK, ("C", 4))
    # board.set_tile(PieceType.BLACK, ("D", 2))
    # board.set_tile(PieceType.BLACK, ("D", 3))
    # board.set_tile(PieceType.BLACK, ("D", 4))
    # board.set_tile(PieceType.BLACK, ("D", 5))
    # board.set_tile(PieceType.BLACK, ("E", 4))
    # board.set_tile(PieceType.BLACK, ("E", 5))
    # board.set_tile(PieceType.BLACK, ("E", 6))
    # board.set_tile(PieceType.BLACK, ("F", 4))
    # board.set_tile(PieceType.BLACK, ("F", 5))
    # board.set_tile(PieceType.BLACK, ("G", 4))
    # board.set_tile(PieceType.BLACK, ("G", 5))
    #
    # board.set_tile(PieceType.WHITE, ("A", 1))
    # board.set_tile(PieceType.WHITE, ("B", 2))
    # board.set_tile(PieceType.WHITE, ("B", 3))
    # board.set_tile(PieceType.WHITE, ("C", 2))
    # board.set_tile(PieceType.WHITE, ("C", 3))
    # board.set_tile(PieceType.WHITE, ("C", 5))
    # board.set_tile(PieceType.WHITE, ("D", 6))
    # board.set_tile(PieceType.WHITE, ("E", 3))
    # board.set_tile(PieceType.WHITE, ("F", 3))
    # board.set_tile(PieceType.WHITE, ("F", 6))
    # board.set_tile(PieceType.WHITE, ("G", 3))
    # board.set_tile(PieceType.WHITE, ("G", 6))
    # board.set_tile(PieceType.WHITE, ("G", 7))
    # board.set_tile(PieceType.WHITE, ("H", 6))
    #
    # print(board)

    # For the testing of heuristics

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print("Board Two: Testing the D to E problem")
    # print(InitialBoardState.EMPTY.value)

    board2 = Board(InitialBoardState.EMPTY)
    board2.set_tile(PieceType.WHITE, ("D", 5))
    board2.set_tile(PieceType.BLACK, ("F", 8))
    print(board2)
    board2.move_piece(MoveDirection.UL, (("D", 5),))
    board2.move_piece(MoveDirection.DL, (("F", 8),))
    print(board2)
    board2.move_piece(MoveDirection.UL, (("E", 5),))
    board2.move_piece(MoveDirection.DL, (("E", 7),))
    print(board2)
    # board2.move_piece(MoveDirection.UL, (("F", 5),))
    # print(board2)

    # board2 = Board(board=board)
    # board.move_piece(MoveDirection.UL, (("I", 9), ("H", 9)))
    # print(board2)

    # print(board.is_valid_column((Board.position_to_index(("A", 1)),
    #                              Board.position_to_index(("A", 3)),
    #                              Board.position_to_index(("A", 5)))))
    #
    # print(board.is_valid_column((Board.position_to_index(("F", 4)),
    #                              Board.position_to_index(("F", 5)),
    #                              Board.position_to_index(("F", 6)))))
    # #
    # # print(board.is_valid_column((Board.position_to_index(("F", 3)),
    # #                              Board.position_to_index(("F", 4)),
    # #                              Board.position_to_index(("F", 5)))))
    # #
    # print(board.is_valid_column((Board.position_to_index(("I", 9)),
    #                              Board.position_to_index(("H", 9)))))

    # print("Out of order selection (ie [A1 A3 A2], [A2 A3 A1]): ")
    # print(board.is_valid_column((Board.position_to_index(("I", 5)),
    #                              Board.position_to_index(("G", 3)),
    #                              Board.position_to_index(("H", 4)))))
    #
    # print(board.is_valid_column((Board.position_to_index(("H", 4)),
    #                              Board.position_to_index(("G", 3)),
    #                              Board.position_to_index(("I", 5)))))
    #
    # print("In order selection (ie [A1 A2 A3], [A3 A2 A1]): ")
    # print(board.is_valid_column((Board.position_to_index(("I", 5)),
    #                              Board.position_to_index(("H", 4)),
    #                              Board.position_to_index(("G", 3)))))
    #
    # print(board.is_valid_column((Board.position_to_index(("G", 3)),
    #                              Board.position_to_index(("H", 4)),
    #                              Board.position_to_index(("I", 5)))))

    # board.move_piece(MoveDirection.R, (("I", 8),))
    # Testing index_to_position() and position_to_index()
    # print(Board.position_to_index(("A", 1)))

    # Testing position_difference()
    # print(Board.position_difference(Board.position_to_index(("A", 1)), Board.position_to_index(("B", 5))))

    # print(ord("A"))
    #
    # print(Board.index_to_position((8,)))

    # print(b.get_tiles())

    # default = Board(InitialBoardState.DEFAULT)
    # print(default)
    #
    # belgian = Board(InitialBoardState.BELGIAN)
    # print(belgian)
    #
    # german = Board(InitialBoardState.GERMAN)
    # print(german)