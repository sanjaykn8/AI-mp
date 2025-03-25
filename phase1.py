import pygame
import heapq
import numpy as np

GRID_SIZE = 50   # Changed from 100 to 50
TILE_SIZE = 10   # Fits well on screen
SCREEN_SIZE = GRID_SIZE * TILE_SIZE

PLAYER_COLOR = (0, 255, 0)   # Green
BOT_COLOR = (255, 0, 0)      # Red
WALL_COLOR = (0, 0, 0)       # Black
GRID_COLOR = (150, 150, 150) # Light Grey Grid
BG_COLOR = (220, 220, 220)   # Slightly darker grey for contrast
FPS = 10  

# 50x50 empty maze (all paths open)
maze = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

# Adding some walls for testing
for i in range(15, 35):
    maze[i, 25] = 1  # Vertical wall in the middle

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Maze Chase Game")
clock = pygame.time.Clock()

# Player & Bots Initial Positions
player_pos = (1, 1)
bot1_pos = (0, 48)
bot2_pos = (48, 0)

# Movement keys
key_map = {pygame.K_w: (-1, 0), pygame.K_s: (1, 0), pygame.K_a: (0, -1), pygame.K_d: (0, 1)}

def draw_grid():
    """ Draws the maze, player, bots, and grid lines """
    screen.fill(BG_COLOR)

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if maze[x, y] == 1:
                pygame.draw.rect(screen, WALL_COLOR, (y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw grid lines
    for x in range(0, SCREEN_SIZE, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_SIZE))
        pygame.draw.line(screen, GRID_COLOR, (0, x), (SCREEN_SIZE, x))

    # Draw player and bots **after** grid and walls
    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[1] * TILE_SIZE, player_pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, BOT_COLOR, (bot1_pos[1] * TILE_SIZE, bot1_pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, BOT_COLOR, (bot2_pos[1] * TILE_SIZE, bot2_pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()

def a_star(start, goal):
    """ A* Pathfinding Algorithm """
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_list = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_list:
        _, current = heapq.heappop(open_list)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and maze[neighbor] == 0:
                temp_g_score = g_score[current] + 1
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []

def move_player(event):
    """ Moves the player based on keypress """
    global player_pos
    if event.key in key_map:
        dx, dy = key_map[event.key]
        new_pos = (player_pos[0] + dx, player_pos[1] + dy)
        if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE and maze[new_pos] == 0:
            player_pos = new_pos
            return True
    return False

def move_bots():
    """ Moves bots using A* pathfinding """
    global bot1_pos, bot2_pos
    bot1_path = a_star(bot1_pos, player_pos)
    bot2_path = a_star(bot2_pos, player_pos)

    if bot1_path:
        bot1_pos = bot1_path[0]  # Move bot1 one step
    if bot2_path:
        bot2_pos = bot2_path[0]  # Move bot2 one step

    if bot1_pos == player_pos or bot2_pos == player_pos:
        print("Game Over! Player caught!")
        pygame.quit()
        exit()

# Main Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if move_player(event):  # Move player first, then bots
                move_bots()

    draw_grid()
    clock.tick(FPS)

pygame.quit()
