from wordle_bot import WordleBot

bot = WordleBot()
bot.setup()

for _ in range(6):
    bot.guess_word()
    bot.check_for_valid_letters()
    bot.update_word_list()
    if len(bot.correct_pos) == 5:
        break

bot.quit()
