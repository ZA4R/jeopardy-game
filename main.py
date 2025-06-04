import pygame
import sys
import serial
import time

# --- Constants ---
# Set the width and height of the game window
WIDTH, HEIGHT = 1000, 700
# Set the frames per second for the game loop
FPS = 60

# Define colors using RGB tuples
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 139)  # Darker blue for board elements
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0) # Darker green for buttons
GRAY = (100, 100, 100) # Color for answered questions

# Serial Port Configuration (IMPORTANT: User needs to change this!)
# Replace 'COM3' with your Arduino's serial port.
# On Windows, it might be 'COM1', 'COM3', etc.
# On Linux/macOS, it might be '/dev/ttyUSB0', '/dev/ttyACM0', '/dev/cu.usbmodemXXXX', etc.
SERIAL_PORT = 'COM3'
# Baud rate must match the baud rate set in your Arduino sketch
BAUD_RATE = 9600

# --- Game Data ---
# Define the categories for the Jeopardy board
CATEGORIES = ["PYTHON", "HISTORY", "SCIENCE", "GEOGRAPHY", "SPORTS"]
# Define the dollar values for each question
DOLLAR_VALUES = [200, 400, 600, 800, 1000]

# Dictionary to store questions, answers, and their answered status.
# Structure: Category -> Dollar Value -> {"question": "...", "answer": "...", "answered": False}
# You can replace these placeholder questions with your actual Jeopardy questions.
QUESTIONS = {
    "PYTHON": {
        200: {"question": "What keyword is used to define a function in Python?", "answer": "def", "answered": False},
        400: {"question": "Which data structure is ordered, mutable, and allows duplicate members?", "answer": "list", "answered": False},
        600: {"question": "What is the purpose of 'self' in a Python class method?", "answer": "Refers to the instance of the class", "answered": False},
        800: {"question": "How do you open a file named 'data.txt' for reading in Python?", "answer": "open('data.txt', 'r')", "answered": False},
        1000: {"question": "Explain GIL (Global Interpreter Lock) in Python.", "answer": "A mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once.", "answered": False},
    },
    "HISTORY": {
        200: {"question": "Who was the first President of the United States?", "answer": "George Washington", "answered": False},
        400: {"question": "In what year did World War II end?", "answer": "1945", "answered": False},
        600: {"question": "Which ancient civilization built the pyramids?", "answer": "Egyptians", "answered": False},
        800: {"question": "Who wrote 'The Communist Manifesto'?", "answer": "Karl Marx and Friedrich Engels", "answered": False},
        1000: {"question": "What event is considered the start of the French Revolution?", "answer": "Storming of the Bastille", "answered": False},
    },
    "SCIENCE": {
        200: {"question": "What is the chemical symbol for water?", "answer": "H2O", "answered": False},
        400: {"question": "What planet is known as the Red Planet?", "answer": "Mars", "answered": False},
        600: {"question": "What is the smallest unit of matter?", "answer": "Atom", "answered": False},
        800: {"question": "What force keeps planets in orbit around the sun?", "answer": "Gravity", "answered": False},
        1000: {"question": "What is the process by which plants make their own food?", "answer": "Photosynthesis", "answered": False},
    },
    "GEOGRAPHY": {
        200: {"question": "What is the capital of France?", "answer": "Paris", "answered": False},
        400: {"question": "Which is the longest river in the world?", "answer": "Nile River", "answered": False},
        600: {"question": "What is the highest mountain in Africa?", "answer": "Mount Kilimanjaro", "answered": False},
        800: {"question": "Which country is known as the Land of the Rising Sun?", "answer": "Japan", "answered": False},
        1000: {"question": "What is the largest desert in the world?", "answer": "Antarctica (Polar Desert)", "answered": False},
    },
    "SPORTS": {
        200: {"question": "How many players are on a standard soccer team?", "answer": "11", "answered": False},
        400: {"question": "Which sport uses a shuttlecock?", "answer": "Badminton", "answered": False},
        600: {"question": "Who is often called 'The King' in basketball?", "answer": "LeBron James", "answered": False},
        800: {"question": "In what year were the first modern Olympic Games held?", "answer": "1896", "answered": False},
        1000: {"question": "Which country has won the most FIFA World Cups?", "answer": "Brazil", "answered": False},
    },
}

