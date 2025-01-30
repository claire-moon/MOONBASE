import curses
import math

# Tile definitions
FLOOR = '.'
WALL = '#'

# Player icons based on direction
PLAYER_ICONS = {
    (1, 0): '>',  # East
    (-1, 0): '<', # West
    (0, 1): 'v',  # South
    (0, -1): '^', # North
}

# Shades for distance (darker means farther)
SHADES = " .:-=+*#%@"
MAX_SHADE = len(SHADES) - 1

# FOV settings
FOV = 66  # Degrees
CAMERA_LENGTH = math.tan(math.radians(FOV / 2))

# Color pairs
WALL_COLOR = 1
FLOOR_COLOR = 2
TITLE_COLOR = 3  # Blood red for the title

# ASCII title
ASCII_TITLE = [
    "▓█████ ██▒   █▓▓█████  ██▀███   █     █░ ▒█████   ▒█████  ▓█████▄ ",
    "▓█   ▀▓██░   █▒▓█   ▀ ▓██ ▒ ██▒▓█░ █ ░█░▒██▒  ██▒▒██▒  ██▒▒██▀ ██▌",
    "▒███   ▓██  █▒░▒███   ▓██ ░▄█ ▒▒█░ █ ░█ ▒██░  ██▒▒██░  ██▒░██   █▌",
    "▒▓█  ▄  ▒██ █░░▒▓█  ▄ ▒██▀▀█▄  ░█░ █ ░█ ▒██   ██░▒██   ██░░▓█▄   ▌",
    "░▒████▒  ▒▀█░  ░▒████▒░██▓ ▒██▒░░██▒██▓ ░ ████▓▒░░ ████▓▒░░▒████▓ ",
    "░░ ▒░ ░  ░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░░ ▓░▒ ▒  ░ ▒░▒░▒░ ░ ▒░▒░▒░  ▒▒▓  ▒ ",
    " ░ ░  ░  ░ ░░   ░ ░  ░  ░▒ ░ ▒░  ▒ ░ ░    ░ ▒ ▒░   ░ ▒ ▒░  ░ ▒  ▒ ",
    "   ░       ░░     ░     ░░   ░   ░   ░  ░ ░ ░ ▒  ░ ░ ░ ▒   ░ ░  ░ ",
    "   ░  ░     ░     ░  ░   ░         ░        ░ ░      ░ ░     ░    ",
    "           ░                                               ░      "
]

