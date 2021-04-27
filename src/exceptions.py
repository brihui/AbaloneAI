class InvalidParameterException(Exception):
    """
    Exception for if a function is called with an invalid parameter
    """

    def __init__(self, message):
        super().__init__(message)


class ClockError(Exception):
    """
    Custom exception for any clock errors
    """

    def __init__(self, msg):
        super().__init__(msg)


class CannotMoveException(Exception):
    """
    Exception for if a function is called with an invalid parameter
    """

    def __init__(self):
        super().__init__()
