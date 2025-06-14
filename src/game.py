from __future__ import annotations
from turtle import Turtle

from pygame import Surface
import pygame
from .display import draw_board, draw_question_screen, draw_main_menu
from .game_utils import Question, Category, Round, Player
from .music import play_music, stop_music, set_music_volume, load_music_files, final_music_list, victory_music_list, title_music_list
import logging
import os
import sqlite3
import serial
import sys
import os

# get current dir and project root
current_dir = os.path.dirname(os.path.abspath(__file__))
proj_root = os.path.abspath(os.path.join(current_dir, ".."))

# get logger
logger = logging.getLogger(__name__)

# path to db
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
db_path = os.path.join(parent_dir, "data", "questions.db")
class Game:
    """
    Responsible for managing and executing a game.

    Attributes:
        players: list of player objects
        screen: pygame surface on which the game will appear (set by main.py)
        board: GameBoard object used to keep track of board state
    """ 

    def __init__(self, screen: Surface):
        self.board = GameBoard(2)
        self.players = []
        self.add_players(4) # 4 hardcoded until basic outline complete
        self.screen = screen

        # device specific port where arduino is connected
        SERIAL_PORT = 'COM3'
        # match arduino, 9600 bits is standard
        BAUD_RATE = 9600

        # serial setup
        #ser = None
        #try:
        #    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        #    if ser.is_open:
        #        logger.info(f"Serial port open: {SERIAL_PORT}")
        #    else:
        #        logger.error(f"Unable to open: {SERIAL_PORT}")
#
        #except serial.SerialException as e:
        #    logger.error(f"Unable to connect to port: {SERIAL_PORT}: {e}")
        #    sys.exit()
        #self.serial = ser

        
        # font setup
        pygame.font.init()
        try:
            PIXEL_FONT = os.path.join(proj_root, "assets", "fonts", "pixel.ttf")
        except pygame.error as e:
            logger.error(f"Unable to load font: {e}")
        except Exception as e:
            logger.error(f"Unable to load font: {e}")
        global category_font, dollar_font, player_font, score_font

        height = pygame.display.Info().current_h
        category_font_size = int(height * 0.035) 
        dollar_font_size = int(height * 0.05)   
        player_font_size = int(height * 0.03)   
        score_font_size = int(height * 0.04)    
        question_font_size = int(height * 0.06)
        title_font_size = int(height * 0.08)
        category_font = pygame.font.Font(PIXEL_FONT, category_font_size)
        dollar_font = pygame.font.Font(PIXEL_FONT, dollar_font_size)
        player_font = pygame.font.Font(PIXEL_FONT, player_font_size)
        score_font = pygame.font.Font(PIXEL_FONT, score_font_size)
        question_font = pygame.font.Font(PIXEL_FONT, question_font_size)
        title_font = pygame.font.Font(PIXEL_FONT, title_font_size)

        self.fonts = {"category": category_font, "dollar": dollar_font, "player": player_font, "score": score_font, 
                      "question": question_font, "title": title_font}

        # music setup
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096) # reduce buffer by powers of two if aduio lags
        # music directory
        MUSIC_DIR = os.path.join(proj_root, "assets", "music")
        load_music_files(MUSIC_DIR)

    def start(self):
        # main menu
        buttons = draw_main_menu(self.screen, self.fonts)
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
                        running = False

        stop_music()
        round_num = 1
        for round in self.board.rounds:
            self.play_round(round, round_num)
            round_num += 1
        self.play_final()
    
    def play_round(self, round: Round, round_num : int):
        # daily doubles
        num_of_dd_left = round_num

        # scale category values for given round
        for cat in round.categories:
            for q in cat.questions:
                q.value *= round_num

        running = True
        while running:
            # update board
            # quesntion_rects is dict {(category)}
            question_rects = draw_board(self.screen, round.categories, self.players, self.fonts)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for q in question_rects:
                        if question_rects[q].collidepoint(pos):
                            logger.info(f"Question selected: {q}")
                            draw_question_screen(self.screen, q, self.fonts)
                            self.buzzer_round(q)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
        #if self.serial:
        #    self.serial.close()

    def play_final(self):
        play_music(final_music_list[0])
        draw_question_screen(self.screen, self.board.final_q, self.fonts)
        # need to figure out how betting system will work
        while True:
            pass
        
    def buzzer_round(self, q: Question):
        q.answered = True

    def add_players(self, num):
        if num < 1 or num + len(self.players) > 4:
            logger.error(f"cannot add {num} players (max of 4)")
            return

        for _ in range(num):
            self.players.append(Player())

    def remove_players(self, num):
        if num < 1:
            logger.error(f"cannot remove {num} players (min 1)")
            return
        if num > len(self.players):
            logger.error(f"cannot remove {num} players (max of {len(self.players)})")
            return

        for _ in range(num):
            del self.players[len(self.players) - 1]
        
class GameBoard:
    """
    GameBoard keeps track of board state.

    Attributes:
        rounds: list[Round]
        round_final: Question
    """
    def __init__(self, round_num):
        self.rounds = []
        for _ in range(round_num):
            self.rounds.append(Round())
        self.set_final_q()
    
    def set_final_q(self):
        """Returns random Question with given questino value.

        Args:
            value (int): desired $ value, -1 denotes final jeopardy

        Returns:
            Question: object containing question attributes
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except Exception as e:
            logger.error(f"Couldn't connect to db for random quesiton: {e}")
            return

        sql_query = f"""
        SELECT clue,answer,value,category,origin
        FROM questions
        WHERE value = -1
        ORDER BY RANDOM()
        LIMIT 1
        """

        cursor.execute(sql_query)
        question_tuple = cursor.fetchone()



        self.final_q = Question(question_tuple[0],question_tuple[1],question_tuple[2],question_tuple[3],question_tuple[4])

        if cursor:
            cursor.close()
        if conn:
            conn.close()


