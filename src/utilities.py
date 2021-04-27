import time

from enums import PieceType
from exceptions import ClockError


def gen_move_numbers(start=1, stop=1000):
    """
    Generator for numbers from start (default 1) to stop (def 1000).
    Used to get next move #. I.e. will get move 1 -> do stuff, then move 2-> gets 2
    :param start:
    :param stop:
    :return:
    """
    yield from (x for x in range(start, stop))


class MoveHistory:
    def __init__(self, history=None):
        if history is None:
            self._history = []
        else:
            self._history = history

    @property
    def history(self):
        return self._history

    def get_move(self, index):
        """
        Gets the move info from history
        :param index: index of move
        :return:
        """
        return self._history[index]

    def get_last_move(self):
        return self._history[-1]

    def add_move(self, move_info):
        """
        Records move into move_history
        :param move_info: MoveInfo object
        """
        self._history.append(move_info)

    def remove_move_from_history(self, index):
        """
        Removes move from history
        :param index: int
        :return: move
        """
        return self._history.pop(index)  # returns None if key doesn't exist

    def remove_last_move(self):
        """
        Removes last move from history
        """
        return self._history.pop()

    def print_move_history(self):
        """
        Prints key and valus of move history
        """
        for move in self._history:
            print(move)

    def clear_move_history(self):
        """
        Clears move history
        """
        self._history.clear()

    def get_last_x_moves(self, last_x):
        moves = self._history[-last_x:]
        return moves

    def get_amount_of_moves(self):
        return len(self._history)


class MoveInfo:
    """
    Just a class to instantiate and represent a move info.
    """
    def __init__(self, from_pos, to_pos, move_type, time_taken, sumito=False, color=PieceType.BLACK):
        self._color = color
        self._from_pos = from_pos
        self._move_type = move_type
        self._to_pos = to_pos
        self._time = time_taken
        self._did_sumito = sumito

    def get_as_history_format(self):
        time_str = ""
        if self._time is None:  # Set time properly if None, or format to 2 decimal places
            time_str = "None"
        else:
            time_str = str(round(self._time,2)) + "s"
        return f"{self._from_pos} to {self._to_pos} {time_str}"

    @property
    def time(self):
        return self._time


