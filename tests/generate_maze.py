import random

# Set up the maze dimensions
width, height = 101, 101
start, end = 'A', 'B'


def generate_maze(width=81, height=51, complexity=.75, density=.75):
    # Adjust complexity and density relative to maze size
    complexity = int(complexity * (5 * (height + width)))  # number of components
    density = int(density * ((height // 2) * (width // 2)))  # size of components
    # Build actual maze
    Z = [['#'] * width + ['#'] for _ in range(height)] + [['#'] * (width + 1)]
    # Fill borders
    Z[0] = Z[-1] = ['#'] * (width + 1)
    # Make aisles
    for _ in range(density):
        x, y = random.randint(0, width // 2) * 2, random.randint(0, height // 2) * 2  # pick a random position
        Z[y][x] = ' '
        for _ in range(complexity):
            neighbours = []
            if x > 1:             neighbours.append(((y, x - 2)))
            if x < width - 2:     neighbours.append(((y, x + 2)))
            if y > 1:             neighbours.append(((y - 2, x)))
            if y < height - 2:    neighbours.append(((y + 2, x)))
            if len(neighbours):
                y_, x_ = neighbours[random.randint(0, len(neighbours) - 1)]
                if Z[y_][x_] == '#':
                    Z[y_][x_] = ' '
                    Z[y_ + (y - y_) // 2][x_ + (x - x_) // 2] = ' '
                    x, y = x_, y_
    return Z


# Generate maze and place start and end points
maze = generate_maze(width, height)
maze[1][1] = start
maze[-3][-3] = end

# Print the maze
for row in maze:
    print(''.join(row[:width]))
