import curses
import math

# TILE TYPES
FLOOR = '.'
WALL = '#'
ITEM = 'I'
ENEMY = 'E'
PLAYER_ICONS = {
    (0, 1): '>', 
    (0, -1): '<', 
    (1, 0): 'v', 
    (-1, 0): '^' 
}

SHADES = " .:-=+*#%@"

def draw_2d_map(map_win, game_map, player_pos, player_dir):
    map_win.clear()
    for y, row in enumerate(game_map):
        for x, char in enumerate(row):
            map_win.addch(y, x, char)
    # draw the player on the 2D map
    player_y, player_x = player_pos
    player_icon = PLAYER_ICONS[tuple(player_dir)]
    map_win.addch(player_y, player_x, player_icon)
    map_win.refresh()

def draw_actions(actions_win, actions):
    actions_win.clear()
    for i, action in enumerate(actions):
        actions_win.addstr(i, 0, action)
    actions_win.refresh()

def raytrace(player_pos, player_dir, game_map, max_depth, fov=60):

    rays = []
    player_y, player_x = player_pos

    # field of view calculations (IDK WHAT THIS IS)
    num_rays = 120 
    angle_step = fov / num_rays
    start_angle = -fov / 2

    for i in range(num_rays):
        ray_angle = math.radians(start_angle + i * angle_step)
        ray_dir = (
            math.cos(ray_angle) * player_dir[0] - math.sin(ray_angle) * player_dir[1],
            math.sin(ray_angle) * player_dir[0] + math.cos(ray_angle) * player_dir[1],
        )
        ray_dir_length = math.sqrt(ray_dir[0]**2 + ray_dir[1]**2)
        ray_dir = (ray_dir[0] / ray_dir_length, ray_dir[1] / ray_dir_length)

        # what the fuck is this
        for depth in range(1, max_depth + 1):
            y = player_y + depth * ray_dir[0]
            x = player_x + depth * ray_dir[1]

            if 0 <= int(y) < len(game_map) and 0 <= int(x) < len(game_map[0]):
                char = game_map[int(y)][int(x)]
                if char in (WALL, ITEM, ENEMY):
                    rays.append((depth, char))
                    break
            else:
                break
        else:
            rays.append((max_depth, FLOOR))

    return rays


def draw_3d_viewport(viewport_win, player_pos, player_dir, game_map, wall_color, floor_color):

    viewport_win.clear()
    height, width = viewport_win.getmaxyx()

    max_depth = 20
    rays = raytrace(player_pos, player_dir, game_map, max_depth)

    for i, (depth, char) in enumerate(rays):
        depth = max(depth, 0.1)  # Prevent division by zero

        # wall height calculations
        perspective_height = height / (depth * math.cos(math.radians(30)))
        column_height = round(perspective_height)
        column_height = max(1, min(height, column_height))  # Clamp column height

        # vertical bounds of column
        center_y = height // 2
        start_y = center_y - (column_height // 2)
        end_y = center_y + (column_height // 2)

        # SUPPOSEDLY keeps the x and y within the bounds of the window
        start_y = max(0, start_y)
        end_y = min(height - 1, end_y)

        # maps the ray to the viewport
        column_x = int(i * width / len(rays))

        # debug output
        print(f"Ray {i}: depth={depth:.2f}, column_x={column_x}, column_height={column_height}, start_y={start_y}, end_y={end_y}")

        if 0 <= column_x < width:  # Ensure column_x is valid
            for y in range(start_y, end_y + 1):
                try:
                    if char == WALL:
                        viewport_win.addch(y, column_x, SHADES[min(int(depth), len(SHADES) - 1)], curses.color_pair(wall_color))
                    else:
                        viewport_win.addch(y, column_x, SHADES[min(int(depth), len(SHADES) - 1)], curses.color_pair(floor_color))
                except curses.error as e:
                    print(f"Error drawing ray {i} at ({y}, {column_x}): {e}")
    viewport_win.border()
    viewport_win.refresh()

def draw_action_log(log_win, action_log):
    log_win.clear()
    for i, log in enumerate(action_log):
        log_win.addstr(i, 0, log)
    log_win.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Wall color (brown)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Floor/Ceiling color (gray)

    stdscr.clear()

    # Define the layout
    height, width = stdscr.getmaxyx()
    viewport_height = int(height * 0.7)
    viewport_width = int(width * 0.5)

    viewport_win = curses.newwin(viewport_height, viewport_width, 1, 1)
    map_win = curses.newwin(height - viewport_height - 2, viewport_width, viewport_height + 1, 1)
    actions_win = curses.newwin(viewport_height, width - viewport_width - 2, 1, viewport_width + 2)
    log_win = curses.newwin(3, width, height - 3, 0)

    # Example game data
    game_map = [
        "###############",
        "#.............#",
        "#.####........#",
        "#.#..#........#",
        "#.#..#........#",
        "#.####........#",
        "#.............#",
        "##########....#",
        "##########....#",
        "#.............#",
        "###############"
    ]
    actions = ["Move North", "Move South", "Move East", "Move West"]
    action_log = ["EVERWOOD DEBUG MODE"]
    player_pos = [1, 1]
    player_dir = [1, 0]  # Initially facing down

    wall_color = 1
    floor_color = 2

    while True:
        draw_2d_map(map_win, game_map, player_pos, player_dir)
        draw_actions(actions_win, actions)
        draw_3d_viewport(viewport_win, player_pos, player_dir, game_map, wall_color, floor_color)
        draw_action_log(log_win, action_log)

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