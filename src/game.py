from __future__ import annotations

from pygame import Surface
from .display import draw_board, draw_question_screen
from.game_utils import Question, Category, Round, Player
from.music import play_music, stop_music, set_music_volume, final_music_list, victory_music_list
import logging

# get logger
logger = logging.getLogger(__name__)
class Game:
    """
    Responsible for managing and executing a game.

    Attributes:
        players: list of player objects
        screen: pygame surface on which the game will appear (set by main.py)
        board: GameBoard object used to keep track of board state
    """
    players = [] 
    screen: Surface 
    def __init__(self) -> None:
        self.board = GameBoard
        self.add_players(4) # 4 hardcoded until basic outline complete

    def start(self):
        for round in self.board.rounds:
            self.play_round(round)
        self.play_final()
    
    def play_round(self, round: Round):
        # implement daily doubles
        running = True
        while running:
            pass

    def play_final(self):
        # need to figure out how betting system will work
        pass

    def add_players(self, num):
        if num < 1 or num + len(self.players) > 6:
            logger.error(f"cannot add {num} players (max of 6)")
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
    rounds = []
    def __init__(self, round_num):
        for _ in range(round_num):
            self.rounds.append(Round())
        self.round_final: Question = self.get_random_question(-1)
    
    def get_random_question(self, value: int) -> Question:
        """Returns random Question with given questino value.

        Args:
            value (int): desired $ value, -1 denotes final jeopardy

        Returns:
            Question: object containing question attributes
        """
        pass


