import time
import logging
import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
ARTICLE_LIST = []

# Function to fetch the latest article titles and URLs
def fetch_latest_articles():
    # Define the URLs to check
    urls = ['https://example.com', 'https://example.org']

    # Iterate through the URLs and fetch the article titles and URLs
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')
        for article in articles:
            title = article.h2.text.strip()
            url = article.a['href']
            # Check if the article has already been added to the list
            if (title, url) not in ARTICLE_LIST:
                ARTICLE_LIST.append((title, url))

# Function to send the list of latest articles to the user
def send_article_list(update, context):
    # Fetch the latest articles
    fetch_latest_articles()

    # Create the message to send
    message = "Here are the latest articles:\n\n"
    for i, (title, url) in enumerate(ARTICLE_LIST):
        message += f"{i+1}. {title}\n{url}\n\n"

    # Send the message to the user
    update.message.reply_text(message)

    # Reset the article list
    ARTICLE_LIST.clear()

# Function to handle the user's choice of article to post to the channel
def post_article_choice(update, context):
    query = update.callback_query
    query.answer()
    choice = int(query.data)

    # Post the selected article to the channel
    title, url = ARTICLE_LIST[choice-1]
    context.bot.send_message(chat_id='your_channel_id_here', text=f"{title}\n{url}")

    # Reset the article list
    ARTICLE_LIST.clear()

# Function to start the bot
def start_bot():
    # Get the bot token from the environment variable
    bot_token = 'your_bot_token_here'

    # Create the updater and dispatcher
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    # Create the command handlers
    send_article_list_handler = CommandHandler('start', send_article_list)
    post_article_choice_handler = CallbackQueryHandler(post_article_choice)

    # Add the command handlers to the dispatcher
    dispatcher.add_handler(send_article_list_handler)
    dispatcher.add_handler(post_article_choice_handler)

    # Start the bot
    updater.start_polling()
    logger.info('Bot started')

    # Keep the bot running until Ctrl-C is pressed
    updater.idle()

if __name__ == '__main__':
    start_bot()
