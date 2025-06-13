from __future__ import annotations
from locale import currency
import sqlite3
import os
import logging

# logger
logger = logging.getLogger(__name__)

# path to db
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
db_path = os.path.join(parent_dir, "data", "questions.db")

class Round:
    def __init__(self):
        self.categories: list[Category] = []
        self.get_random_categories()

    def get_random_categories(self):
        """
        Returns a list of six random categories populated with questions.
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except Exception as e:
            logger.error(f"Unable to connect to db: {e}")
            return []

        # selects 6 random categories
        # returns as list of tuples
        # WHERE value = 100 ensures there is a set of questions aka not a final jeopardy only category 
        try:
            cursor.execute("SELECT DISTINCT category FROM questions WHERE value = 100 ORDER BY RANDOM() LIMIT 6")
        except Exception as e:
            logger.error(f"Unable to exectue category search query: {e}")
            
        category_tuples = cursor.fetchall()
        for cat in category_tuples:
            self.categories.append(Category(cat[0]))

        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
class Category:
    def __init__(self, title: str):
        # pull questions from db
        self.title = title
        self.questions: list[Question] = []
        self.get_random_questions(title)

    def get_random_questions(self, category: str):
        """
        Returns list[Question] for given category, one question per value.

        Params:
            category: str="" - determines question category, must have 5 questions with distinct values
        """
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except Exception as e:
            logger.error(f"Unable to connect to db: {e}")
            return []

        # selects 6 random categories
        # returns as list of tuples
        # WHERE value = 100 ensures there is a set of questions aka not a final jeopardy only category

        sql_query = f"""
        SELECT
            clue,
            answer,
            value,
            category,
            origin
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY value ORDER BY RANDOM()) as rn_per_value,
                RANDOM() as overall_random_sort
            FROM
                questions
            WHERE
                category = '{category}'
        ) AS RankedQuestions
        WHERE
            rn_per_value = 1
        ORDER BY
            overall_random_sort
        LIMIT 5;
        """ 
        try:
            cursor.execute(sql_query)
        except Exception as e:
            logger.error(f"Unable to exectue category search query: {e}")
            return
            
        question_tuples = cursor.fetchall()
        for q in question_tuples:
            self.questions.append(Question(q[0],q[1],q[2],q[3],q[4]))
        sorted(self.questions, key= lambda q: q.value, reverse=False)

        if cursor:
            cursor.close()
        if conn:
            conn.close()
class Question:
    """
    Represents a question including its clue, answer, value, category, and origin.

    Notes: 
        value = -1 defines a final jeopardy question
    """
    
    def __init__(self, clue: str, answer: str, value: int, category: str, origin: str):
        self.clue = clue
        self.answer = answer
        self.value = value
        self.category = category
        self.origin = origin
        self.ansewred = False

class Player:
    name = "Steve"
    score = 0


    