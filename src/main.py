import logging
import os
import pygame
import sys
import pyserial
import time
from data.settings import FPS

# consts
MAX_PLAYERS = 6

# setup
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

# Define the log file path
log_directory = 'logs'
log_file_path = os.path.join(log_directory, 'game_errors.log')

# Create the logs directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout), 
        logging.FileHandler(log_file_path)
    ]
)

logger = logging.getLogger(__name__)

def main():
    # inits
    pygame.mixer.init()
    pygame.font.init()
    pygame.init()
    clock = pygame.time.Clock()
    
    # device specific port where arduino is connected
    SERIAL_PORT = 'COM3'
    # match arduino, 9600 bits is standard
    BAUD_RATE = 9600

    # serial setup
    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        logger.info("Connected to port: {SERIAL_PORT}")
    except serial.SerialException as e:
        logger.error("Unable to connect to port: {SERIAL_PORT}: {e}")
        sys.exit()

    # get screen size for fullscreen
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w
    HEIGHT = infoObject.current_h

    # set screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Main Menu")

    

    return

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