import pygame
import heapq
import numpy as np

GRID_SIZE = 50
TILE_SIZE = 15
SCREEN_SIZE = GRID_SIZE * TILE_SIZE

PLAYER_COLOR = (0, 255, 0)
BOT_COLOR = (255, 0, 0)
WALL_COLOR = (0, 0, 0)
GRID_COLOR = (150, 150, 150)
BG_COLOR = (220, 220, 220)
FPS = 10

maze = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

for i in range(15, 35):
    maze[i, 25] = 1

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Maze Chase Game")
clock = pygame.time.Clock()

player_pos = (1, 1)
bot1_pos = (0, 48)
bot2_pos = (48, 0)

bot1_path_cache = []
bot2_path_cache = []

key_map = {pygame.K_w: (-1, 0), pygame.K_s: (1, 0), pygame.K_a: (0, -1), pygame.K_d: (0, 1)}

DIRECTIONS = [
    (-1, 0), (1, 0), (0, -1), (0, 1),  
    (-1, -1), (-1, 1), (1, -1), (1, 1)  
]

def draw_grid():
    """ Draws the maze, player, bots, and grid lines """
    screen.fill(BG_COLOR)

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if maze[x, y] == 1:
                pygame.draw.rect(screen, WALL_COLOR, (y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for x in range(0, SCREEN_SIZE, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_SIZE))
        pygame.draw.line(screen, GRID_COLOR, (0, x), (SCREEN_SIZE, x))

    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[1] * TILE_SIZE, player_pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, BOT_COLOR, (bot1_pos[1] * TILE_SIZE, bot1_pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, BOT_COLOR, (bot2_pos[1] * TILE_SIZE, bot2_pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()

def a_star(start, goal):
    def heuristic(a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return (dx + dy) + (1.414 - 2) * min(dx, dy)  

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

        for dx, dy in DIRECTIONS:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and maze[neighbor] == 0:
                temp_g_score = g_score[current] + (1.414 if dx != 0 and dy != 0 else 1) 
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []

def move_player(event):
    global player_pos, bot1_path_cache, bot2_path_cache
    if event.key in key_map:
        dx, dy = key_map[event.key]
        new_pos = (player_pos[0] + dx, player_pos[1] + dy)
        if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE and maze[new_pos] == 0:
            player_pos = new_pos
            bot1_path_cache = a_star(bot1_pos, player_pos) 
            bot2_path_cache = a_star(bot2_pos, player_pos)
            return True
    return False

def move_bots():
    global bot1_pos, bot2_pos

    if bot1_path_cache:
        next_step = bot1_path_cache.pop(0)
        if maze[next_step] == 0 and next_step != bot2_pos:  
            bot1_pos = next_step

    if bot2_path_cache:
        next_step = bot2_path_cache.pop(0)
        if maze[next_step] == 0 and next_step != bot1_pos: 
            bot2_pos = next_step

    if bot1_pos == player_pos or bot2_pos == player_pos:
        print("Game Over! Player caught!")
        pygame.quit()
        exit()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if move_player(event):
                move_bots()

    draw_grid()
    clock.tick(FPS)

pygame.quit()
