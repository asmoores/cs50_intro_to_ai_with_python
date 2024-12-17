import sys
import logging
import time
from pprint import pformat, pprint

from PIL import Image, ImageDraw
from abc import (
    ABC,
    abstractmethod,
)  # ABC is a package that provides abstract base classes.

from src.cs50_intro_to_ai_with_python.maze.error_messages import (
    EXACTLY_ONE_START_POINT,
    EXACTLY_ONE_GOAL,
    NO_SOLUTION,
    EMPTY_FRONTIER,
)

from src.cs50_intro_to_ai_with_python.directions import Direction

UP, DOWN, LEFT, RIGHT = Direction

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Node:
    """
    In search algorithms nodes represent the individual states that are explored during the search process.  A node
    is a fundamental unit in search algorithms and encapsulated information about a particular state in the search space.

    Attributes:
          state: a tuple representing the position of the node in search space.  In this case it is a position within
          a maze.
          parent: The parent, or preceding, node in the search tree.  A Node can have only one parent but can be the
          parent of many node.
          action:  a List of possible actions, or moves, that can be taken from this state.

    """

    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

    def __repr__(self):
        return f"Node(state={self.state}, parent={repr(self.parent)}, action={self.action})"


class Frontier(ABC):
    """
    Abstract base class for frontiers.
    Inherits from ABC to mark it as an abstract class and allow the use of the @abstractmethod decorator. If the class
    did not inherit from ABC then the @abstractmethod decorator would not be honoured.

    This class is used to represent the frontier of the search algorithm, i.e. the next nodes to be explored.
    """

    def __init__(self):
        self.frontier = []

    def log_attributes(self):
        logging.info("%s attributes: %s", self.__class__.__name__, pformat(vars(self)))

    def __repr__(self):
        # Define a meaningful representation for the object
        logging.info("Node attributes: %s", pformat(vars(self)))
        return f"Node({vars(self)})"

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def add(self, node):
        self.frontier.append(node)

    @abstractmethod
    def remove(self):
        """
        Remove and return a node from the frontier. Subclasses must implement this function and the implementation
        will determine whether the search is breadth first or depth first.
        """
        pass


class StackFrontier(Frontier):
    """
    Implements depth first search.
    """

    def remove(self):
        if self.empty():
            raise Exception(EMPTY_FRONTIER)
        else:
            node = self.frontier.pop()
            return node


class QueueFrontier(Frontier):
    """
    Implements breadth first search.
    """

    def remove(self):
        if self.empty():
            raise Exception(EMPTY_FRONTIER)
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


class Maze:
    """Represents the search space."""

    def __init__(self, filename):
        self.explored = None
        self.num_of_states_explored = None

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("%s" % EXACTLY_ONE_START_POINT)
        if contents.count("B") != 1:
            raise Exception(EXACTLY_ONE_GOAL)

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self._setup_walls(contents)
        self.solution = None
        self.explored = set()

    def _setup_walls(self, contents):
        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

    def neighbors(self, state):
        row, col = state
        candidates = [
            (UP, (row - 1, col)),
            (DOWN, (row + 1, col)),
            (LEFT, (row, col - 1)),
            (RIGHT, (row, col + 1)),
        ]

        result = []
        for action, (r, c) in candidates:
            #            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
            if self._can_visit(r, c):
                result.append((action, (r, c)))
        return result

    def _is_within_bounds(self, r, c):
        """Check if (r, c) is within the maze."""
        return 0 <= r < self.height and 0 <= c < self.width

    def _is_not_a_wall(self, r, c):
        return not self.walls[r][c]

    def _can_visit(self, r, c):
        return self._is_within_bounds(r, c) and self._is_not_a_wall(r, c)

    def print_initial_maze(self):
        """Print the maze initially."""
        print("\nInitial Maze:")
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                else:
                    print(" ", end="")
            print()

    def update_explored_node(self, state):
        """
        Update a single explored node using ANSI escape codes to avoid redrawing the entire maze.
        """
        row, col = state
        if state != self.start and state != self.goal:  # Skip 'A' and 'B'
            print(f"\033[{row + 5};{col + 1}H*", end="", flush=True)

    def solve(self):
        """Finds a solution to maze, if one exists."""

        logging.info("Solving maze")

        # Keep track of number of states explored
        self.num_of_states_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        # logging.info(f"Adding {start.state} with {start.action}")
        frontier = StackFrontier()  # StackFrontier QueueFrontier
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        self.print_initial_maze()
        print("\nExploring maze...\n")

        try:
            print("\033[?25l", end="", flush=True)
            time.sleep(1)  # Pause for

            # Keep looping until solution found
            while True:
                # If nothing left in frontier, then no path
                if frontier.empty():
                    raise Exception(NO_SOLUTION)

                # Extract the next node in the frontier to be examined
                node = frontier.remove()
                # logging.info(f"Checking {node.state}")

                self.explored.add(node.state)
                self.update_explored_node(node.state)  # Update only the current node
                time.sleep(0.1)  # Pause for

                self.num_of_states_explored += 1

                if node.state == self.goal:
                    self._create_solution(node)
                    break

                for action, state in self.neighbors(node.state):
                    if (
                        not frontier.contains_state(state)
                        and state not in self.explored
                    ):
                        frontier.add(Node(state=state, parent=node, action=action))
        finally:
            print("\033[?25h", end="", flush=True)
            print(f"\033[{self.height + 29};1H", end="", flush=True)

            # Mark node as explored
            # self.explored.add(node.state)
            # # logging.info(f"Adding {node.state} to explored")
            # self._add_neighbours_to_frontier(frontier, node)
            # for idx, node in enumerate(frontier.frontier):
            #     print(f"Node {idx + 1}:")
            #     pprint(vars(node), width=1)  # Use vars() to access all attributes
            #     print()  # Add spacing between nodes

    def _create_solution(self, node):
        actions = []
        cells = []
        while node.parent is not None:
            actions.append(node.action)
            cells.append(node.state)
            node = node.parent
        actions.reverse()
        cells.reverse()
        self.solution = (actions, cells)

    def _add_neighbours_to_frontier(self, frontier, node):
        for action, state in self.neighbors(node.state):
            if not frontier.contains_state(state) and state not in self.explored:
                child = Node(state=state, parent=node, action=action)
                frontier.add(child)

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def output_image(self, filename, show_solution=True, show_explored=False):
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA", (self.width * cell_size, self.height * cell_size), "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    (
                        [
                            (j * cell_size + cell_border, i * cell_size + cell_border),
                            (
                                (j + 1) * cell_size - cell_border,
                                (i + 1) * cell_size - cell_border,
                            ),
                        ]
                    ),
                    fill=fill,
                )

        img.save(filename)


if __name__ == "__main__":
    # If no arg passed use default file.
    if len(sys.argv) != 2:
        maze_file = "maze1.txt"
    else:
        maze_file = sys.argv[1]

    m = Maze(maze_file)
    # print("Maze:")
    # m.print()
    # print("Solving...")
    m.solve()
    # print("States Explored:", m.num_of_states_explored)
    # print("Solution:")
    # m.print()
    # m.output_image("maze.png", show_explored=True)
