from __future__ import annotations

class Round:
    def __init__(self):
        self.categories: list[Category] = self.get_random_categories()

    def get_random_categories(self) -> list[Category]:
        """
        Returns a list of six random categories populated with questions.
        """
        pass
class Category:
    def __init__(self, title: str):
        # pull questions from db
        self.title = title
        self.questions = self.get_random_questions(title)

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

    Notes: 
        value = -1 defines a final jeopardy question
    """
    answered = False
    
    def __init__(self, clue: str, answer: str, value: int, category: str, origin: str):
        self.clue = clue
        self.answer = answer
        self.value = value
        self.category = category
        self.origin = origin

class Player:
    name = "Steve"
    score = 0


    