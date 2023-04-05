import requests
from bs4 import BeautifulSoup
import sqlite3
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext


# Define the URLs of the websites you want to scrape
urls = ['https://www.bleepingcomputer.com/', 'https://www.zscaler.com/blogs']

# Create a connection to a local SQLite database
conn = sqlite3.connect('articles.db')
c = conn.cursor()

# Create a table in the database to store the articles
c.execute('''CREATE TABLE IF NOT EXISTS articles
             (title text, url text)''')
conn.commit()

# Initialize the Telegram bot
bot_token = 'BOTTOKENHERE'
bot = telegram.Bot(token=bot_token)

# Define the function to scrape the websites and check for new articles
def scrape_websites():
    for url in urls:
        # Send a GET request to the website
        response = requests.get(url)
        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all the article titles and URLs
        articles = soup.find_all('article')
        for article in articles:
            title = article.find('h2').text
            url = article.find('a')['href']
            # Check if the article is already in the database
            c.execute("SELECT * FROM articles WHERE title=? AND url=?", (title, url))
            if c.fetchone() is None:
                # If the article is new, insert it into the database
                c.execute("INSERT INTO articles VALUES (?, ?)", (title, url))
                conn.commit()
                # Send a message to the Telegram bot chat with the new article
                message = f'New article published:\n\n{title}\n{url}'
                bot.send_message(chat_id='your_chat_id_here', text=message)
            
# Define the function to display the list of articles and ask the user to choose one to post to a channel
def choose_article(update: Update, context: CallbackContext) -> None:
    # Get the list of articles from the database
    c.execute("SELECT * FROM articles")
    articles = c.fetchall()
    # Create a list of InlineKeyboardButtons for each article
    buttons = []
    for article in articles:
        title = article[0]
        url = article[1]
        buttons.append([InlineKeyboardButton(text=title, callback_data=url)])
    # Create an InlineKeyboardMarkup with the list of buttons
    keyboard = InlineKeyboardMarkup(buttons)
    # Send a message to the user with the list of articles and the keyboard
    update.message.reply_text('Please choose an article to post to the channel:', reply_markup=keyboard)

# Define the function to handle the callback when the user selects an article to post to a channel
def post_article(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    url = query.data
    # Send a message to the user to confirm the post
    message = f'Do you want to post this article to the channel?\n\n{url}'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text='Yes', callback_data=url), InlineKeyboardButton(text='No', callback_data='cancel')]])
    query.message.reply_text(message, reply_markup=keyboard)

# Define the function to handle the callback when the user confirms the post

def confirm_post(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    if data == 'cancel':
        # If the user cancels the post, send a message to the chat
        query.message.reply_text('Post canceled.')
    else:
        # If the user confirms the post, post the article to the channel
        chat_id = 'your_channel_id_here'
        bot.send_message(chat_id=chat_id, text=data)
        # Send a message to the chat to confirm the post
        query.message.reply_text('Article posted to the channel.')
    # Delete the inline keyboard from the chat
    query.message.delete_reply_markup()

# Define the function to start the bot and schedule the scraping task to run every hour
def start_bot():
    updater = Updater(bot_token)
    updater.dispatcher.add_handler(CommandHandler('start', choose_article))
    updater.dispatcher.add_handler(CallbackQueryHandler(post_article))
    updater.dispatcher.add_handler(CallbackQueryHandler(confirm_post))
    updater.start_polling()
    # Schedule the scraping task to run every hour
    updater.job_queue.run_repeating(scrape_websites, interval=3600)
    updater.idle()

# Start the bot
if __name__ == '__main__':
    start_bot()
