import os
import sys


#path setup for modules
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir))
sys.path.append(project_root)

import logging
from bs4 import BeautifulSoup, Tag
import requests
import sqlite3
from src.game_utils import Question

# logger setup
logger = logging.getLogger(__name__)

def main():
    # path setup
    #script_dir = os.path.dirname(os.path.abspath(__file__))
    #parent_dir = os.path.dirname(script_dir)
    #db_path = os.path.join(parent_dir, "data", "questions.db")
#
    #try:
    #    conn = sqlite3.connect(db_path) 
    #    logger.info(f"Successfully connected to database: {db_path}")
    #except sqlite3.Error as e:
    #    logger.error(f"Couldn't connect to or operate on database at '{db_path}': {e}")
    #except Exception as e:
    #    logger.error(f"An unexpected error occurred: {e}")
#
    #create_table(conn)

    search_page_for_categories("https://j-archive.com/showgame.php?game_id=9200")
    
    #if conn:
    #    conn.close()


# J! Archive example page: "https://j-archive.com/showgame.php?game_id=9200"
# max id 9200-10000
def search_page_for_questions(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    answers_and_clues = soup.find_all("td", class_="clue_text")
    
    for ele in answers_and_clues:
        # skip non-Tag elements
        if not isinstance(ele, Tag):
            continue

        id = ele["id"]
        if isinstance(id, str) and id.endswith('_r'):
            continue

        question = ele.get_text(strip=True)
        answer = ele.find_next_sibling()
        # work on naming and flow
        if answer and isinstance(answer, Tag):
            answer = answer.find('em', class_='correct_response')
        if answer:
            answer = answer.get_text(strip=True)

def search_page_for_categories(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    categories = soup.find_all("td", class_="category_name")
    
    for ele in categories:
        # skip non-Tag elements
        if not isinstance(ele, Tag):
            continue


        category = ele.get_text(strip=True)
        print(category)
        

    

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
    

def add_jquestion(conn,clue,answer,value,category,origin):
    """Adds jeopardy question to question db

    Args:
        conn (sqlite connection)
        clue (str)
        answer (str)
        value (int)
        category (str)
        origin (str)
    """
    cursor = conn.cursor

    with conn:
        cursor.execute("INSERT INTO question (clue, answer, value, category, origin) VALUES (?,?,?,?,?)", (f"{clue}",f"{answer}",f"{value}",f"{category}",f"{origin}"))
    
if __name__ == "__main__":
    main()