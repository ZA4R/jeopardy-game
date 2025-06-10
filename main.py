import logging
import os
from pdb import run
import pygame
import sys
import serial
from src.display import draw_main_menu
from src.game import Game
from src.music import load_music_files, play_music, stop_music, set_music_volume, final_music_list, victory_music_list, title_music_list



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
    
    # device specific port where arduino is connected
    SERIAL_PORT = 'COM3'
    # match arduino, 9600 bits is standard
    BAUD_RATE = 9600

    # serial setup
    ser = None
    try:
        #ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        logger.info("Connected to port: {SERIAL_PORT}")

        #if ser.is_open:
        #    logger.info(f"Serial port open: {SERIAL_PORT}")
        #else:
        #    logger.error(f"Unable to open: {SERIAL_PORT}")

    except serial.SerialException as e:
        logger.error("Unable to connect to port: {SERIAL_PORT}: {e}")
        sys.exit()
    
    # music setup
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096) # reduce buffer by powers of two if aduio lags
    # music directory
    MUSIC_DIR = os.path.join(project_root, "assets", "music")
    load_music_files(MUSIC_DIR)

    # get screen size for fullscreen
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w
    HEIGHT = infoObject.current_h

    # set screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Main Menu")

    # set up game
    game = Game()
    game.screen = screen

    # main menu
    buttons = draw_main_menu(screen)
    play_music(title_music_list[0])

    
    running = True
    while running:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if buttons['exit_button'].collidepoint(pos):
                    running = False
                elif buttons['start_button'].collidepoint(pos):
                    game.start()
                     
    if ser:
        ser.close()
    pygame.quit()
    sys.exit()
    return

if __name__ == "__main__":
    main()