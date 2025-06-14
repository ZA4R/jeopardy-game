import logging
import os
import pygame
import sys
from src.game import Game




# path setup
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(project_root)

# Define log file path
log_directory = 'logs'
log_file_path = os.path.join(log_directory, 'game_errors.log')

# Create logs directory if it doesn't exist
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
    # init
    pygame.init()

    # get screen size for fullscreen
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w
    HEIGHT = infoObject.current_h

    # set screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Main Menu")

    # set up game
    game = Game(screen)
    game.start()
                     
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()