class Clock:
    """
    Game clock to store all clock related items. All time is in time seconds (float).
    Includes keeping track of game time related things and timer-type capabilities
    """

    def __init__(self):
        self._time_log = {}
        self._timer_start = None
        self._timer_stop = None
        self._timer_elapsed_time = None
        self._game_start = None
        self._game_end = None
        self.game_time_limit = None  # misread, probably don't need this
        self.move_time_limit = None  # Might move this elsewhere
        self._time_game_ends = None

    @property
    def move_time_limit(self):
        """
        Time limit for moves, to be implemented later if necessary
        :return:
        """
        return self._move_limit

    @move_time_limit.setter
    def move_time_limit(self, value):
        self._move_limit = value

    @property
    def game_end(self):
        """
        Time game ends
        :return: a float
        """
        return self._game_end

    @property
    def game_time_limit(self):
        """
        Get game time limit
        :return:
        """
        return self._game_time_limit

    @game_time_limit.setter
    def game_time_limit(self, limit):
        """
        Sets game time limit
        :param limit: a float
        """
        self._game_time_limit = limit

    @property
    def game_start(self):
        """
        Getter for game start time
        :return:
        """
        return self._game_start

    @game_start.setter
    def game_start(self, start_time):
        """
        Setter for game start time if specific
        :param start_time:
        :return:
        """
        self._game_start = start_time

    @property
    def time_game_ends(self):
        """
        Getter for time game ends, if not set, calculate it
        :return: a float
        """
        if self._time_game_ends is None:
            self._set_time_game_ends()
        return self._time_game_ends

    def _set_time_game_ends(self):
        """
        Helper method to set when game time ends, raises clock errors if none set
        :return:
        """
        if self._game_start is None:
            raise ClockError("Game has not started yet, can't calculate when the time limit is up")
        elif self._game_time_limit is None:
            raise ClockError("No time limit has been set, can't calculate when time limit is up")
        self._time_game_ends = self.game_start + self.game_time_limit

    def has_move_time_expired(self):
        """
        Returns if time so far has exceeded move_time_limit
        :return:
        """
        return self.get_time_since_timer_start() > self.move_time_limit

    def get_time_since_timer_start(self):
        """
        Returns time since timer start
        :return:
        """
        return time.perf_counter() - self._timer_start

    def has_game_time_expired(self):
        """
        Returns if the game time has expired, in comparison to when the game started
        :return:
        """
        return self.get_time_since_game_start() > self._game_time_limit

    def start_game_time(self):
        """
        Sets game time to now
        """
        self._game_start = time.time()

    def stop_game_time(self):
        """
        Sets game end time
        """
        self._game_end = time.time()

    def get_time_since_game_start(self):
        """
        Returns time since game start
        :return: a float
        """
        return time.time() - self.game_start

    def get_game_duration(self):
        return self._game_end - self._game_start

    def start_time(self):
        """
        Sets start time
        """
        self._timer_start = time.perf_counter()

    def stop_timer(self):
        """
        Sets stop time
        """
        if self._timer_start is None:
            raise ClockError("There is no start time, can't stop clock")

        self._timer_stop = time.perf_counter()

    def reset_timer(self):
        self._timer_start = None
        self._timer_stop = None
        self._timer_elapsed_time = None

    def get_elapsed_time(self):
        """
        Gets elapsed time of clock, raises ClockError if missing values.
        :return: float , elapsed time
        """
        if self._timer_start is None or self._timer_stop is None:
            raise ClockError("Missing a start or stop time")

        self._set_elapsed_time()
        return self._timer_elapsed_time

    def _set_elapsed_time(self):
        self._timer_elapsed_time = self._timer_stop - self._timer_start

    def print_elapsed_time(self):
        print(f"Elapsed time {self._timer_elapsed_time:0.2f} seconds")

    def add_logs_to_time_log(self, dict):
        """
        Adds dictionary of log times to existing log
        :param dict: dictionry of log times
        """
        self._time_log.update(dict)

    def add_to_time_log(self, name, amount_time):
        """
        Add key and value pair to time log
        :param name: string, name of event/instance to capture as key
        :param amount_time: float or int, amount of time for name instance
        """
        self._time_log.update({name: amount_time})

    def remove_event_from_log(self, name):
        """
        Removes key from time log, returns None if not found
        :param name: key to remove
        :return: value of key if found, else None
        """
        return self._time_log.pop(name, None)

    def print_time_log(self):
        for k, v in self._time_log.items():
            print(f"Event {k} took {v} seconds")

    def clear_log(self):
        """
        Clears time log
        :return:
        """
        self._time_log = {}

    @staticmethod
    def calculate_time_difference(end, start):
        """
        static method to get difference between two times
        :param end:
        :param start:
        :return: difference
        """
        return end - start

    @staticmethod
    def get_current_time():
        """
        Returns current time in epoch seconds
        :return:
        """
        return time.time()

    @staticmethod
    def convert_minutes_to_seconds(minutes):
        """
        Converts minutes to seconds
        :param minutes: int or float
        :return: a float
        """
        return minutes * 60.0

    @staticmethod
    def convert_seconds_to_minutes(seconds):
        """
        Converts seconds to minutes
        :param seconds: int or float
        :return: a float
        """
        return seconds / 60.0

    @staticmethod
    def seconds_as_clock_time(seconds):
        """
        Returns a formatted string for seconds , in a nice formatted clock time "01:02:56"
        :param seconds: int or float
        :return: a string
        """
        return time.strftime("%H:%M:%S", time.gmtime(seconds))

    def print_game_over_times(self):
        """
        Prints game over statistics
        :return:
        """
        game_end = time.strftime('%H:%M:%S', time.gmtime(self._game_end))
        return self.__str__() + f"\nGame Ended: {game_end}"

    def __str__(self):
        game_start = time.strftime('%H:%M:%S', time.gmtime(self.game_start))
        game_end_limit_time = time.strftime('%H:%M:%S', time.gmtime(self.time_game_ends))
        return f"Game started at: {game_start}\nGame time limit ends at: {game_end_limit_time}"




if __name__ == '__main__':
    # Test code for clock methods
    clock = Clock()
    clock.start_time()
    time.sleep(2)
    clock.stop_timer()
    elapsed = clock.get_elapsed_time()
    clock.print_elapsed_time()

    clock.add_to_time_log("m1", clock.get_elapsed_time())
    clock.add_to_time_log("m2", 5213)
    clock.print_time_log()

    print(clock.remove_event_from_log("m1"))
    print(clock.remove_event_from_log("wrong"))

    # static method tests
    print(Clock.calculate_time_difference(5, 3))
    print(Clock.convert_minutes_to_seconds(5))
    print(Clock.convert_seconds_to_minutes(300))
    print(Clock.seconds_as_clock_time(300))
    print("Time: %f " % Clock.get_current_time())

    ## testing game time stuff
    game_clock = Clock()
    game_clock.game_time_limit = 500
    game_clock.start_game_time()
    print(game_clock.time_game_ends)
    print(game_clock)
    print(game_clock.has_game_time_expired())
    time.sleep(1)
    print(game_clock.get_time_since_game_start())
    game_clock.stop_game_time()
    print(game_clock.print_game_over_times())
