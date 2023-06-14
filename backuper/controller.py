import abc


class Controller(abc.ABC):
    @abc.abstractmethod
    def should_continue(self): ...


class InfiniteController(Controller):
    def should_continue(self):
        return True


class FiniteController(Controller):
    def __init__(self, max_iterations: int):
        self._max_iterations = max_iterations
        self._iterations = 0

    def should_continue(self):
        self._iterations += 1
        return self._iterations < self._max_iterations + 1