# --- Game State Variables ---
# Controls the current screen/phase of the game
# States: "BOARD", "SHOWING_QUESTION", "WAITING_FOR_BUZZER", "BUZZER_RESPONDED"
current_state = "BOARD"
selected_category = None # Stores the category of the selected question
selected_value = None    # Stores the dollar value of the selected question
buzzer_pressed_by = None # Stores which player (e.g., 'PLAYER 1', 'PLAYER 2') pressed the buzzer
buzzer_feedback_timer = 0 # Used to control how long the "Player X Buzzed In!" message is shown

# --- Pygame Initialization ---
pygame.init()
# Set up the display window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# Set the window title
pygame.display.set_caption("Jeopardy-like Game Interface")
# Create a clock object to control frame rate
clock = pygame.time.Clock()

# --- Fonts ---
# Initialize fonts for different text elements. Using default Pygame font.
category_font = pygame.font.Font(None, 40)
dollar_font = pygame.font.Font(None, 60)
question_font = pygame.font.Font(None, 45)
instruction_font = pygame.font.Font(None, 30)
buzzer_font = pygame.font.Font(None, 70)

# --- Serial Communication Setup ---
ser = None # Initialize serial port object as None
try:
    # Attempt to open the serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Successfully connected to serial port {SERIAL_PORT}")
except serial.SerialException as e:
    # If connection fails, print an error and disable serial functionality
    print(f"Could not open serial port {SERIAL_PORT}: {e}")
    print("Please check if the Arduino is connected and the port name is correct.")
    print("You can continue playing, but buzzer functionality will be disabled.")

# --- UI Element Dimensions and Positions ---
# Calculate dimensions for each question cell on the board
# 100px total horizontal padding (50px left, 50px right)
# 150px total vertical padding (100px top for categories, 50px bottom for instructions/buttons)
cell_width = (WIDTH - 100) // len(CATEGORIES)
cell_height = (HEIGHT - 150) // len(DOLLAR_VALUES)
# Starting coordinates for the grid of questions
start_x = 50
start_y = 100

# Dictionary to store the Pygame Rect objects for each question cell.
# This is used for click detection.
question_rects = {} # {(category_name, dollar_value): pygame.Rect}

# --- Helper Functions ---

