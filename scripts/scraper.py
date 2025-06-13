import os
import sys
import logging
from bs4 import BeautifulSoup, Tag
import requests
import sqlite3

#Traceback (most recent call last):
#  File "C:\Users\rhoad\Repositories\jeopardy-game\scripts\scraper.py", line 195, in <module>       
#    main()
#  File "C:\Users\rhoad\Repositories\jeopardy-game\scripts\scraper.py", line 43, in main
#    add_jquestion(conn, q)
#  File "C:\Users\rhoad\Repositories\jeopardy-game\scripts\scraper.py", line 192, in add_jquestion  
#    cursor.execute("INSERT INTO question (clue, answer, value, category, origin) VALUES (?,?,?,?,?)", (f"{question.clue}",f"{question.answer}",f"{question.value}",f"{question.category}",f"{question.origin}"))
#    ^^^^^^^^^^^^^^
#AttributeError: 'builtin_function_or_method' object has no attribute 'execute'


#path setup for modules
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir))
sys.path.append(project_root)

from src.game_utils import Question

# logger setup
logger = logging.getLogger(__name__)

def main():
    # path setup
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    db_path = os.path.join(parent_dir, "data", "questions.db")

    try:
        conn = sqlite3.connect(db_path) 
        logger.info(f"Successfully connected to database: {db_path}")
    except sqlite3.Error as e:
        logger.error(f"Couldn't connect to or operate on database at '{db_path}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    create_table(conn)

    # gather questions
    questions: list[Question] = []
    for i in range(9200):
        if i == 0: i = 1
        questions += search_page(f"https://j-archive.com/showgame.php?game_id={i}")

    # add questions to db
    for q in questions:
        add_jquestion(conn, q)
    
    if conn:
        conn.close()

    print("STATUS: COMPLETE")
    print("--------------------")
    print(f"QUESTIONS LOADED: {len(questions)}")
    print(f"PERCENTAGE OF GAMES USED: {(len(questions) / (9200 * 61.0)) * 100}%")

def search_page(url) -> list[Question]:
    categories = search_page_for_categories(url)
    content = search_page_for_questions(url)

    if len(categories) != 13 or len(content) != 61: 
        logger.error(f"Couldn't scrape sufficient data from {url},\ncontent len = {len(content)}")
        return []

    questions: list[Question] = []
    
    for i in range(12):
        # loops through all 12 first and second round categories
        category = categories[i]
        for j in range(5):
            # loops through each question per category
            # $ value can be determined from j
            value = (j * 100) + 100

            # determine content index with formula
            if i < 6:
                clue = content[i + (j*6)][0]
                answer = content[i + (j*6)][1]
            else:
                clue = content[i + 24 + (j*6)][0]
                answer = content[i + 24 + (j*6)][1]

            # add Questino obj to list to later be added to db
            questions.append(Question(clue,answer,value,category,"J! Archive"))
    # Final Jeopardy
    # hardcoded values work fine as list lengths already determined
    questions.append(Question(content[60][0],content[60][1],-1,categories[12],"J! Archive"))
    return questions

def search_page_for_questions(url):
    """Searches jeopardy url for question/answer pairs.

    Args:
        url (str): 
            url of J! Archive webparge, example: "https://j-archive.com/showgame.php?game_id=9200"
            max id somewhere in 9200-10000

    Returns:
        list[(question,answer)]: list containing question,answer tuples from webpage
    """
    try:
        response = requests.get(url)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    answer_question_pairs = []
    
    answers_and_clues = soup.find_all("td", class_="clue_text")
    for ele in answers_and_clues:
        # skip non-Tag elements
        if not isinstance(ele, Tag):
            continue

        id = ele["id"]
        if isinstance(id, str) and id.endswith('_r'):
            continue

        question = ele.get_text(strip=True)

        # finds specific answer str text, can have appended text without
        answer_td = ele.find_next_sibling()
        if answer_td and isinstance(answer_td, Tag):
            answer_em = answer_td.find('em', class_='correct_response')
        if answer_em:
            answer = answer_em.get_text(strip=True)

        if answer and question:
            answer_question_pairs.append((question,answer))
            
    return answer_question_pairs
    
def search_page_for_categories(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    categories: list[str] = []

    categories_td = soup.find_all("td", class_="category_name")

    
    for ele in categories_td:
        # skip non-Tag elements
        if not isinstance(ele, Tag):
            continue


        category = ele.get_text(strip=True)
        categories.append(category)
    return categories    

def create_table(conn):
    """Creates necessary table if it don't exist."""
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clue TEXT NOT NULL,
                answer TEXT NOT NULL,
                value INTEGER,
                category TEXT,
                origin TEXT
            )
        ''')
        conn.commit()
        logger.info("Table 'questions' checked/created.")
    except sqlite3 as e:
        logger.error(f"Table couldn't be created: {e}")
    except Exception as e:
        logger.error(f"Table couldn't be created: {e}")    

def add_jquestion(conn, question: Question):
    """Adds jeopardy question to question db

    Args:
        conn (sqlite connection)
        clue (str)
        answer (str)
        value (int)
        category (str)
        origin (str)
    """
    cursor = conn.cursor()

    with conn:
        cursor.execute("INSERT INTO questions (clue, answer, value, category, origin) VALUES (?,?,?,?,?)", (f"{question.clue}",f"{question.answer}",f"{question.value}",f"{question.category}",f"{question.origin}"))
    
if __name__ == "__main__":
    main()