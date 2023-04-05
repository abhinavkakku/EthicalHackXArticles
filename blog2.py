import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater

# Enter your bot token here
bot_token_here = 'YOUR_BOT_TOKEN'

# Enter your chat id here
your_chat_id_here = 'YOUR_CHAT_ID'

# Enter the channel id you want to post articles to
your_channel_id_here = 'YOUR_CHANNEL_ID'

# List of websites to check for new articles
websites = [
    {
        'name': 'Ethical Hack X',
        'url': 'https://www.ethicalhackx.com/'
    },
    {
        'name': 'Hackaday',
        'url': 'https://hackaday.com/'
    },
    {
        'name': 'Wired',
        'url': 'https://www.wired.com/'
    }
]

# List of article titles and URLs that have already been posted
posted_articles = []


def check_websites():
    """Check websites for new articles"""
    for website in websites:
        name = website['name']
        url = website['url']
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')
        for article in articles:
            title = article.h2.a.text.strip()
            url = article.h2.a['href']
            if not any(posted_article['title'] == title for posted_article in posted_articles):
                posted_articles.append({'title': title, 'url': url})
                post_to_channel(title, url)
                send_message(f"New article posted on {name}: {title}\n{url}")


def send_message(message):
    """Send message to your chat id"""
    requests.post(f"https://api.telegram.org/bot{bot_token_here}/sendMessage",
                  data={"chat_id": your_chat_id_here, "text": message})


def post_to_channel(title, url):
    """Post the article to the channel"""
    requests.post(f"https://api.telegram.org/bot{bot_token_here}/sendMessage",
                  data={"chat_id": your_channel_id_here, "text": f"{title}\n{url}"})


def start_bot():
    """Start the Telegram bot"""
    updater = Updater(bot_token_here)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    check_websites()
    start_bot()
