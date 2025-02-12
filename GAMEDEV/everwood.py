import curses
import math
import configparser
import os

# Define the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the map and config files
MAP_FILE = os.path.join(SCRIPT_DIR, "MAP01.txt")  # Updated to MAP01.txt
GAMEDATA_FILE = os.path.join(SCRIPT_DIR, "GAMEDATA.ini")

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
LOG_PLAYER_COLOR = 4  # Blue for "You"
LOG_DIRECTION_COLOR = 5  # Yellow for directions
CEILING_COLOR = 7  # Gray for ceiling
FLOOR_COLOR_3D = 8  # Gray for floor

# Gradient color pairs for shading
SHADE_COLORS = 10  # Starting color pair for shades

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

def load_next_map(map_index):
    """
    Load the next map in sequence.
    - map_index: The index of the map to load (e.g., 1 for MAP01.txt).
    Returns: A dictionary containing the map data.
    """
    map_file = os.path.join(SCRIPT_DIR, f"MAP{map_index:02d}.txt")
    return load_map(map_file)

def load_map(map_file):
    """
    Load a map from a .txt file.
    - map_file: The path to the .txt file.
    Returns: A dictionary containing the map data.
    """
    try:
        with open(map_file, "r") as file:
            layout = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Warning: Map file '{map_file}' not found. Using default map.")
        layout = [
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
    
    map_data = {
        "layout": layout,
        "wall_color": "BROWN",  # Default wall color
        "floor_color": "GRAY",   # Default floor color,
    }
    return map_data

def load_gamedata():
    """
    Load game data from GAMEDATA.ini.
    Returns: A dictionary containing the game data.
    """
    config = configparser.ConfigParser()
    config.read(GAMEDATA_FILE)
    
    gamedata = {
        "player_color": config.get("COLORS", "player_color", fallback="BLUE"),
        "direction_color": config.get("COLORS", "direction_color", fallback="YELLOW"),
        "wall_color": config.get("COLORS", "wall_color", fallback="BROWN"),
        "floor_color": config.get("COLORS", "floor_color", fallback="GRAY"),
        "max_log_entries": config.getint("LOG", "max_log_entries", fallback=10),
    }
    return gamedata

def draw_2d_map(map_win, game_map, player_pos, player_dir, camera_y, camera_x, wall_color, floor_color):
    """
    Draw the 2D map and the player.
    - map_win: The window where the map is drawn.
    - game_map: The 2D array representing the map.
    - player_pos: The player's current position (x, y).
    - player_dir: The player's direction vector.
    - camera_y: The camera's y offset.
    - camera_x: The camera's x offset.
    - wall_color: The color pair for walls.
    - floor_color: The color pair for the floor.
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
                char = game_map[y][x]
                if char == WALL:
                    map_win.addch(y - start_y, x - start_x, char, curses.color_pair(wall_color))
                elif char == FLOOR:
                    map_win.addch(y - start_y, x - start_x, char, curses.color_pair(floor_color))
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

def draw_3d_viewport(viewport_win, player_pos, player_dir, camera_plane, game_map, wall_color, floor_color):
    """
    Draw the 3D viewport using ray casting.
    - viewport_win: The window where the 3D view is drawn.
    - player_pos: The player's current position (x, y).
    - player_dir: The player's direction vector.
    - camera_plane: The camera plane vector.
    - game_map: The 2D array representing the map.
    - wall_color: The color pair for walls.
    - floor_color: The color pair for the floor.
    """
    height, width = viewport_win.getmaxyx()
    viewport_win.clear()
    
    # Fill the ceiling and floor with gradient shading
    for y in range(1, height // 2):  # Ceiling
        for x in range(1, width - 1):
            # Calculate the distance for the ceiling
            dist = (height // 2 - y) / (height // 2)
            shade_level = min(int(dist * MAX_SHADE), MAX_SHADE)
            # Use the default ceiling color (gray) and apply the gradient shading
            color_pair = CEILING_COLOR  # Default ceiling color
            try:
                # Apply the gradient shading by blending with the base color
                viewport_win.addch(y, x, ' ', curses.color_pair(color_pair) | curses.A_DIM if shade_level > 0 else curses.color_pair(color_pair))
            except curses.error:
                pass  # Skip invalid positions
    
    for y in range(height // 2, height - 1):  # Floor
        for x in range(1, width - 1):
            # Calculate the distance for the floor
            dist = (y - height // 2) / (height // 2)
            shade_level = min(int(dist * MAX_SHADE), MAX_SHADE)
            # Use the default floor color (gray) and apply the gradient shading
            color_pair = FLOOR_COLOR_3D  # Default floor color
            try:
                # Apply the gradient shading by blending with the base color
                viewport_win.addch(y, x, ' ', curses.color_pair(color_pair) | curses.A_DIM if shade_level > 0 else curses.color_pair(color_pair))
            except curses.error:
                pass  # Skip invalid positions
    
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
            
            # Determine the color based on the shade level
            shade_level = min(int(dist), MAX_SHADE)
            color_pair = SHADE_COLORS + shade_level
            
            for y in range(start, end):
                if 0 <= y < height-1 and 0 <= x < width-1:
                    try:
                        # Set the background color to the shade level
                        viewport_win.addch(y, x, shade, curses.color_pair(color_pair))
                    except curses.error:
                        pass  # Skip invalid positions
    
    viewport_win.border()
    viewport_win.refresh()

def draw_log(log_win, log_messages, player_color, direction_color):
    """
    Draw the log window with colored text.
    - log_win: The window where the log is drawn.
    - log_messages: A list of log messages to display.
    - player_color: The color pair for "You".
    - direction_color: The color pair for directions.
    """
    log_win.clear()
    log_win.border()
    
    height, width = log_win.getmaxyx()
    max_entries = height - 2  # Account for border
    
    # Display the last few log messages
    for i, message in enumerate(log_messages[-max_entries:]):
        try:
            # Split the message into parts for coloring
            if "You" in message:
                parts = message.split(" ")
                log_win.addstr(i + 1, 1, parts[0], curses.color_pair(player_color))  # "You" in blue
                log_win.addstr(" " + parts[1], curses.color_pair(6))  # "moved" or "turned" in white
                log_win.addstr(" " + " ".join(parts[2:]), curses.color_pair(direction_color))  # Direction in yellow
            else:
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

def draw_title_screen(stdscr):
    """
    Draw the title screen and handle user input.
    - stdscr: The standard screen object from curses.
    Returns: The selected option (1-6).
    """
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Display the title
    for i, line in enumerate(ASCII_TITLE):
        x = w//2 - len(line)//2
        y = h//2 - len(ASCII_TITLE)//2 + i
        stdscr.addstr(y, x, line, curses.color_pair(TITLE_COLOR))
    
    # Display the menu options
    options = [
        "1. NEW GAME (CREATE CHARACTER)",
        "2. NEW GAME (DEFAULT CHARACTER)",
        "3. NEW GAME (DEBUG MODE)",
        "4. LOAD GAME",
        "5. OPTIONS",
        "6. EXIT"
    ]
    
    for i, option in enumerate(options):
        x = w//2 - len(option)//2
        y = h//2 + len(ASCII_TITLE)//2 + i + 2
        stdscr.addstr(y, x, option)
    
    stdscr.refresh()
    
    # Wait for user input
    while True:
        key = stdscr.getch()
        if key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')]:
            return key - ord('0')  # Convert ASCII to integer

def draw_chargen_screen(stdscr):
    """
    Draw the character creation screen.
    - stdscr: The standard screen object from curses.
    """
    stdscr.clear()  # Clear the screen before rendering the character creation screen
    h, w = stdscr.getmaxyx()
    
    # Display the character creation message
    message = "CHARACTER CREATION SCREEN"
    x = w//2 - len(message)//2
    y = h//2
    stdscr.addstr(y, x, message)
    
    stdscr.refresh()
    stdscr.getch()  # Wait for any key press to return

def draw_options_screen(stdscr, gamedata):
    """
    Draw the options screen and handle user input.
    - stdscr: The standard screen object from curses.
    - gamedata: The game data dictionary.
    """
    stdscr.clear()  # Clear the screen before rendering the options screen
    h, w = stdscr.getmaxyx()
    
    # Display the options
    options = [
        "1. Change Player Color",
        "2. Change Direction Color",
        "3. Change Wall Color",
        "4. Change Floor Color",
        "5. Back to Title Screen"
    ]
    
    for i, option in enumerate(options):
        x = w//2 - len(option)//2
        y = h//2 - len(options)//2 + i
        stdscr.addstr(y, x, option)
    
    stdscr.refresh()
    
    # Wait for user input
    while True:
        key = stdscr.getch()
        if key == ord('1'):
            gamedata["player_color"] = "BLUE"  # Example: Change player color to blue
        elif key == ord('2'):
            gamedata["direction_color"] = "YELLOW"  # Example: Change direction color to yellow
        elif key == ord('3'):
            gamedata["wall_color"] = "BROWN"  # Example: Change wall color to brown
        elif key == ord('4'):
            gamedata["floor_color"] = "GRAY"  # Example: Change floor color to gray
        elif key == ord('5'):
            break  # Return to title screen

def draw_load_game_screen(stdscr):
    """
    Draw the load game screen.
    - stdscr: The standard screen object from curses.
    """
    stdscr.clear()  # Clear the screen before rendering the load game screen
    h, w = stdscr.getmaxyx()
    
    # Display the load game message
    message = "LOAD GAME SCREEN (SAVE FILES LIST)"
    x = w//2 - len(message)//2
    y = h//2
    stdscr.addstr(y, x, message)
    
    stdscr.refresh()
    stdscr.getch()  # Wait for any key press to return

def main(stdscr):
    # Enable fullscreen mode
    curses.resize_term(curses.LINES, curses.COLS)
    stdscr.clear()
    stdscr.refresh()
    
    # Check if the terminal supports colors
    if not curses.has_colors():
        raise RuntimeError("Your terminal does not support colors.")
    
    # Initialize colors
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()  # Use default terminal colors for better compatibility
    
    # Load game data
    gamedata = load_gamedata()
    
    # Define color pairs based on GAMEDATA.ini
    curses.init_pair(WALL_COLOR, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Wall color
    curses.init_pair(FLOOR_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Floor color
    curses.init_pair(TITLE_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)    # Blood red title
    curses.init_pair(LOG_PLAYER_COLOR, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Blue for "You"
    curses.init_pair(LOG_DIRECTION_COLOR, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Yellow for directions
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White for "moved" or "turned"
    curses.init_pair(CEILING_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Ceiling color (gray)
    curses.init_pair(FLOOR_COLOR_3D, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Floor color (gray)
    
    # Initialize gradient color pairs for shading (brown gradient)
    for i in range(MAX_SHADE + 1):
        # Create a gradient from light brown to black
        intensity = int(255 * (1 - i / MAX_SHADE))
        curses.init_color(i + 10, intensity, intensity // 2, 0)  # Brown gradient
        curses.init_pair(SHADE_COLORS + i, i + 10, i + 10)
    
    # Title screen loop
    game_in_play = False  # Flag to track if the game is running
    while True:
        if not game_in_play:
            option = draw_title_screen(stdscr)
        
        if option == 1:
            draw_chargen_screen(stdscr)
        elif option == 2:
            # Start the game with default character
            game_in_play = True  # Set the game state to "in play"
            stdscr.clear()  # Clear the title screen
            stdscr.refresh()  # Refresh to apply the clear
            
            map_index = 1
            map_data = load_next_map(map_index)
            game_map = map_data["layout"]
            wall_color = WALL_COLOR
            floor_color = FLOOR_COLOR
            
            # Player setup
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
            
            # Main game loop
            while game_in_play:
                # Calculate camera offsets to center the player
                camera_y = int(player_pos[1])
                camera_x = int(player_pos[0])
                
                draw_2d_map(map_win, game_map, player_pos, player_dir, camera_y, camera_x, wall_color, floor_color)
                draw_3d_viewport(viewport, player_pos, player_dir, camera_plane, game_map, wall_color, floor_color)
                draw_log(log_win, log_messages, LOG_PLAYER_COLOR, LOG_DIRECTION_COLOR)
                draw_title(title_win)
                
                key = stdscr.getch()
                
                if key == ord('q'):
                    game_in_play = False  # Exit the game loop and return to the title screen
                    stdscr.clear()  # Clear the game screen
                    stdscr.refresh()  # Refresh to apply the clear
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
        elif option == 3:
            # Debug mode (same as option 2 but with debug features)
            pass
        elif option == 4:
            draw_load_game_screen(stdscr)
        elif option == 5:
            draw_options_screen(stdscr, gamedata)
        elif option == 6:
            break  # Exit the game
        
if __name__ == "__main__":
    curses.wrapper(main)