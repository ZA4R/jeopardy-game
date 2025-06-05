
class GameBoard:
    """
    GameBoard keeps track of the game board state throughout the game.

    Attributes:
        round_one_categories: list[Category]
        round_two_categories: list[Category]
        round_final: Question
    """
    def __init__(self):
        self.round_one_categories = get_random_categories()
        self.round_two_categories = get_random_categories()
        self.round_final = get_question(1000)
    
    def get_random_categories() -> list[Category]:
        """
        Returns a list of six random categories populated with questions.
        """
        pass
    
    def get_random_question(value: int) -> Question:
        """
        Returns Question from db.

        Params:
            value: int - $ value of question
        """
        pass

class Category:
    def __init__(self, name: str):
        # pull questions from db
        self.name = name
        self.questions = get_random_questions(name)

    def get_random_questions(category: str="") -> list[Question]:
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
