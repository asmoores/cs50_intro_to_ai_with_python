import pytest
import io

from src.cs50_intro_to_ai_with_python.maze.maze import Maze


class TestMazePrint:
    @pytest.fixture
    def maze(self):
        return Maze("tests/test_files/maze2.txt")

    def test_print(self, monkeypatch, maze):
        test_output = io.StringIO()
        monkeypatch.setattr('sys.stdout', test_output)
        maze.print()

        expected_output = """
█A█
█ █
█B█

"""
        assert test_output.getvalue() == expected_output