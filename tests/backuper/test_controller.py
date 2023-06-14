from backuper.controller import InfiniteController, FiniteController


def test_infinite_controller_should_continue():
    controller = InfiniteController()
    for _ in range(100):
        assert controller.should_continue()


def test_finite_controller_should_continue():
    max_iterations = 5
    controller = FiniteController(max_iterations)
    for _ in range(max_iterations):
        assert controller.should_continue()
    assert not controller.should_continue()
