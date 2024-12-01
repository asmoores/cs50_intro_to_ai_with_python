import pytest
import io

from src.cs50_intro_to_ai_with_python.maze.maze import Maze


class TestMaze:
    @pytest.fixture
    def maze(self):
        return Maze("tests/test_files/maze1.txt")

    def test_init(self, maze):
        assert maze.height == 10
        assert maze.width == 10
        assert maze.start == (9, 0)
        assert maze.goal == (0, 5)

    def test_maze_solves_correctly(self, maze):
        maze.solve()
        solution_actions, solution_cells = maze.solution
        assert solution_actions[0] == "up"
        assert solution_cells[0] == (8, 0)
        assert solution_actions[-1] == "up"
        assert solution_cells[-1] == (0, 5)

    def test_neighbors(self, maze):
        neighbors = maze.neighbors((9, 0))
        expected_neighbors = [("up", (8, 0))]
        assert neighbors == expected_neighbors

    @pytest.fixture
    def simple_maze(self):
        maze_layout = """
        ##########
        #A       #
        #  ####  #
        #        #
        #  ####  #
        #     B  #
        ##########
        """
        return maze_layout.strip()

    @pytest.fixture
    def maze_with_no_start_point(self):
        maze_layout = """
        ##########
        #        #
        #  ####  #
        #        #
        #  ####  #
        #     B  #
        ##########
        """
        return maze_layout.strip()

    @pytest.fixture
    def maze_with_no_end_point(self):
        maze_layout = """
        ##########
        #A       #
        #  ####  #
        #        #
        #  ####  #
        #        #
        ##########
        """
        return maze_layout.strip()

    @pytest.fixture
    def maze_with_two_start_points(self):
        maze_layout = """
        ##########
        #A       #
        #  ####  #
        #       A#
        #  ####  #
        #     B  #
        ##########
        """
        return maze_layout.strip()

    @pytest.fixture
    def maze_with_two_end_points(self):
        maze_layout = """
        ##########
        #A       #
        #  ####  #
        #   B    #
        #  ####  #
        #     B  #
        ##########
        """
        return maze_layout.strip()

    @pytest.mark.parametrize(
        "maze_input, exception_message",
        [
            ("maze_with_no_start_point", "maze must have exactly one start point"),
            ("maze_with_no_end_point", "maze must have exactly one goal"),
            ("maze_with_two_start_points", "maze must have exactly one start point"),
            ("maze_with_two_end_points", "maze must have exactly one goal"),
        ],
    )
    def test_maze_init_raises_exception_for_invalid_input(
        self, request, monkeypatch, maze_input, exception_message
    ):
        maze_input = request.getfixturevalue(maze_input)
        monkeypatch.setattr("builtins.open", lambda x, y="r": io.StringIO(maze_input))
        with pytest.raises(Exception, match=exception_message):
            Maze("../test_files/maze1.txt")

    def test_maze_solve_exists(self, monkeypatch):
        monkeypatch.setattr("builtins.open", lambda x, y="r": io.StringIO("A  B"))
        maze = Maze("../test_files/maze1.txt")
        maze.solve()
        assert maze.solution is not None

    def test_maze_neighbors_exists(self, monkeypatch):
        monkeypatch.setattr("builtins.open", lambda x, y="r": io.StringIO("A  B"))
        maze = Maze("../test_files/maze1.txt")
        neighbors = maze.neighbors(maze.start)
        assert isinstance(neighbors, list)
