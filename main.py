from typing import List, Tuple
import sys
import time
import pygame
import random
from itertools import product, cycle

fps = 20 # Capped fps of the game

# Widht in pixels of each cell
cell_width = 3

# Size in number of cells of the grid
width, height = (200, 200)

# The size of the screen is derived from the size_per_cell and the number of 
# cells on the board
screen_size = width * cell_width, height * cell_width

# Colors used for no-cell and cell on the creen
GREEN = 50, 200, 50
BLACK = 0, 0, 0

# Memoize the coordinates to improve efficiency
COORDS = list(product(range(width), range(height)))

def make_board(width: int, height: int, randomize: bool = False) -> List[List[int]]:
    """ Our board factory """

    if randomize:
        # Generate a column with either 0 or 1 on its positions and then
        # multriply it `width` times to generate the full board
        new_board = [
            [random.choice([0, 1]) for y in range(height)]
            for x in range(width)
        ]
    else:
        # Generate a column with 0 on its positions and then
        # multriply it `width` times to generate the full board
        new_board = [
            [0 for y in range(height)]
            for x in range(width)
        ]
    return new_board

def get_neighbors(x: int, y: int, board: List[List[int]]) -> int:
    """ Get the number immediate neighbors of the cell at a Manhatan distance of 1 """
    neighbors = 0

    # `delta_x` and `delta_x` will permutate all the possible offsets
    # to the surronding cells with a Manhatan distance of 1
    for delta_x in [-1, 0, 1]:
        for delta_y in [-1, 0, 1]:
            # Generate from the offsets the actual coordinates of the
            # neighbor knowing that the board really has no borders (infinite)
            nx = (x + delta_x) % width
            ny = (y + delta_y) % height
            
            # Incrase the neighbor count if its alive
            if board[nx][ny] == 1: 
                neighbors += 1

    return neighbors

def advance(board: List[List[int]]) -> List[List[int]]:
    """ Tick time forward step and adjust cells accordingly """

    # Create a blank new board (with no randomization)
    new_board = make_board(width, height)

    # Generate the set of all possible coordinates of the screen and iterate them
    # extacting the number of neighbors and state at that position
    for x, y in COORDS: 
        alive_num = get_neighbors(x, y, board)
        state = board[x][y]

        # If a cell is alive and it has 2 or 3 living neighbors, it 
        # stays alive
        if state == 1 and alive_num in [2, 3]: 
            new_board[x][y] = 1

        # If a cell is dead and has 3 living neighbors, it revives
        if state == 0 and alive_num == 3:
            new_board[x][y] = 1

        # Otherwise the cells dies or stays dead (do nothing as the board
        # is zero initialized)

    return new_board

# Initialize pygame and set the display size
pygame.init()
screen = pygame.display.set_mode(screen_size)

# Create the first board (with random cells on it)
board = make_board(width, height, randomize=True)

# Start update/render loop with its state variables
start = time.time()
paused = True
mouse_dragging = False
while 1:
    # Handle events
    for event in pygame.event.get():
        # The enter button with pause or play the game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

        # Drag clicking with the mouse will revive cells on its cursor
        # position (that mechanic is handled later)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_dragging = False

        # Handle program exit
        if event.type == pygame.QUIT:
            sys.exit()

    # Revive cells at mouse pos if is click-dragging
    if mouse_dragging:
        # Get the mouse coord and transform them to board indices
        x, y = pygame.mouse.get_pos()
        col, row = min(x // cell_width, width-1), min(y // cell_width, height-1)

        # Revive the cell at its coords
        board[col][row] = 1

    # Framerate control, only redraw/relogic when 1/fps has passed, 
    # it is not blocking so input events are fluid
    elapsed = time.time() - start
    if elapsed < 1 / fps:
        continue
    start = time.time()

    # Render logic (clean -> advance in logic (if needed) -> draw cells)
    screen.fill(BLACK)
    if not paused:
        board = advance(board)
    for x, y in COORDS:
        # Because the cells are circles generate as its coords the center point
        # if that circle of radious `cell_width/2`
        if board[x][y] == 1:
            coords = ((x + 0.5) * cell_width, (y + 0.5) * cell_width)
            pygame.draw.circle(screen, GREEN, coords, cell_width/2)
    pygame.display.flip()
