from enum import Enum


class PieceType(Enum):
    """
    Uses booleans to keep track of which player is which on the board.

    EMPTY in the case that a board space is occupied by neither WHITE or BLACK
    """
    WHITE = W = True
    BLACK = B = False
    EMPTY = E = None


class MoveDirection(Enum):
    """
    Directions used for moving a piece

    The values for each enum are mapped to the vector of movement

    The first value is the change in the Y axis (A..I)
    The second value is the change in the X axis (0..9)
    """
    DOWN_LEFT = DL = (-1, -1)
    DOWN_RIGHT = DR = (-1, 0)
    LEFT = L = (0, -1)
    RIGHT = R = (0, 1)
    UP_LEFT = UL = (1, 0)
    UP_RIGHT = UR = (1, 1)


class GameMode(Enum):
    HumanVsPC = 1
    PCVsPC = 2
    HumanVsHuman = 3


class PlayerType(Enum):

    HUMAN = 1
    PC = 2


class InitialBoardState(Enum):
    """
    Stores each possible starting board state
    """
    EMPTY = [
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value],
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value],
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value]
    ]

    DEFAULT = [
        [PieceType.W.value, PieceType.W.value, PieceType.W.value, PieceType.W.value, PieceType.W.value],
        [PieceType.W.value, PieceType.W.value, PieceType.W.value, PieceType.W.value, PieceType.W.value,
         PieceType.W.value],
        [PieceType.E.value, PieceType.E.value, PieceType.W.value, PieceType.W.value, PieceType.W.value,
         PieceType.E.value, PieceType.E.value],
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value],
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value],
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value],
        [PieceType.E.value, PieceType.E.value, PieceType.B.value, PieceType.B.value, PieceType.B.value,
         PieceType.E.value, PieceType.E.value],
        [PieceType.B.value, PieceType.B.value, PieceType.B.value, PieceType.B.value, PieceType.B.value,
         PieceType.B.value],
        [PieceType.B.value, PieceType.B.value, PieceType.B.value, PieceType.B.value, PieceType.B.value]
    ]

    BELGIAN = [
        [PieceType.W.value, PieceType.W.value, PieceType.E.value, PieceType.B.value, PieceType.B.value],
        [PieceType.W.value, PieceType.W.value, PieceType.W.value, PieceType.B.value, PieceType.B.value,
         PieceType.B.value],

        [PieceType.E.value, PieceType.W.value, PieceType.W.value, PieceType.E.value, PieceType.B.value,
         PieceType.B.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.B.value, PieceType.B.value, PieceType.E.value, PieceType.W.value,
         PieceType.W.value, PieceType.E.value],

        [PieceType.B.value, PieceType.B.value, PieceType.B.value, PieceType.W.value, PieceType.W.value,
         PieceType.W.value],
        [PieceType.B.value, PieceType.B.value, PieceType.E.value, PieceType.W.value, PieceType.W.value]
    ]

    GERMAN = [
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value],
        [PieceType.W.value, PieceType.W.value, PieceType.E.value, PieceType.E.value, PieceType.B.value,
         PieceType.B.value],

        [PieceType.W.value, PieceType.W.value, PieceType.W.value, PieceType.E.value, PieceType.B.value,
         PieceType.B.value, PieceType.B.value],

        [PieceType.E.value, PieceType.W.value, PieceType.W.value, PieceType.E.value, PieceType.E.value,
         PieceType.B.value, PieceType.B.value, PieceType.E.value],

        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value,
         PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value],

        [PieceType.E.value, PieceType.B.value, PieceType.B.value, PieceType.E.value, PieceType.E.value,
         PieceType.W.value, PieceType.W.value, PieceType.E.value],

        [PieceType.B.value, PieceType.B.value, PieceType.B.value, PieceType.E.value, PieceType.W.value,
         PieceType.W.value, PieceType.W.value],

        [PieceType.B.value, PieceType.B.value, PieceType.E.value, PieceType.E.value, PieceType.W.value,
         PieceType.W.value],
        [PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value, PieceType.E.value]
    ]


class HeuristicWeight(Enum):
    """
    Enum for the weight of the heuristics as well as supporting values
    """
    WIN_WEIGHT = 4096
    PIECE_WEIGHT = 150
    GROUP_WEIGHT = (0, 1, 2)
    DISTANCE_WEIGHT = (4, 3, 2, 1, 0)
    DISTANCE_TILE_ARRAY = [
        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[3],
         DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2],
         DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1],
         DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[0],
         DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1],
         DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2],
         DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[3], DISTANCE_WEIGHT[3],
         DISTANCE_WEIGHT[4]],

        [DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4], DISTANCE_WEIGHT[4]]
    ]
    ENEMY_DISTANCE_TILE_ARRAY = [
        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1],
         DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2],
         DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1],
         DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[0],
         DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1],
         DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2], DISTANCE_WEIGHT[2],
         DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1], DISTANCE_WEIGHT[1],
         DISTANCE_WEIGHT[0] * 2],

        [DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2, DISTANCE_WEIGHT[0] * 2]
    ]


if __name__ == '__main__':
    print(InitialBoardState.DEFAULT.value)
