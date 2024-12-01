import sys

''' ABC is a package that provides abstract base classes.'''
from abc import ABC, abstractmethod


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


class Frontier(ABC):
    """
    Abstract base class for frontiers.
    Inherits from ABC to mark it as an abstract class and allow the use of the @abstractmethod decorator. If the class
    did not inherit from ABC then the @abstractmethod decorator would not be honoured.

    This class is used to represent the frontier of the search algorithm, i.e. the next nodes to be explored.
    """

    def __init__(self):
        self.frontier = []

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
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            # node = self.frontier[-1]
            # self.frontier = self.frontier[:-1]
            node = self.frontier.pop()
            return node


class QueueFrontier(Frontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


class Maze:
    def __init__(self, filename):
        self.explored = None
        self.num_explored = None

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self._setup_walls(contents)
        self.solution = None

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

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1)),
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

    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()  # StackFrontier QueueFrontier
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:
            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = (
                frontier.remove()
            )  # Extract the next node in the frontier to be examined
            self.num_explored += (
                1  # This could be done after checking if we have solved the maze
            )

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw

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
    if len(sys.argv) != 2:
        maze_file = 'maze1.txt'
    else:
        maz_file = sys.argv[1]

    m = Maze(maze_file)
    print("Maze:")
    m.print()
    print("Solving...")
    m.solve()
    print("States Explored:", m.num_explored)
    print("Solution:")
    m.print()
    m.output_image("maze.png", show_explored=True)
