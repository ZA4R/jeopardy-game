import logging
import pygame
from .game_utils import Round, Category, Question, Player

# get logger
logger = logging.getLogger(__name__)


# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
GRAY = (100, 100, 100)

def draw_text(surface, text, font, color, x, y, align="center", max_width=None, max_height=None):
    """
    Draws text on a surface, with optional alignment and wrapping.
    Args:
        surface (pygame.Surface): The surface to draw on.
        text (str): The text string to render.
        font (pygame.font.Font): The Pygame font object to use.
        color (tuple): RGB color for the text.
        x (int): X-coordinate for the text (based on align).
        y (int): Y-coordinate for the text (based on align).
        align (str): "center", "left", "right".
        max_width (int, optional): Maximum width for text before wrapping.
        max_height (int, optional): Maximum height. If text exceeds, it will be clipped.
    """
    words = text.split(' ')
    lines = []
    current_line = ""

    # Text wrapping logic
    for word in words:
        # Check if adding the next word exceeds max_width
        if max_width:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        else: # No max_width, just append
            current_line += " " + word if current_line else word
    lines.append(current_line)

    total_text_height = sum(font.size(line)[1] for line in lines)
    current_y_offset = 0

    if align == "center":
        current_y_offset = y - total_text_height // 2
    elif align == "top":
        current_y_offset = y
    elif align == "bottom":
        current_y_offset = y - total_text_height

    for line in lines:
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()

        if align == "center":
            text_rect.centerx = x
        elif align == "left":
            text_rect.left = x
        elif align == "right":
            text_rect.right = x

        text_rect.centery = current_y_offset + text_rect.height // 2 # Center vertically within its line
        
        # Clip if exceeding max_height
        if max_height and (text_rect.bottom > y + max_height // 2 or text_rect.top < y - max_height // 2):
             # This is a simple clipping, for more advanced clipping you might need to render to a smaller surface
             # or calculate which part of the text should be rendered. For categories, a simple clip is fine.
             pass
        else:
            surface.blit(text_surface, text_rect)
        
        current_y_offset += text_rect.height # Move to the next line positiondef draw_text(surface, text, font, color, center_x, center_y):

def draw_button(surface, text, font, rect, color, text_color, border_radius=10):
    """
    Draws a button with a slight shadow and border.
    """
    # Draw shadow for depth
    shadow_offset = 3
    pygame.draw.rect(surface, BLACK, (rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height), border_radius=border_radius)
    # Draw the main button rectangle
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    # Draw a white border around the button
    pygame.draw.rect(surface, YELLOW, rect, 2, border_radius=border_radius)
    # Draw the button text
    draw_text(surface, text, font, text_color, rect.centerx, rect.centery)
    return rect # Return the rectangle for click detection

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """
    Wraps text to fit within a given maximum width when rendered with a Pygame font.
    Handles words that are themselves longer than the max_width by breaking them.

    Args:
        text (str): The full string of text to wrap.
        font (pygame.font.Font): The Pygame font object to use for measuring text width.
        max_width (int): The maximum pixel width for each line.

    Returns:
        list[str]: A list of strings, where each string represents a wrapped line.
    """
    lines = []
    current_line_words = []

    # Helper function to break a single word that's too long for a line
    def _split_long_word(long_word: str) -> list[str]:
        """
        Breaks a single word that exceeds max_width into multiple sub-lines.
        Each sub-line will fit within max_width.
        """
        sub_lines = []
        current_segment = ""
        for char in long_word:
            # Check if adding the next character makes the segment too long
            if font.size(current_segment + char)[0] <= max_width:
                current_segment += char
            else:
                # Current segment is full, add it as a sub-line
                sub_lines.append(current_segment)
                current_segment = char # Start new segment with the current character
        
        # Add any remaining segment as the last sub-line
        if current_segment:
            sub_lines.append(current_segment)
        return sub_lines

    # Split the input text into words. This handles spaces correctly.
    words = text.split(' ')

    for word in words:
        # Measure the width of the current word
        word_width = font.size(word)[0]

        # --- Case 1: The current 'word' itself is too long for any single line ---
        if word_width > max_width:
            # If there are already words in the current line, finalize that line first
            if current_line_words:
                lines.append(' '.join(current_line_words))
                current_line_words = [] # Reset for the new, long word

            # Break the oversized word into smaller, fitting sub-lines
            broken_word_parts = _split_long_word(word)
            for part in broken_word_parts:
                lines.append(part) # Add each part as a new full line

            # Continue to the next word from the original list after processing this long one
            continue

        # --- Case 2: The current 'word' fits on the current line or starts a new one ---
        # Test if adding the current word to the current_line_words exceeds the max_width
        # Join current_line_words and the new word with a space for accurate width measurement
        test_line_string = ' '.join(current_line_words + [word])
        test_line_width = font.size(test_line_string)[0]

        if test_line_width <= max_width:
            # The word fits, so add it to the current line
            current_line_words.append(word)
        else:
            # The word does not fit on the current line
            # Finalize the current line (if it's not empty)
            if current_line_words:
                lines.append(' '.join(current_line_words))
            
            # Start a new line with the current word
            current_line_words = [word]

    # --- Final Step: Add any remaining words as the last line ---
    # After the loop, if there are any words left in current_line_words,
    # they form the last line.
    if current_line_words:
        lines.append(' '.join(current_line_words))

    return lines

def draw_board(screen: pygame.Surface, categories: list[Category], players: list[Player], 
               fonts):
    """
    Draws the main Jeopardy game board, including categories, dollar values,
    and player names/scores at the bottom.

    Args:
        screen (pygame.Surface): The Pygame screen surface to draw on.
        categories (list[Category]): A list of Category objects, expected to be of length 6.
        players (list[Player]): A list of Player objects (1 to 4 players).
        category_font (pygame.font.Font): The font for category titles.
        dollar_font (pygame.font.Font): The font for dollar values.
        player_font (pygame.font.Font): The font for player names.
        score_font (pygame.font.Font): The font for player scores.

    Returns:
        dict: A dictionary storing the Pygame Rect objects for each question cell.
              Keys are (question_obj) tuples, values are pygame.Rect objects.
    """

    width, height = screen.get_size()
    screen.fill(BLACK)

    # --- Layout Calculations for Board and Player Area ---
    num_categories = len(categories)
    if num_categories != 6:
        logger.warning(f"Expected 6 categories, but got {num_categories}. Board layout may be off.")
        if num_categories == 0:  # Avoid division by zero if no categories
            return {}

    num_question_rows = 5  # Fixed number of questions per category

    # Define vertical space ratios for different sections
    TOP_MARGIN_RATIO = 0.04          # Reduced top margin slightly
    BOTTOM_BOARD_GAP_RATIO = 0.02    # Reduced gap
    PLAYER_INFO_HEIGHT_RATIO = 0.12  # Reduced player info height slightly
    SIDE_MARGIN_RATIO = 0.03         # Reduced side margins for more board space

    # Calculate pixel dimensions for each section
    top_margin_px = height * TOP_MARGIN_RATIO
    bottom_board_gap_px = height * BOTTOM_BOARD_GAP_RATIO
    player_info_height_px = height * PLAYER_INFO_HEIGHT_RATIO
    side_margin_px = width * SIDE_MARGIN_RATIO

    # Calculate board dimensions
    board_start_y = top_margin_px
    board_end_y = height - player_info_height_px - bottom_board_gap_px
    board_height = board_end_y - board_start_y
    board_width = width - (2 * side_margin_px)

    # Cell dimensions for the board
    cell_width = board_width / num_categories
    # +1 for category header row
    cell_height = board_height / (num_question_rows + 1)

    # Starting position for the question grid cells (below category headers)
    grid_start_x = side_margin_px
    grid_start_y = board_start_y + cell_height # Start below the category headers

    question_rects = {}

    # --- Draw Category Headers ---
    for col, category in enumerate(categories):
        # Calculate the center X for the category column
        cat_x_center = grid_start_x + col * cell_width + cell_width // 2
        # Calculate the Y center for the category header cell
        cat_y_center = board_start_y + cell_height // 2
        
        # The crucial part: use max_width for text wrapping
        # Pass the effective width for the category text
        draw_text(screen, category.title.upper(), fonts["category"], YELLOW, 
                  cat_x_center, cat_y_center, 
                  align="center", max_width=int(cell_width * 0.9)) # 90% of cell_width for padding

        # Ensure questions are sorted by value for consistent display
        # Use a defensive check if questions might be missing or not sorted
        sorted_questions = sorted(category.questions, key=lambda q: q.value)

        # --- Draw Question Cells ---
        for row, question_obj in enumerate(sorted_questions):
            rect_x = grid_start_x + col * cell_width
            rect_y = grid_start_y + row * cell_height

            # Inner padding for cells
            rect_padding = max(5, int(min(cell_width, cell_height) * 0.03)) # Dynamic padding
            
            rect = pygame.Rect(rect_x + rect_padding, rect_y + rect_padding,
                               cell_width - (2 * rect_padding), cell_height - (2 * rect_padding))

            question_rects[question_obj] = rect

            if hasattr(question_obj, 'answered') and question_obj.answered:
                # Draw answered cell
                pygame.draw.rect(screen, GRAY, rect, border_radius=int(min(rect.width, rect.height) * 0.1)) # Dynamic border radius
                draw_text(screen, "X", fonts["dollar"], BLACK, rect.centerx, rect.centery)
            else:
                # Draw active question cell
                pygame.draw.rect(screen, BLUE, rect, border_radius=int(min(rect.width, rect.height) * 0.1)) # Dynamic border radius
                pygame.draw.rect(screen, WHITE, rect, max(1, int(min(rect.width, rect.height) * 0.01)), border_radius=int(min(rect.width, rect.height) * 0.1)) # White border, dynamic thickness
                
                # Use max_width for the dollar value text as well
                draw_text(screen, f"${question_obj.value}", fonts["dollar"], YELLOW, 
                          rect.centerx, rect.centery, 
                          align="center", max_width=int(rect.width * 0.8)) # 80% of rect width

    # --- Draw Player Names and Scores at the Bottom ---
    num_players = len(players)
    if num_players > 0:
        player_area_width = width
        player_cell_width = player_area_width / num_players
        player_area_y = height - player_info_height_px # Top of the player info area

        for i, player in enumerate(players):
            player_rect_x = i * player_cell_width
            player_rect = pygame.Rect(player_rect_x, player_area_y, player_cell_width, player_info_height_px)

            # Draw a background for each player's info
            player_bg_color = (30, 30, 30) # Darker gray for player background
            # Add some padding/margin to player cells
            player_inner_padding = max(5, int(player_rect.height * 0.05)) # Dynamic inner padding
            
            pygame.draw.rect(screen, player_bg_color, 
                             (player_rect.x + player_inner_padding, 
                              player_rect.y + player_inner_padding, 
                              player_rect.width - 2 * player_inner_padding, 
                              player_rect.height - 2 * player_inner_padding), 
                             border_radius=int(min(player_rect.width, player_rect.height) * 0.05))
            
            # Draw player name
            # Align player name to the top-ish of its section
            draw_text(screen, player.name.upper(), fonts["player"], WHITE, 
                      player_rect.centerx, player_rect.y + player_info_height_px * 0.3,
                      align="center", max_width=int(player_rect.width * 0.9))
            
            # Draw player score
            # Align player score to the bottom-ish of its section
            draw_text(screen, f"${player.score}", fonts["score"], YELLOW, 
                      player_rect.centerx, player_rect.y + player_info_height_px * 0.7,
                      align="center", max_width=int(player_rect.width * 0.9))

    pygame.display.flip() # Update the full display Surface to the screen
    return question_rects

def draw_question_screen(screen: pygame.Surface, question: Question, fonts):
    """
    Draws the screen displaying the selected question.
    Includes a button to start the buzzer round.
    """
    screen.fill(BLACK) # Clear the screen

    width, height = screen.get_size()

    # Wrap the question text to fit within the screen width
    wrapped_lines = wrap_text(question.clue, fonts["question"], width - 200)

    # Define the rectangle for the question box
    question_box_rect = pygame.Rect(50, 50, width - 100, height - 200)
    pygame.draw.rect(screen, BLUE, question_box_rect, border_radius=20) # Blue background
    pygame.draw.rect(screen, WHITE, question_box_rect, 5, border_radius=20) # White border

    # Draw the wrapped question text, centered vertically within the box
    line_height = fonts["question"].get_linesize()
    text_start_y = question_box_rect.centery - (len(wrapped_lines) * line_height) // 2
    for i, line in enumerate(wrapped_lines):
        draw_text(screen, line, fonts["question"], WHITE, question_box_rect.centerx, text_start_y + i * line_height)
    pygame.display.flip()

def draw_main_menu(surface: pygame.Surface, fonts: dict) -> dict[str, pygame.Rect]:
    """
    Draws the main menu screen with a large, wrapped title and buttons.
    The title takes up more screen space and wraps properly.
    The start button is positioned closer to the bottom of the screen.

    Args:
        surface (pygame.Surface): The surface to draw on (e.g., the screen).
        fonts (dict): A dictionary of Pygame font objects.
                      Expected keys: "title" (for the main title),
                      "question" (for the START GAME button text),
                      "category" (for the 'X' exit button text).

    Returns:
        dict: A dictionary containing the pygame.Rect objects for each button,
              e.g., {'start_button': rect, 'exit_button': rect}.
    """
    screen_width, screen_height = surface.get_size()

    # Fill the background with the Jeopardy Blue
    surface.fill(BLUE)

    # --- Draw the Game Title (Large & Wrapped) ---
    title_text = "DUNCAN'S DEFINITIVELY NOT A GAME SHOW ABOUT QUESTIONS & ANSWERS"
    
    # Define the max width the title should occupy (e.g., 85% of screen width)
    max_title_render_width = int(screen_width * 0.85)

    # Get the title font from the provided dictionary
    title_font = fonts["title"]

    # Use the provided wrap_text function
    wrapped_lines = wrap_text(title_text, title_font, max_title_render_width)

    # Calculate the total height of the wrapped title block
    total_title_height = len(wrapped_lines) * title_font.get_height()
    
    # Center the entire title block vertically in the upper portion
    # For example, vertically centered within the top 30% of the screen.
    # This leaves more space below for buttons.
    title_block_center_y = int(screen_height * 0.25) # Position the center of the text block
    title_start_y = title_block_center_y - (total_title_height // 2)


    # Render and blit each wrapped line
    for i, line in enumerate(wrapped_lines):
        line_y_pos = title_start_y + (i * title_font.get_height())
        draw_text(surface, line, title_font, YELLOW, screen_width / 2, line_y_pos, align="center")


    # --- Define Button Properties ---
    main_button_width = 350
    main_button_height = 100 # Adjusted for a more compact layout
    button_margin_from_bottom = 80 # Distance from screen bottom to start button

    # Calculate Start Button Position (closer to bottom)
    start_button_rect = pygame.Rect(
        (screen_width / 2) - (main_button_width / 2), # Centered horizontally
        screen_height - main_button_height - button_margin_from_bottom, # Positioned from the bottom
        main_button_width,
        main_button_height
    )
    
    # --- Draw Buttons ---
    buttons = {}

    # Start Button
    buttons['start_button'] = draw_button(
        surface, "START GAME", fonts["question"], start_button_rect, # Using "question" font for button text
        BLUE, YELLOW # Button fill color, text color
    )

    # --- Top-Right Exit Button ---
    # This button remains in the top-right corner as a small "X"
    top_right_button_width = 60 # Smaller for a close button look
    top_right_button_height = 60 # Smaller for a close button look
    padding = 20 # Padding from the top and right edges

    top_right_exit_button_rect = pygame.Rect(
        screen_width - top_right_button_width - padding, # X: Screen width - button width - padding
        padding,                                       # Y: Padding from top
        top_right_button_width,
        top_right_button_height
    )
    buttons['exit_button'] = draw_button(
        surface, "X", fonts["category"], top_right_exit_button_rect, # Using "category" font for "X"
        RED, BLACK # Button fill color, text color
    )

    pygame.display.flip()
    
    return buttons

def display_buzzed(font: pygame.font.Font, player: Player, screen: pygame.Surface, fonts: dict) -> None:
    """
    Displays a message indicating which player buzzed in, centered on a black background.
    Additionally, displays instructions for handling correct/incorrect answers.

    Args:
        font (pygame.font.Font): The Pygame font object to render the main buzz message.
        player (Player): The Player object whose name will be displayed.
        screen (pygame.Surface): The Pygame screen surface to draw on.
        fonts (dict): A dictionary of Pygame font objects.
                      Expected key: "action_prompt" for the instruction text.
    """
    screen.fill(BLACK) 
    width, height = screen.get_size()
    
    screen_center_x = width // 2
    screen_center_y = height // 2

    message = f"{player.name} buzzed in!"

    # It takes x, y as the center coordinates when align="center".
    # No max_width or max_height is applied here to allow the text to fill the center as much as needed.
    draw_text(screen, message, font, WHITE, screen_center_x, screen_center_y, align="center")

    # --- Add bottom left and bottom right instructions ---
    padding = 20
    bottom_y = height - padding

    # Bottom Left: "Press space for correct answers"
    correct_prompt = "Press space for correct answers"
    draw_text(screen, correct_prompt, fonts["player"], WHITE, 
              padding, bottom_y, align="left", max_width=int(width * 0.4))

    # Bottom Right: "Press backspace for incorrect answers"
    incorrect_prompt = "Press backspace for incorrect answers"
    draw_text(screen, incorrect_prompt, fonts["player"], WHITE, 
              width - padding, bottom_y, align="right", max_width=int(width * 0.4))

    pygame.display.flip()

def display_correct_answer(screen: pygame.Surface, question: Question, fonts) -> None:
    """
    Displays the correct answer to a question and a prompt to continue.

    Args:
        screen (pygame.Surface): The Pygame screen surface to draw on.
        question (Question): The Question object containing the answer.
        fonts (dict): A dictionary of Pygame font objects.
    """
    screen.fill(BLACK) 
    width, height = screen.get_size()

    # --- Display the Answer (Upper 75%) ---
    answer_area_height = height * 0.75
    answer_area_center_y = answer_area_height / 2
    answer_text_max_width = width * 0.9 # 90% of screen width for padding

    answer_message = f"Answer: {question.answer}"

    # Use draw_text to render the answer, centered within its allocated area
    draw_text(
        screen,
        answer_message,
        fonts["question"],
        WHITE,
        width // 2,
        answer_area_center_y,
        align="center",
        max_width=int(answer_text_max_width)
    )

    # --- Display "Press space to continue" (Bottom 25%) ---
    continue_message_area_height = height * 0.25
    continue_message_area_center_y = height - (continue_message_area_height / 2)
    continue_message = "Press space to continue"

    # Use draw_text to render the continue message, centered within its allocated area
    draw_text(
        screen,
        continue_message,
        fonts["player"], # Use a smaller font for this message
        WHITE,
        width // 2,
        continue_message_area_center_y,
        align="center"
    )

    pygame.display.flip()

def display_final_jeopardy_title(screen: pygame.Surface, fonts: dict, players: list) -> None:
    """
    Displays "FINAL JEOPARDY" in yellow text on a blue background,
    and then lists player names (yellow) and scores (white)
    in descending order by score, centered below the title.

    Args:
        screen (pygame.Surface): The Pygame screen surface to draw on.
        fonts (dict): A dictionary of Pygame font objects.
                      Expected keys: "title" (for "FINAL JEOPARDY"),
                      "player" (for player names), and "score" (for player scores).
        players (list): A list of player objects. Each player object should have
                        'name' (str) and 'score' (int) attributes.
    """
    screen.fill(BLUE) # Fill the background with the Jeopardy! blue

    width, height = screen.get_size()
    
    # --- Display "FINAL JEOPARDY" Title ---
    title_message = "FINAL JEOPARDY"
    
    # Position the title in the upper half, centered horizontally.
    # We want it to occupy a chunk in the upper part, not just the exact quarter mark.
    # Let's say its vertical center is at 25% of screen height.
    title_center_x = width // 2
    title_center_y = int(height * 0.25) # 25% down from the top

    draw_text(
        screen,
        title_message,
        fonts["title"], # Using 'title' font from your dict
        YELLOW,
        title_center_x,
        title_center_y,
        align="center",
        max_width=int(width * 0.9) # Occupy 90% of the screen width for the text
    )

    # --- Display Player Names and Scores ---
    
    # 1. Sort players by score in descending order.
    sorted_players = sorted(players, key=lambda p: p.score, reverse=True)

    # 2. Define vertical spacing and font sizes for player display.
    player_name_font = fonts["player"]
    player_score_font = fonts["score"]
    
    # Calculate line height for each player entry, considering both fonts and adding padding.
    line_height = max(player_name_font.get_height(), player_score_font.get_height()) + 15 
    
    # 3. Calculate the total height the block of player information will occupy.
    total_players_block_height = len(sorted_players) * line_height

    # 4. Determine the available vertical space for the player list.
    # This space is from the *bottom of the title* down to the *bottom of the screen*.
    # Calculate the Y-coordinate where the title text effectively ends.
    title_text_bottom_y = title_center_y + (fonts["title"].get_height() // 2)

    # The region for players starts just below the title and goes to the bottom.
    # Add a buffer for visual separation.
    region_start_y = title_text_bottom_y + 30 # 30 pixels buffer after title
    region_end_y = height # Bottom of the screen

    # Calculate the exact vertical center of this *remaining region*.
    # This is the point where the middle of our player block should sit.
    center_of_remaining_region_y = region_start_y + (region_end_y - region_start_y) // 2

    # 5. Calculate the starting Y-position for the *first* player.
    # To center the block, we subtract half of the block's total height from the center of the region.
    start_y_for_players = center_of_remaining_region_y - (total_players_block_height // 2)

    # 6. Define horizontal positioning for names (left-aligned) and scores (right-aligned).
    # These are horizontal offsets from the screen center for name and score columns.
    # Adjust these values based on how wide you want your "columns" to be.
    name_column_x_pos = int(width * 0.3) # 30% from the left edge for name's midleft
    score_column_x_pos = int(width * 0.7) # 70% from the left edge for score's midright

    # 7. Draw each player's name and score.
    for i, player in enumerate(sorted_players):
        # Current player's Y position within the vertically centered block.
        y_pos = start_y_for_players + i * line_height
        
        # Player Name (aligned left, in YELLOW)
        draw_text(
            screen,
            player.name,
            player_name_font, # Use 'player' font from your dict
            YELLOW,           # Name color is YELLOW
            name_column_x_pos,
            y_pos,
            align="left"
        )
        
        # Player Score (aligned right, in WHITE)
        draw_text(
            screen,
            f"${player.score:,}", # Format score with comma for thousands
            player_score_font,    # Use 'score' font from your dict
            WHITE,                # Score color is WHITE
            score_column_x_pos,
            y_pos,
            align="right"
        )

    pygame.display.flip() # Update the display to show all changes