def draw_text(surface, text, font, color, center_x, center_y):
    """
    Helper function to render and draw text centered at given coordinates.
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    surface.blit(text_surface, text_rect)

def draw_button(surface, text, font, rect, color, text_color, border_radius=10):
    """
    Helper function to draw a button with a slight shadow and border.
    """
    # Draw shadow for depth
    shadow_offset = 3
    pygame.draw.rect(surface, BLACK, (rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height), border_radius=border_radius)
    # Draw the main button rectangle
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    # Draw a white border around the button
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=border_radius)
    # Draw the button text
    draw_text(surface, text, font, text_color, rect.centerx, rect.centery)
    return rect # Return the rectangle for click detection

def wrap_text(surface, text, font, max_width):
    """
    Wraps text to fit within a given maximum width.
    Returns a list of lines.
    """
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        # Test if adding the next word exceeds the max_width
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            # If the current line is not empty, add it to the list of lines
            if current_line:
                lines.append(' '.join(current_line))
            # Start a new line with the current word
            current_line = [word]
    # Add any remaining words as the last line
    if current_line:
        lines.append(' '.join(current_line))
    return lines


def draw_board():
    """
    Draws the main Jeopardy game board, including categories and dollar values.
    """
    screen.fill(BLACK) # Fill the background with black

    # Draw category headers at the top
    for i, category in enumerate(CATEGORIES):
        cat_x = start_x + i * cell_width + cell_width // 2
        draw_text(screen, category, category_font, YELLOW, cat_x, start_y - 50)

    # Draw individual dollar value cells for each category
    for row_idx, value in enumerate(DOLLAR_VALUES):
        for col_idx, category in enumerate(CATEGORIES):
            q_data = QUESTIONS[category][value] # Get question data
            rect_x = start_x + col_idx * cell_width
            rect_y = start_y + row_idx * cell_height
            # Add a small margin between cells for better visual separation
            rect = pygame.Rect(rect_x + 5, rect_y + 5, cell_width - 10, cell_height - 10)

            # Store the rectangle for click detection later
            question_rects[(category, value)] = rect

            if q_data["answered"]:
                # If the question has been answered, draw a gray box with an 'X'
                pygame.draw.rect(screen, GRAY, rect, border_radius=10)
                draw_text(screen, "X", dollar_font, BLACK, rect.centerx, rect.centery)
            else:
                # If not answered, draw the blue box with the dollar value
                pygame.draw.rect(screen, BLUE, rect, border_radius=10)
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=10) # White border
                draw_text(screen, f"${value}", dollar_font, YELLOW, rect.centerx, rect.centery)

def draw_question_screen():
    """
    Draws the screen displaying the selected question.
    Includes a button to start the buzzer round.
    """
    screen.fill(BLACK) # Clear the screen

    question_text = QUESTIONS[selected_category][selected_value]["question"]
    # Wrap the question text to fit within the screen width
    wrapped_lines = wrap_text(screen, question_text, question_font, WIDTH - 200)

    # Define the rectangle for the question box
    question_box_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 200)
    pygame.draw.rect(screen, BLUE, question_box_rect, border_radius=20) # Blue background
    pygame.draw.rect(screen, WHITE, question_box_rect, 5, border_radius=20) # White border

    # Draw the wrapped question text, centered vertically within the box
    line_height = question_font.get_linesize()
    text_start_y = question_box_rect.centery - (len(wrapped_lines) * line_height) // 2
    for i, line in enumerate(wrapped_lines):
        draw_text(screen, line, question_font, WHITE, question_box_rect.centerx, text_start_y + i * line_height)

    # Instructions for the user
    instruction_text = "Click 'Start Buzzer Round' when ready for players to buzz in."
    draw_text(screen, instruction_text, instruction_font, YELLOW, WIDTH // 2, HEIGHT - 100)

    # Button to transition to the buzzer waiting state
    start_buzzer_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 70, 300, 50)
    draw_button(screen, "Start Buzzer Round", instruction_font, start_buzzer_button_rect, GREEN, WHITE)
    return start_buzzer_button_rect # Return the button's rect for click detection

def draw_waiting_for_buzzer_screen():
    """
    Draws the screen while the game is actively waiting for a buzzer input.
    """
    screen.fill(BLACK) # Clear the screen

    question_text = QUESTIONS[selected_category][selected_value]["question"]
    wrapped_lines = wrap_text(screen, question_text, question_font, WIDTH - 200)

    # Question box (same as in draw_question_screen)
    question_box_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 200)
    pygame.draw.rect(screen, BLUE, question_box_rect, border_radius=20)
    pygame.draw.rect(screen, WHITE, question_box_rect, 5, border_radius=20)

    line_height = question_font.get_linesize()
    text_start_y = question_box_rect.centery - (len(wrapped_lines) * line_height) // 2
    for i, line in enumerate(wrapped_lines):
        draw_text(screen, line, question_font, WHITE, question_box_rect.centerx, text_start_y + i * line_height)

    # Display "Waiting for buzzers..." message
    draw_text(screen, "Waiting for buzzers...", buzzer_font, YELLOW, WIDTH // 2, HEIGHT - 100)

def draw_buzzer_responded_screen():
    """
    Draws the screen indicating which player buzzed in.
    Includes a button to return to the main board.
    """
    screen.fill(BLACK) # Clear the screen

    question_text = QUESTIONS[selected_category][selected_value]["question"]
    wrapped_lines = wrap_text(screen, question_text, question_font, WIDTH - 200)

    # Question box (same as before)
    question_box_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 200)
    pygame.draw.rect(screen, BLUE, question_box_rect, border_radius=20)
    pygame.draw.rect(screen, WHITE, question_box_rect, 5, border_radius=20)

    line_height = question_font.get_linesize()
    text_start_y = question_box_rect.centery - (len(wrapped_lines) * line_height) // 2
    for i, line in enumerate(wrapped_lines):
        draw_text(screen, line, question_font, WHITE, question_box_rect.centerx, text_start_y + i * line_height)

    # Display who buzzed in, or a message if no one did (e.g., if timer ran out)
    if buzzer_pressed_by:
        draw_text(screen, f"{buzzer_pressed_by} BUZZED IN!", buzzer_font, RED, WIDTH // 2, HEIGHT - 100)
    else:
        draw_text(screen, "No one buzzed in!", buzzer_font, RED, WIDTH // 2, HEIGHT - 100)

    # Button to go back to the board
    back_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 50, 200, 40)
    draw_button(screen, "Back to Board", instruction_font, back_button_rect, YELLOW, BLACK)
    return back_button_rect # Return the button's rect for click detection

# --- Game Loop ---
running = True
while running:
    # Event handling: Process all events in the queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # If the user clicks the close button, exit the loop
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse click position
            mouse_pos = event.pos

            if current_state == "BOARD":
                # If on the board, check if a question cell was clicked
                for (cat, val), rect in question_rects.items():
                    # Check if mouse clicked within the cell and if the question hasn't been answered
                    if rect.collidepoint(mouse_pos) and not QUESTIONS[cat][val]["answered"]:
                        selected_category = cat
                        selected_value = val
                        current_state = "SHOWING_QUESTION" # Change state to show the question
                        buzzer_pressed_by = None # Reset buzzer status for the new question
                        buzzer_feedback_timer = 0 # Reset timer
                        print(f"Selected: {selected_category} for ${selected_value}")
                        break # Exit loop once a question is selected
            elif current_state == "SHOWING_QUESTION":
                # If showing a question, check if the "Start Buzzer Round" button was clicked
                # We need to recreate the button's rect to check collision
                temp_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 70, 300, 50)
                if temp_button_rect.collidepoint(mouse_pos):
                    current_state = "WAITING_FOR_BUZZER" # Change state to wait for buzzers
                    print("Waiting for buzzers...")
            elif current_state == "BUZZER_RESPONDED":
                # If a buzzer has responded, check if the "Back to Board" button was clicked
                # Recreate the button's rect for collision check
                temp_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 50, 200, 40)
                if temp_button_rect.collidepoint(mouse_pos):
                    # Mark the question as answered
                    if selected_category and selected_value:
                        QUESTIONS[selected_category][selected_value]["answered"] = True
                    # Reset game state variables and return to board
                    current_state = "BOARD"
                    selected_category = None
                    selected_value = None
                    buzzer_pressed_by = None
                    print("Returned to board.")

    # --- Game Logic / Drawing based on current state ---
    if current_state == "BOARD":
        draw_board()
    elif current_state == "SHOWING_QUESTION":
        draw_question_screen()
    elif current_state == "WAITING_FOR_BUZZER":
        draw_waiting_for_buzzer_screen()
        # Read serial input only if serial port is open
        if ser:
            try:
                if ser.in_waiting > 0: # Check if there's data in the serial buffer
                    line = ser.readline().decode('utf-8').strip() # Read a line and decode it
                    # Expected serial inputs from Arduino: "BUZZER1" or "BUZZER2"
                    if line == "BUZZER1":
                        buzzer_pressed_by = "PLAYER 1"
                        current_state = "BUZZER_RESPONDED" # Transition to show who buzzed
                        buzzer_feedback_timer = pygame.time.get_ticks() # Record time for auto-return
                        print("Player 1 buzzed in!")
                    elif line == "BUZZER2":
                        buzzer_pressed_by = "PLAYER 2"
                        current_state = "BUZZER_RESPONDED"
                        buzzer_feedback_timer = pygame.time.get_ticks()
                        print("Player 2 buzzed in!")
            except serial.SerialException as e:
                print(f"Serial read error: {e}")
                ser = None # If an error occurs, disable serial to prevent repeated errors
    elif current_state == "BUZZER_RESPONDED":
        draw_buzzer_responded_screen()
        # Auto-return to the board after 3 seconds if no manual click
        if pygame.time.get_ticks() - buzzer_feedback_timer > 3000:
            if selected_category and selected_value:
                QUESTIONS[selected_category][selected_value]["answered"] = True # Mark question as answered
            current_state = "BOARD" # Return to board
            selected_category = None
            selected_value = None
            buzzer_pressed_by = None
            print("Auto-returned to board after buzzer feedback.")


    # Update the full display surface to the screen
    pygame.display.flip()
    # Control the game's frame rate
    clock.tick(FPS)

# --- Cleanup ---
# Close the serial port if it was opened
if ser:
    ser.close()
    print("Serial port closed.")
# Uninitialize Pygame modules
pygame.quit()
# Exit the system
sys.exit()

if __name__ == "__main__":
    main()