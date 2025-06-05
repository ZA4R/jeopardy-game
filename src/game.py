from __future__ import annotations
from enum import Enum


class GameState(Enum):
    """
    Defines possible game states.
    """
    
    BOARD = "b"
    SHOWING_QUESTION = "sq"

class GameBoard:
    """
    GameBoard keeps track of the game board state throughout the game.

    Attributes:
        round_one_categories: list[Category]
        round_two_categories: list[Category]
        round_final: Question
    """
    def __init__(self):
        self.round_one_categories: list[Category] = get_random_categories()
        self.round_two_categories: list[Category] = get_random_categories()
        self.round_final: Question = get_question(1000)
    
    def get_random_categories(self) -> list[Category]:
        """
        Returns a list of six random categories populated with questions.
        """
        pass
    
    def get_random_question(self, value: int) -> Question:
        """Returns random Questino with given questino value.

        Args:
            value (int): random question $ value

        Returns:
            Question: object containing question attributes
        """
        pass

class Category:
    def __init__(self, name: str):
        # pull questions from db
        self.name = name
        self.questions = get_random_questions(name)

    def get_random_questions(self, category: str="") -> list[Question]:
        """
        Returns list[Question] for given category, one question per value.

        Params:
            category: str="" - determines question category, default is random
        """
        pass

class Question:
    """
    Represents a question including its clue, answer, value, category, and origin.
    """
    def __init__(self, clue: str, answer: str, value: int, category: str, origin: str):
        self.clue = clue
        self.answer = answer
        self.value = value
        self.category = category
        self.origin = origin
