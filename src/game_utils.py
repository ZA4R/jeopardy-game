from __future__ import annotations
from locale import currency
import sqlite3
import os
import logging
import random

# logger
logger = logging.getLogger(__name__)

# path to db
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
db_path = os.path.join(parent_dir, "data", "questions.db")

class Round:
    def __init__(self):
        self.categories: list[Category] = []
        cats = self.get_eligible_categories(6)
        for cat in cats:
            self.categories.append(Category(cat))

    def get_eligible_categories(self, num_categories: int = 6) -> list[str]:
        """
        Selects N random categories that have at least one question for each
        of the 5 standard dollar values (100, 200, 300, 400, 500).
        It explicitly excludes categories that only contain questions with value -1.
        """
        eligible_categories = []
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except Exception as e:
            logger.error(f"Unable to connect to db: {e}")
            return []

        # SQL to find categories that have at least one question for each of the 5 values
        # AND ensure they have questions with values other than -1
        sql_query = """
        SELECT category
        FROM questions
        WHERE value IN (100, 200, 300, 400, 500)
        GROUP BY category
        HAVING COUNT(DISTINCT value) = 5
        AND SUM(CASE WHEN value != -1 THEN 1 ELSE 0 END) > 0; -- Ensures it's not a -1 only category
        """
        
        try:
            cursor.execute(sql_query)
            all_eligible_titles = [row[0] for row in cursor.fetchall()]
            
            if len(all_eligible_titles) == 0:
                logger.critical("No categories found in the database that meet the criteria (5 unique standard values and not -1 only). Please check your database.")
                return []

            if len(all_eligible_titles) < num_categories:
                logger.warning(f"Only found {len(all_eligible_titles)} categories with 5 unique standard values. Requesting {num_categories}. Will return fewer.")
                # Return all available eligible categories, even if fewer than requested
                return all_eligible_titles 
                
            # Randomly select num_categories from the eligible list
            eligible_categories = random.sample(all_eligible_titles, num_categories)

        except sqlite3.Error as e:
            logger.error(f"Database error fetching eligible categories: {e}")
        finally:
            conn.close()
            
        return eligible_categories        
class Category:
    def __init__(self, title: str):
        # pull questions from db
        self.title = title
        self.questions: list[Question] = []
        self._get_unique_value_questions(title)

    def _get_unique_value_questions(self, category_title: str):
        """
        Attempts to retrieve one question for each of the standard Jeopardy dollar values
        (100, 200, 300, 400, 500) for a given category.
        If a value is not found, it will not be included.
        """
        desired_values = [100, 200, 300, 400, 500]
        found_questions = []

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except Exception as e:
            logger.error(f"Unable to connect to db: {e}")
            return []

        for value in desired_values:
            sql_query = """
            SELECT clue, answer, value, category, origin
            FROM questions
            WHERE category = ? AND value = ?
            ORDER BY RANDOM()
            LIMIT 1;
            """
            try:
                # --- CRITICAL CHANGE HERE ---
                # Pass a tuple of parameters as the second argument to execute
                cursor.execute(sql_query, (category_title, value))
                # --------------------------
                
                row = cursor.fetchone()
                if row:
                    found_questions.append(Question(*row))
                else:
                    logger.warning(f"Category '{category_title}' missing question for value ${value}.")
            except sqlite3.Error as e:
                logger.error(f"Database error fetching question for {category_title} at ${value}: {e}")
                continue # Continue to next value even if one fails

        conn.close()
        found_questions.sort(key=lambda q: q.value)
        self.questions = found_questions
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
        self.answered = False

class Player:
    name = "Steve"
    score = 0


    