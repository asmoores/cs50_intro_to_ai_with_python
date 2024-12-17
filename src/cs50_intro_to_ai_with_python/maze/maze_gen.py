import random
from collections import deque


def generate_maze(width, height):
    """
    Generates a complex but solvable maze using an iterative depth-first search approach.
    Ensures the goal 'B' is placed at the farthest reachable cell from the start 'A'.
    """
    maze = [["#" for _ in range(width)] for _ in range(height)]

    # Define start position
    start = (0, 0)
    maze[start[0]][start[1]] = "A"

    # Stack for iterative DFS
    stack = [start]
    visited = set()
    visited.add(start)

    def neighbors(cx, cy):
        """Returns all unvisited neighbors two cells away."""
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        result = []
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < height and 0 <= ny < width and (nx, ny) not in visited:
                result.append((nx, ny))
        return result

    # Track the farthest cell from the start
    farthest_cell = start

    # Carve out the maze
    while stack:
        cx, cy = stack[-1]
        unvisited_neighbors = neighbors(cx, cy)

        if unvisited_neighbors:
            # Choose a random unvisited neighbor
            nx, ny = random.choice(unvisited_neighbors)

            # Carve a path
            maze[(cx + nx) // 2][(cy + ny) // 2] = " "
            maze[nx][ny] = " "
            visited.add((nx, ny))
            stack.append((nx, ny))

            # Update the farthest cell
            farthest_cell = (nx, ny)
        else:
            stack.pop()

    # Place the goal 'B' at the farthest reachable cell
    maze[farthest_cell[0]][farthest_cell[1]] = "B"

    return maze


def save_maze_to_file(maze, filename):
    """Saves the maze to a text file."""
    with open(filename, "w") as file:
        for row in maze:
            file.write("".join(row) + "\n")


if __name__ == "__main__":
    width = 100
    height = 30

    # Generate the maze
    maze = generate_maze(width, height)

    # Save the maze to a file
    filename = "solvable_maze.txt"
    save_maze_to_file(maze, filename)

    print(f"100x100 solvable maze generated and saved to '{filename}'")
