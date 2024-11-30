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

    def test_solve(self, maze):
        maze.solve()
        solution_actions, solution_cells = maze.solution
        assert solution_actions[0] == "up"
        assert solution_cells[0] == (8, 0)
        assert solution_actions[-1] == "up"
        assert solution_cells[-1] == (0, 5)

    def test_neighbors(self, maze):
        neighbors = maze.neighbors((9, 0))
        expected_neighbors = [('up', (8, 0))]
        assert neighbors == expected_neighbors

    def test_maze_init_multiple_starts(self, monkeypatch):
        monkeypatch.setattr('builtins.open', lambda x, y='r': io.StringIO("AA B"))
        with pytest.raises(Exception):
            Maze("../test_files/maze1.txt")

    def test_maze_init_multiple_goals(self, monkeypatch):
        monkeypatch.setattr('builtins.open', lambda x, y='r': io.StringIO("A BB"))
        with pytest.raises(Exception):
            Maze("../test_files/maze1.txt")

    def test_maze_solve_exists(self, monkeypatch):
        monkeypatch.setattr('builtins.open', lambda x, y='r': io.StringIO("A  B"))
        maze = Maze("../test_files/maze1.txt")
        maze.solve()
        assert maze.solution is not None

    def test_maze_neighbors_exists(self, monkeypatch):
        monkeypatch.setattr('builtins.open', lambda x, y='r': io.StringIO("A  B"))
        maze = Maze("../test_files/maze1.txt")
        neighbors = maze.neighbors(maze.start)
        assert isinstance(neighbors, list)
