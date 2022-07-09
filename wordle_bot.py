import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from random import randint


CHROME_DRIVER_PATH = Service("/Users/*****/Development/chromedriver")
WEBSITE = "https://www.nytimes.com/games/wordle/index.html"


class WordleBot:

    def __init__(self):
        self.driver = webdriver.Chrome(service=CHROME_DRIVER_PATH)
        self.actions = ActionChains(self.driver)
        self.bot_guess = None
        self.correct_pos = {}  # letters in correct position
        self.incorrect_pos = {}  # letters present, but in incorrect position
        self.absent_letters = []  # letters not in word
        self.tile_index_position = 0  # keeps track of which tile element to check/fill in each row

        # create valid word list:
        with open(file='word_list.txt') as word_file:
            self.valid_words = [word.strip().upper() for word in word_file]

    def setup(self):
        self.driver.get(WEBSITE)
        self.driver.find_element(By.CLASS_NAME, "Modal-module_closeIcon__b4z74").click()
        time.sleep(1)

    def guess_word(self):
        # bot guess:
        if self.tile_index_position == 0:
            self.bot_guess = "SLATE"
        else:
            random_index = randint(0, len(self.valid_words) - 1)
            self.bot_guess = self.valid_words[random_index]

        # enter word in current row of tiles:
        for index, letter in enumerate(self.bot_guess):
            self.actions.send_keys(letter)
            self.actions.perform()
            time.sleep(1)
            # keeps track of which index position to start checking elements in tile list [UP TO 30]:
            self.tile_index_position += 1

        self.actions.send_keys(Keys.RETURN)
        self.actions.perform()

    def check_for_valid_letters(self):
        # get current state of each tile element:
        time.sleep(2)
        tile_list = self.driver.find_elements(By.XPATH, "//div[@data-testid='tile']")
        letter_index = 0

        for i in range(self.tile_index_position - 5, self.tile_index_position):
            data_state = tile_list[i].get_attribute("data-state")

            if data_state == "present":
                self.incorrect_pos[letter_index] = self.bot_guess[letter_index]
            elif data_state == "correct":
                self.correct_pos[letter_index] = self.bot_guess[letter_index]
            else:
                if self.correct_pos and self.bot_guess[letter_index] not in self.correct_pos.values() or not self.correct_pos:
                    self.absent_letters.append(self.bot_guess[letter_index])

            letter_index += 1

        print(f"letters in correct pos: {self.correct_pos}\nletters in incorrect pos: {self.incorrect_pos}\nabsent letters: {self.absent_letters}")

    def update_word_list(self):
        self.valid_words.remove(self.bot_guess)
        updated_word_list = []
        # keep track of the highest correct and present letter streaks to optimize word list without duplicating words:
        highest_correct_streak = len(self.correct_pos)
        highest_present_streak = len(self.incorrect_pos)
        print(f"bot guessed: {self.bot_guess}")

        # loop through word and check if any letter indices match in each dictionary [CORRECT/INCORRECT/ABSENT]:
        for i, word in enumerate(self.valid_words):
            correct_streak = 0
            present_streak = 0
            absent_streak = 0

            # check if letter is absent:
            if self.absent_letters:
                for j, letter in enumerate(word):
                    if letter in self.absent_letters:
                        absent_streak += 1

            # check if letter in correct pos:
            if self.correct_pos:
                for key, value in self.correct_pos.items():
                    if word[key] == value:
                        correct_streak += 1

            # check if letter not in incorrect pos from previous guess(es):
            if self.incorrect_pos:
                for key, value in self.incorrect_pos.items():
                    if value in word and word[key] != value:
                        present_streak += 1

            if correct_streak == highest_correct_streak and present_streak == highest_present_streak and absent_streak == 0:
                updated_word_list.insert(0, word)

        print(f"word list: {updated_word_list}, updated word list length: {len(updated_word_list)}")
        self.incorrect_pos = {}
        self.valid_words = updated_word_list

    def quit(self):
        time.sleep(5)
        self.driver.quit()
