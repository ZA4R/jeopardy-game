from __future__ import annotations

from pygame import Surface
import pygame
from .display import draw_board, draw_question_screen, draw_main_menu, display_buzzed, display_correct_answer, display_final_jeopardy_title
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
        self.board = GameBoard(2) # two rounds are standard, will be variable when settings are implemented
        self.players : list[Player] = []
        self.add_players(3) # 3 player games are standard, will be variable when settings are implemented
        self.screen = screen

        # device specific port where arduino is connected
        SERIAL_PORT = 'COM4'
        # match arduino, 9600 bits is standard
        BAUD_RATE = 9600

        # serial setup
        self.serial = None
        try:
            self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            if self.serial.is_open:
                logger.info(f"Serial port open: {SERIAL_PORT}")
            else:
                logger.error(f"Unable to open: {SERIAL_PORT}")

        except Exception as e:
            logger.error(f"Unable to connect to port: {SERIAL_PORT}\n because of: {e}")
            self.quit()

        
        # font setup
        pygame.font.init()
        try:
            PIXEL_FONT = os.path.join(proj_root, "assets", "fonts", "pixel.ttf")
        except pygame.error as e:
            logger.error(f"Unable to load font: {e}")
        except Exception as e:
            logger.error(f"Unable to load font: {e}")

        height = pygame.display.Info().current_h
        category_font_size = int(height * 0.035) 
        dollar_font_size = int(height * 0.05)   
        player_font_size = int(height * 0.03)   
        score_font_size = int(height * 0.04)    
        question_font_size = int(height * 0.06)
        title_font_size = int(height * 0.1)
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

        stop_music()
        round_num = 1
        for round in self.board.rounds:
            self.play_round(round, round_num)
            round_num += 1
        self.play_final()
    
    def play_round(self, round: Round, round_num : int):
        # daily doubles to implement

        # scale category values for given round
        for cat in round.categories:
            for q in cat.questions:
                q.value *= round_num

        running = True
        while running:
            # update board
            # quesntion_rects is dict {Question: rect}
            question_rects = draw_board(self.screen, round.categories, self.players, self.fonts)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for q in question_rects:
                        if question_rects[q].collidepoint(pos):
                            self.buzzer_round(q)

                            # exit round if all questions have been answered
                            if check_for_all_answered(question_rects):
                                running = False
                                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    

    def play_final(self):
        # awaiting betting implementation
        play_music(final_music_list[0])
        display_final_jeopardy_title(self.screen, self.fonts, self.players)

        # clear events
        pygame.event.get()

        # wait for host to continue
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting = False

        draw_question_screen(self.screen, self.board.final_q, self.fonts)
        
        start_final = pygame.time.get_ticks()


        # clear events
        pygame.event.get()
        # 30 second timer for final jeopardy
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                # redundant to ensure holding down a button doesn't interfere with timer
                if (pygame.time.get_ticks() - start_final > 30000):
                    running = False
            if (pygame.time.get_ticks() - start_final > 30000):
                running = False

        display_correct_answer(self.screen, self.board.final_q, self.fonts)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            running = False

        # end game for now
        # create winner screen, betting screen, betting system in future
        self.quit()

    def reset_buzzed(self):
        for p in self.players:
            p.answered = False
    
        
    def wait_for_buzz_in(self, ser: serial.Serial):
        # wait for serial response
        while ser.in_waiting == 0:
            pass
        
        byte_response = ser.readline()
        return byte_response.decode("utf-8").strip()

    def handle_buzz_in_response(self, ser_response: str, question_value: int) -> bool:
        """Manages system response to timeouts and buzz-ins. Returns False to exit buzz-in round.
        Args:
            ser (serial.Serial): serial connection to buzzer system
            ser_response (str): cleaned str containing serial response to "start" command

        Returns:
            bool: Returns False when buzzer round should end
        """

        # quit round if timeout occured
        if ser_response == "timeout":
            return False

        # response should be index of player
        # check for bad serial response
        try:
            resp = int(ser_response)
        except ValueError:
            logger.error(f"Incorrect serial usage detected. {ser_response} should be the index of the player that buzzed")
            self.quit()

        if resp < 0 or resp > len(self.players) - 1:
            logger.error(f"Incorrect serial usage detected. {resp} should be the index of the player that buzzed")
            self.quit()

        buzzed_player: Player = self.players[resp]
        buzzed_player.answered = True

        # display buzzed in screen
        # update player score based on host response
        display_buzzed(self.fonts["question"], buzzed_player, self.screen, self.fonts)

        # clear event list
        pygame.event.get()

        # wait for host response
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # update score
                        buzzed_player.score += question_value

                        # inform buzzer system
                        if self.serial:
                            self.serial.write(b"correct\n")

                        # exit round 
                        return False

                    if event.key == pygame.K_BACKSPACE:
                        # update score
                        buzzed_player.score -= question_value

                        # exit loop to check if all players have answered
                        waiting = False

        # check if all players have buzzed
        for player in self.players:
            if not player.answered:
                # send buzzed_in player to serial to lock them out for round
                idx = f"{resp}\n"
                if self.serial:
                    self.serial.write(idx.encode("utf-8"))
                # continue the round
                return True

        # all players have buzzed in, inform system and end round
        if self.serial:
            self.serial.write(b"all players buzzed")
        return False

    def buzzer_round(self, q: Question):
        # clear event list
        pygame.event.get()
        
        draw_question_screen(self.screen, q, self.fonts)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.serial:
                            self.serial.write(b"start\n")

                        buzzing = True
                        while buzzing:
                            draw_question_screen(self.screen, q, self.fonts)
                            if self.serial:
                                ser_response = self.wait_for_buzz_in(self.serial)

                            # returns False if player gets correct answer or out of players
                            buzzing = self.handle_buzz_in_response(ser_response, q.value)
                        running = False
                        


        q.answered = True
        self.reset_buzzed()
        display_correct_answer(self.screen, q, self.fonts)
        # clear events
        pygame.event.get() 
        # wait until space to continue
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False

    
    def quit(self):
        if self.serial:
            self.serial.close()
        if pygame:
            pygame.quit()
        sys.exit()

    def add_players(self, num):
        if num < 1 or num + len(self.players) > 3:
            logger.error(f"cannot add {num} players (max of 3)")
            return

        for i in range(num):
            self.players.append(Player(i + 1))

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


# helper functions

def check_for_all_answered(question_rects: dict[Question, pygame.rect.Rect]) -> bool:
    """Checks if every question in dict has been answered. Returns bool answer.

    Args:
        question_rects (dict[Question, pygame.rect.Rect]): Gameboard dictionary containing questions
    """

    for q in question_rects:
        if not q.answered:
            return False
    return True

