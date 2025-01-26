import curses
import math

# Define tile types
FLOOR = '.'
WALL = '#'
ITEM = 'I'
ENEMY = 'E'
PLAYER_ICONS = {
    (0, 1): '>',  # Facing right
    (0, -1): '<',  # Facing left
    (1, 0): 'v',  # Facing down
    (-1, 0): '^'  # Facing up
}

SHADES = " .:-=+*#%@"

def draw_2d_map(stdscr, map_win, game_map, player_pos, player_dir):
    map_win.clear()
    for y, row in enumerate(game_map):
        for x, char in enumerate(row):
            map_win.addch(y, x, char)
    # Draw the player on the 2D map
    player_y, player_x = player_pos
    player_icon = PLAYER_ICONS[tuple(player_dir)]
    map_win.addch(player_y, player_x, player_icon)
    map_win.refresh()

def draw_actions(stdscr, actions_win, actions):
    actions_win.clear()
    for i, action in enumerate(actions):
        actions_win.addstr(i, 0, action)
    actions_win.refresh()

def raytrace(player_pos, player_dir, game_map, max_depth):
    rays = []
    player_y, player_x = player_pos
    for angle in range(-30, 31, 1):  # 60 degree FOV
        ray_angle = math.radians(angle)
        ray_dir = (
            player_dir[0] * math.cos(ray_angle) - player_dir[1] * math.sin(ray_angle),
            player_dir[0] * math.sin(ray_angle) + player_dir[1] * math.cos(ray_angle)
        )
        for depth in range(max_depth):
            y = player_y + depth * ray_dir[0]
            x = player_x + depth * ray_dir[1]
            if 0 <= int(y) < len(game_map) and 0 <= int(x) < len(game_map[0]):
                char = game_map[int(y)][int(x)]
                if char == WALL:
                    rays.append((depth, WALL))
                    break
                elif char == ITEM:
                    rays.append((depth, ITEM))
                    break
                elif char == ENEMY:
                    rays.append((depth, ENEMY))
                    break
            else:
                rays.append((depth, FLOOR))
                break
    return rays

def draw_3d_viewport(viewport_win, player_pos, player_dir, game_map):
    viewport_win.clear()
    height, width = viewport_win.getmaxyx()
    
    max_depth = 20
    rays = raytrace(player_pos, player_dir, game_map, max_depth)
    
    for i, (depth, char) in enumerate(rays):
        column_height = int(height / (depth + 1))
        shade_index = min(depth, len(SHADES) - 1)
        shade = SHADES[shade_index]
        for y in range(height // 2 - column_height // 2, height // 2 + column_height // 2):
            if 0 <= y < height and 0 <= i < width:
                viewport_win.addch(y, i, shade if char == WALL else char)
    
    viewport_win.border()
    viewport_win.refresh()

def draw_action_log(stdscr, log_win, action_log):
    log_win.clear()
    for i, log in enumerate(action_log):
        log_win.addstr(i, 0, log)
    log_win.refresh()

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    # Define the layout
    height, width = stdscr.getmaxyx()
    viewport_height = int(height * 3 // 4)
    viewport_width = int(viewport_height * 4 // 3)
    viewport_y = (height - viewport_height) // 2
    viewport_x = (width - viewport_width) // 2

    viewport_win = curses.newwin(viewport_height, viewport_width, viewport_y, viewport_x)
    map_win = curses.newwin(height // 4, width // 4, height * 3 // 4, width * 3 // 4)
    actions_win = curses.newwin(height // 4, width // 4, 0, width * 3 // 4)
    log_win = curses.newwin(3, width, height - 3, 0)

    # Example game data
    game_map = [
        "########",
        "#......#",
        "#.####.#",
        "#.#..#.#",
        "#.#..#.#",
        "#.####.#",
        "#......#",
        "########"
    ]
    actions = ["Move North", "Move South", "Move East", "Move West"]
    action_log = ["Welcome to Everwood!"]
    player_pos = [1, 1]
    player_dir = [1, 0]  # Initially facing down

    while True:
        draw_2d_map(stdscr, map_win, game_map, player_pos, player_dir)
        draw_actions(stdscr, actions_win, actions)
        draw_3d_viewport(viewport_win, player_pos, player_dir, game_map)
        draw_action_log(stdscr, log_win, action_log)

        key = stdscr.getch()
        if key == ord('q'):
            break  # Exit the game loop if 'q' is pressed
        elif key == curses.KEY_UP:
            new_y = player_pos[0] + player_dir[0]
            new_x = player_pos[1] + player_dir[1]
            if game_map[new_y][new_x] != WALL:
                player_pos[0] = new_y
                player_pos[1] = new_x
        elif key == curses.KEY_DOWN:
            new_y = player_pos[0] - player_dir[0]
            new_x = player_pos[1] - player_dir[1]
            if game_map[new_y][new_x] != WALL:
                player_pos[0] = new_y
                player_pos[1] = new_x
        elif key == curses.KEY_LEFT:
            player_dir = [-player_dir[1], player_dir[0]]  # Rotate left
        elif key == curses.KEY_RIGHT:
            player_dir = [player_dir[1], -player_dir[0]]  # Rotate right

curses.wrapper(main)