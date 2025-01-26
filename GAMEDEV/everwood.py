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

def draw_2d_map(map_win, game_map, player_pos, player_dir):
    map_win.clear()
    for y, row in enumerate(game_map):
        for x, char in enumerate(row):
            map_win.addch(y, x, char)
    # Draw the player on the 2D map
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

    # Field of view calculations
    num_rays = 120  # Number of rays to cast
    angle_step = fov / num_rays
    start_angle = -fov / 2

    for i in range(num_rays):
        ray_angle = math.radians(start_angle + i * angle_step)
        ray_dir = (
            player_dir[0] * math.cos(ray_angle) - player_dir[1] * math.sin(ray_angle),
            player_dir[0] * math.sin(ray_angle) + player_dir[1] * math.cos(ray_angle),
        )
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
        # Calculate the column height based on depth
        column_height = max(1, int(height / (depth + 1)))  # Scale column height inversely with depth
        shade_index = min(depth, len(SHADES) - 1)
        shade = SHADES[shade_index]

        # Calculate the vertical start and end points for the column
        start_y = max(0, (height // 2) - (column_height // 2))
        end_y = min(height, (height // 2) + (column_height // 2))

        column_x = i * width // len(rays)  # Scale column width across viewport

        # Draw the column within its boundaries
        for y in range(start_y, end_y):
            if 0 <= y < height and 0 <= column_x < width:
                if char == WALL:
                    viewport_win.addch(y, column_x, shade, curses.color_pair(wall_color))
                else:
                    viewport_win.addch(y, column_x, shade, curses.color_pair(floor_color))

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