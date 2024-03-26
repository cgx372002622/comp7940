from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import configparser
import logging
import redis
from ChatGPT_HKBU import HKBU_ChatGPT
import requests
import random

#添加的功能
from image_handler import save_photo, get_saved_photo
from movie_scraper import scrape_movies

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    # updater = Updater(token=(os.environ['ACCESS_TOKEN']),  use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
        password=(config['REDIS']['PASSWORD']),
        port=(config['REDIS']['REDISPORT']))
        
# You can set this logging module, so you will know when
# and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    
# register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    
    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
      
    
# on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("Hello", hello))      #register a new command_handler
    dispatcher.add_handler(CommandHandler("good", good))
    
# 处理图片
    dispatcher.add_handler(CommandHandler("sendphoto", send_saved_photo))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
    
    dispatcher.add_handler(CommandHandler("movie", handle_movie_request))
    
# To start the bot:
    updater.start_polling()
    updater.idle()
    
    
# 定义功能
def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
    # Define a few command handlers. These usually take the two arguments update and
    # context. Error handlers also receive the raised TelegramError object in error.


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
        
def hello(update:Update, context: CallbackContext) -> None:
    name = context.args[0]
    reply_message = f"Good day,{name}!"
    update.message.reply_text(reply_message)
    
    
def good(update: Update, context: CallbackContext) -> None:
    try:
        name = context.args[0]
        reply_message = f"干哈子, {name}!"
        update.message.reply_text(reply_message)
    except IndexError:
        update.message.reply_text('Usage: /good <name>')
        
        
def good(update: Update, context: CallbackContext) -> None:
    try:
        name = context.args[0]
        reply_message = f"干哈子, {name}!"
        update.message.reply_text(reply_message)
    except IndexError:
        update.message.reply_text('Usage: /good <name>')
        
        
        
        
# 处理接收到的图片消息
def handle_photo(update, context):
    # 获取接收到的图片
    photo = update.message.photo[-1]  # 获取最高分辨率的图片
    print(photo)
    file_id = photo.file_id

    # 将图片的file_id保存到Redis中
    save_photo(file_id)

    update.message.reply_text('图片已保存')

# 处理用户请求发送之前保存的图片
def send_saved_photo(update, context):
    # 从Redis中获取保存的图片的file_id
    file_id = get_saved_photo()

    if file_id:
        # 发送图片给用户
        update.message.reply_photo(photo=file_id)
    else:
        update.message.reply_text('没有保存的图片')
    

# 处理用户请求电影的命令
def handle_movie_request(update, context):
    # 获取用户发送的电影查询
    query = ' '.join(context.args)
    print(context)
    print(update.text)
    
    # 爬取电影数据
    movies = scrape_movies(query)
    
    # 将电影数据发送给用户
    if movies:
        for movie in movies:
            message = f"电影名称：{movie['title']}\n评分：{movie['rating']}\n描述：{movie['description']}"
            update.message.reply_text(message)
    else:
        update.message.reply_text("未找到相关电影")
    
        
if __name__ == '__main__':
    main()