def draw_2d_map(map_win, game_map, player_pos, player_dir, camera_y, camera_x):
    """
    Draw the 2D map and the player.
    - map_win: The window where the map is drawn.
    - game_map: The 2D array representing the map.
    - player_pos: The player's current position (x, y).
    - player_dir: The player's direction vector.
    - camera_y: The camera's y offset.
    - camera_x: The camera's x offset.
    """
    map_win.clear()
    map_height, map_width = map_win.getmaxyx()
    
    # Calculate the visible portion of the map
    start_y = max(0, camera_y - map_height // 2)
    start_x = max(0, camera_x - map_width // 2)
    end_y = min(len(game_map), start_y + map_height)
    end_x = min(len(game_map[0]), start_x + map_width)
    
    # Draw the visible portion of the map
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            try:
                map_win.addch(y - start_y, x - start_x, game_map[y][x])
            except curses.error:
                pass  # Skip invalid positions
    
    # Draw the player (centered in the viewport)
    px, py = int(player_pos[0]), int(player_pos[1])
    if start_y <= py < end_y and start_x <= px < end_x:
        dir_key = (round(player_dir[0]), round(player_dir[1]))
        icon = PLAYER_ICONS.get(dir_key, '?')
        try:
            map_win.addch(py - start_y, px - start_x, icon)
        except curses.error:
            pass  # Skip invalid positions
    
    map_win.border()
    map_win.refresh()

def draw_3d_viewport(viewport_win, player_pos, player_dir, camera_plane, game_map):
    """
    Draw the 3D viewport using ray casting.
    - viewport_win: The window where the 3D view is drawn.
    - player_pos: The player's current position (x, y).
    - player_dir: The player's direction vector.
    - camera_plane: The camera plane vector.
    - game_map: The 2D array representing the map.
    """
    height, width = viewport_win.getmaxyx()
    viewport_win.clear()
    
    for x in range(1, width - 1):  # Account for border
        # Calculate ray position and direction
        camera_x = 2 * (x / (width - 2)) - 1  # [-1, 1]
        ray_dir = (
            player_dir[0] + camera_plane[0] * camera_x,
            player_dir[1] + camera_plane[1] * camera_x
        )
        
        # DDA setup
        map_x, map_y = int(player_pos[0]), int(player_pos[1])
        delta_dist = (
            abs(1 / ray_dir[0]) if ray_dir[0] else 1e30,
            abs(1 / ray_dir[1]) if ray_dir[1] else 1e30
        )
        step = [0, 0]
        side_dist = [0.0, 0.0]
        
        # Determine step and initial side distances
        step[0] = 1 if ray_dir[0] > 0 else -1
        side_dist[0] = (player_pos[0] - map_x) * delta_dist[0] if ray_dir[0] < 0 else (map_x + 1 - player_pos[0]) * delta_dist[0]
        step[1] = 1 if ray_dir[1] > 0 else -1
        side_dist[1] = (player_pos[1] - map_y) * delta_dist[1] if ray_dir[1] < 0 else (map_y + 1 - player_pos[1]) * delta_dist[1]
        
        # DDA loop
        hit, side = False, 0
        while not hit:
            if side_dist[0] < side_dist[1]:
                side_dist[0] += delta_dist[0]
                map_x += step[0]
                side = 0
            else:
                side_dist[1] += delta_dist[1]
                map_y += step[1]
                side = 1
            
            # Check boundaries
            if map_x < 0 or map_x >= len(game_map[0]) or map_y < 0 or map_y >= len(game_map):
                break
            
            # Check hit
            if game_map[map_y][map_x] == WALL:
                hit = True
        
        if hit:
            # Calculate distance
            if side == 0:
                dist = (map_x - player_pos[0] + (1 - step[0]) / 2) / ray_dir[0]
            else:
                dist = (map_y - player_pos[1] + (1 - step[1]) / 2) / ray_dir[1]
            
            # Calculate line height and draw
            line_height = int(height / dist) if dist else height
            start = max(0, height//2 - line_height//2)
            end = min(height-1, height//2 + line_height//2)
            shade = SHADES[min(int(dist), MAX_SHADE)]
            
            for y in range(start, end):
                if 0 <= y < height-1 and 0 <= x < width-1:
                    try:
                        if game_map[map_y][map_x] == WALL:
                            viewport_win.addch(y, x, shade, curses.color_pair(WALL_COLOR))
                        else:
                            viewport_win.addch(y, x, shade, curses.color_pair(FLOOR_COLOR))
                    except curses.error:
                        pass  # Skip invalid positions
    
    viewport_win.border()
    viewport_win.refresh()

def draw_log(log_win, log_messages):
    """
    Draw the log window.
    - log_win: The window where the log is drawn.
    - log_messages: A list of log messages to display.
    """
    log_win.clear()
    log_win.border()
    
    # Display the last few log messages
    for i, message in enumerate(log_messages[-10:]):  # Show last 10 messages
        try:
            log_win.addstr(i + 1, 1, message)
        except curses.error:
            pass  # Skip invalid positions
    
    log_win.refresh()

def draw_title(title_win):
    """
    Draw the ASCII title.
    - title_win: The window where the title is drawn.
    """
    title_win.clear()
    for i, line in enumerate(ASCII_TITLE):
        try:
            title_win.addstr(i, 0, line, curses.color_pair(TITLE_COLOR))
        except curses.error:
            pass  # Skip invalid positions
    title_win.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(WALL_COLOR, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Wall color
    curses.init_pair(FLOOR_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Floor color
    curses.init_pair(TITLE_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)    # Blood red title
    
    # Game setup
    game_map = [
        "###############",
        "#.............#",
        "#.####........#",
        "#.#..#........#",
        "#.#..#........#",
        "#.####........#",
        "#.............#",
        "##########....#",
        "#........#....#",
        "#........#....#",
        "#........#....#",
        "#........#....#",
        "#........#....#",
        "#.............#",
        "#.............#",
        "#........#....#",
        "#........#....#",
        "#........#....#",
        "#........#....#",
        "##########....#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "###############"
    ]
    player_pos = [1.5, 1.5]  # Start position (centered in the hallway)
    player_dir = [1, 0]       # Facing east
    camera_plane = [0, CAMERA_LENGTH]
    
    # Log messages
    log_messages = []
    
    # Window setup
    h, w = stdscr.getmaxyx()
    
    # Define viewport size (4:3 aspect ratio)
    viewport_height = min(h // 2, 20)  # Fixed height for 2D map
    viewport_width = min(w // 2, 30)   # Fixed width for 2D map
    
    # Ensure the viewport fits within the terminal
    if viewport_height <= 0 or viewport_width <= 0:
        raise ValueError("Terminal too small to create viewport.")
    
    # Position viewport in the top-left quadrant
    viewport = curses.newwin(viewport_height, viewport_width, 1, 1)
    
    # Position 2D map below the viewport
    map_win = curses.newwin(viewport_height, viewport_width, viewport_height + 2, 1)
    
    # Position log window to the right of the viewport (same height as viewport + map)
    log_win_height = viewport_height * 2 + 1  # Height of viewport + map + border
    log_win = curses.newwin(log_win_height, w - viewport_width - 2, 1, viewport_width + 2)
    
    # Position title window at the bottom
    title_win = curses.newwin(len(ASCII_TITLE), w, h - len(ASCII_TITLE), 0)
    
    # Main loop
    while True:
        # Calculate camera offsets to center the player
        camera_y = int(player_pos[1])
        camera_x = int(player_pos[0])
        
        draw_2d_map(map_win, game_map, player_pos, player_dir, camera_y, camera_x)
        draw_3d_viewport(viewport, player_pos, player_dir, camera_plane, game_map)
        draw_log(log_win, log_messages)
        draw_title(title_win)
        
        key = stdscr.getch()
        
        if key == ord('q'):
            break
        elif key == curses.KEY_UP:
            new_x = player_pos[0] + player_dir[0]
            new_y = player_pos[1] + player_dir[1]
            if game_map[int(new_y)][int(new_x)] == FLOOR:
                player_pos[0] = new_x
                player_pos[1] = new_y
                log_messages.append("You moved forward.")
        elif key == curses.KEY_DOWN:
            new_x = player_pos[0] - player_dir[0]
            new_y = player_pos[1] - player_dir[1]
            if game_map[int(new_y)][int(new_x)] == FLOOR:
                player_pos[0] = new_x
                player_pos[1] = new_y
                log_messages.append("You moved backward.")
        elif key == curses.KEY_LEFT:
            # Rotate direction and camera plane CCW
            new_dir = (-player_dir[1], player_dir[0])
            new_plane = (-camera_plane[1], camera_plane[0])
            player_dir = list(new_dir)
            camera_plane = list(new_plane)
            log_messages.append("You turned left.")
        elif key == curses.KEY_RIGHT:
            # Rotate direction and camera plane CW
            new_dir = (player_dir[1], -player_dir[0])
            new_plane = (camera_plane[1], -camera_plane[0])
            player_dir = list(new_dir)
            camera_plane = list(new_plane)
            log_messages.append("You turned right.")

if __name__ == "__main__":
    curses.wrapper(main)