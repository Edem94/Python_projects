from random import choice
import telebot

# new token should be generated and added by user when the bot is created
TOKEN = ""
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
  # Keybord generation for handling with user
  keyboard = telebot.types.ReplyKeyboardMarkup()

  # Add buttons
  easy = telebot.types.KeyboardButton("Easy")
  middle = telebot.types.KeyboardButton("Middle")
  hard = telebot.types.KeyboardButton("Hard")

  # Add buttons to keyboard
  keyboard.row(easy)
  keyboard.row(middle)
  keyboard.row(hard)

  # Send the question + keyboard
  bot.send_message(message.chat.id,
                   "Choose the level: Easy, Middle, Hard",
                   reply_markup=keyboard)
  bot.register_next_step_handler(message, level_answer)


# Choose the level of game
def level_answer(message):
  # Keybord generation for handling with user
  keyboard = telebot.types.ReplyKeyboardMarkup()
  if message.text == 'Easy':
    # Add buttons
    red_button = telebot.types.KeyboardButton("🟥")
    black_button = telebot.types.KeyboardButton("⬛️")
    # Add buttons to keyboard
    keyboard.row(red_button)
    keyboard.row(black_button)
    bot.send_message(message.chat.id,
     "You chose the easy level. Your task is only to guess the color of my card.")
    bot.send_message(message.chat.id,
                     "Guess the color: 🟥 or ⬛️",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, evaluate_answer_color)
  elif message.text == 'Middle':
    # Add buttons
    hearts_suit = telebot.types.KeyboardButton("Hearts")
    diamond_suit = telebot.types.KeyboardButton("Diamonds")
    spades_suit = telebot.types.KeyboardButton("Spades")
    clubs_suit = telebot.types.KeyboardButton("Clubs")
    # Add buttons to keyboard
    keyboard.row(hearts_suit)
    keyboard.row(diamond_suit)
    keyboard.row(spades_suit)
    keyboard.row(clubs_suit)
    bot.send_message(message.chat.id,
       "You chose the middle level. Your task is to guess the suit of my card.")
    bot.send_message(message.chat.id,
                     "Guess the card suit: Hearts, Diamonds, Spades or Clubs", reply_markup=keyboard)
    bot.register_next_step_handler(message, evaluate_answer_suit)
  elif message.text == 'Hard':
    bot.send_message(message.chat.id,
       "You chose the hard level. Your task is to guess the number of my card. It's not so easy. There are 13 options:)")
    bot.send_message(message.chat.id,
                     "Guess the card number: 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K or A. Type in the chat",
                     reply_markup=keyboard)

    bot.register_next_step_handler(message, evaluate_answer_number)
  elif message.text.lower() in ['exit', '/exit']:
    bot.send_message(message.chat.id, "Thanks for the game! Have a nice day! Bye!")
  else:
    bot.send_message(message.chat.id,
     "Such level does not exist.",
     reply_markup=keyboard)
    start(message)


# Answer comparison color
def evaluate_answer_color(message):
  # Generate random card number and suit
  random_card_number, random_card_suit = random_card()
  # Answer comparison
  if message.text not in ["🟥", "⬛️"]:
    bot.send_message(
        message.chat.id,
        "Such color doesn't exist.")
  elif message.text == "🟥" and random_card_suit in ["Hearts", "Diamonds"]:
    # Result of comparison
    bot.send_message(
        message.chat.id,
        f"Correct! The card was: {random_card_number} {random_card_suit}. Congratulations!")
  elif message.text == "⬛️" and random_card_suit in ["Spades", "Clubs"]:
    bot.send_message(
        message.chat.id,
        f"Correct! The card was: {random_card_number} {random_card_suit}. Congratulations!")
  else:
    bot.send_message(
        message.chat.id,
        f"Incorrect! The card was: {random_card_number} {random_card_suit}. Good luck next time!")

  start(message)


# Answer comparison suit
def evaluate_answer_suit(message):
  # Generate random card number and suit
  random_card_number, random_card_suit = random_card()
  # Answer comparison
  if message.text not in ["Hearts", "Diamonds", "Clubs", "Spades"]:
    bot.send_message(
        message.chat.id,
        "Such card suit doesn't exist.")
  elif message.text == random_card_suit:
    # Result of comparison
    bot.send_message(
        message.chat.id,
        f"Correct! The card was: {random_card_number} {random_card_suit}. Congratulations!")
  else:
    bot.send_message(
        message.chat.id,
        f"Incorrect! The card was: {random_card_number} {random_card_suit}. Good luck next time!")

  start(message)


# Answer comparison number
def evaluate_answer_number(message):
  # Generate random card number and suit
  random_card_number, random_card_suit = random_card()
  if message.text not in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]:
    bot.send_message(
        message.chat.id,
        "Such card doesn't exist.")
  # Answer comparison
  elif message.text == random_card_number:
    # Result of comparison
    bot.send_message(
        message.chat.id,
        f"Correct! The card was: {random_card_number} {random_card_suit}. Congratulations!")
  else:
    bot.send_message(
        message.chat.id,
        f"Incorrect! The card was: {random_card_number} {random_card_suit}. Good luck next time!")

  start(message)


# random card generation
def random_card():
  value = choice(
      ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"])
  suit = choice(["Hearts", "Diamonds", "Clubs", "Spades"])
  return [value, suit]


bot.infinity_polling()
