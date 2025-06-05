import os

# get current dir and project root
current_dir = os.path.dirname(os.path.abspath(__file__))
proj_root = os.path.abspath(os.path.join(current_dir, ".."))



# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
GRAY = (100, 100, 100)

# fonts
PIXEL_FONT = os.path.join(proj_root, "assets", "fonts", "pixel.ttf")
category_font = pygame.font.Font(PIXEL_FONT, 40)
dollar_font = pygame.font.Font(PIXEL_FONT, 60)
question_font = pygame.font.Font(PIXEL_FONT, 45)
instruction_font = pygame.font.Font(PIXEL_FONT, 30)
buzzer_font = pygame.font.Font(PIXEL_FONT, 70)


def draw_text(surface, text, font, color, center_x, center_y):
    """
    Helper function to render and draw text centered at given coordinates.
    """
    text_surface = font.render(text, False, color)
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


def draw_board(board: GameBoard, width, height):
    """
    Draws the main Jeopardy game board, including categories and dollar values.
    """
    screen.fill(BLACK)
    # Draw category headers at the top
    for i, category in enumerate(CATEGORIES):
        cat_x = start_x + i * cell_width + cell_width // 2
        draw_text(screen, category, category_font, YELLOW, cat_x, start_y - 50)

    # Dictionary to store the Pygame Rect objects for each question cell.
    # This is used for click detection.
    question_rects = {} # {(category_name, dollar_value): pygame.Rect}

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
    return question_rects

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
