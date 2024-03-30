from telegram import Update, Bot, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import os
import configparser
import logging
import redis
from ChatGPT_HKBU import HKBU_ChatGPT

#添加的功能
from function.image_handler import save_photo, get_saved_photo, set_photo_attr, pop_latest_photo, save_video, pop_latest_video, set_video_attr, get_saved_video
from function.movie_scraper import scrape_movies
from function.tv_show_reviews import write_review, read_review
#路径分享功能
from function import hiking_route_sharing


PHOTO, NAME = range(2)

VIDEO, VIDEO_NAME = 2, 3

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
    # 设置Menu菜单
    commands = [BotCommand('/start', '开始上传图片'), BotCommand('/start_video', '开始上传视频')]
    bot = Bot(config['TELEGRAM']['ACCESS_TOKEN'])
    bot.set_my_commands(commands)
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
        password=(config['REDIS']['PASSWORD']),
        port=(config['REDIS']['REDISPORT']))
        
# You can set this logging module, so you will know when
# and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    
# 上传图片
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO: [MessageHandler(Filters.photo, handle_photo)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, handle_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    ))

# 上传视频
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start_video", start_video)],
        states={
            VIDEO: [MessageHandler(Filters.video, handle_video)],
            VIDEO_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_video_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    ))
    
# register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)
    
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
    dispatcher.add_handler(CommandHandler("photo", photo)) # get photo
    dispatcher.add_handler(CommandHandler("video", video)) # get video

    dispatcher.add_handler(CommandHandler("movie", handle_movie_request))
# 注册分享tv show命令处理函数
    dispatcher.add_handler(CommandHandler("save_review", save_review))
    dispatcher.add_handler(CommandHandler("get_review", get_review))
    
    #注册路径分享命令
    # dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('save_hiking_route_description', hiking_route_sharing.save_hiking_route_description))
    dispatcher.add_handler(CommandHandler('share_hiking_route', hiking_route_sharing.share_hiking_route))
    
# To start the bot:
    updater.start_polling()
    updater.idle()

def photo(update, context):
    if (context.args is None or len(context.args) == 0):
        update.message.reply_text(
            "Please enter photo name"
        )
        return
    user_id = update.message.from_user.id
    name = ' '.join(context.args)
    file_id = get_saved_photo(f"{user_id}@{name}")

    if file_id:
        # 发送图片给用户
        update.message.reply_photo(photo=file_id)
    else:
        update.message.reply_text('No photo named: ' + name)

def video(update, context):
    if (context.args is None or len(context.args) == 0):
        update.message.reply_text(
            "Please enter video name"
        )
        return
    user_id = update.message.from_user.id
    name = ' '.join(context.args)
    file_id = get_saved_video(f"video@{user_id}@{name}")

    if file_id:
        # 发送图片给用户
        update.message.reply_video(video=file_id)
    else:
        update.message.reply_text('No video named: ' + name)

def start(update, context):
    update.message.reply_text(
        "Hi! I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "After uploading, send /photo plus photo's name to get photo\n\n"
        "Please upload your photo"
    )
    return PHOTO

def start_video(update, context):
    update.message.reply_text(
        "Hi! I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "After uploading, send /video plus video's name to get video\n\n"
        "Please upload your video"
    )
    return VIDEO

def handle_photo(update, context):
    # 用户id
    user_id = update.message.from_user.id
    # 获取接收到的图片
    photo = update.message.photo[-1]  # 获取最高分辨率的图片
    file_id = photo.file_id

    # 将图片的file_id保存到Redis中
    save_photo(user_id, file_id)

    update.message.reply_text(
        "Upload photo successfully!"
        "Please enter this photo's name"
    )

    return NAME

def handle_video(update, context):
    # 用户id
    user_id = update.message.from_user.id
    # 获取接收到的图片
    video = update.message.video
    file_id = video.file_id

    # 将图片的file_id保存到Redis中
    save_video(user_id, file_id)

    update.message.reply_text(
        "Upload video successfully!"
        "Please enter this video's name"
    )

    return VIDEO_NAME

def handle_name(update, context):
    user_id = update.message.from_user.id
    photo_id = pop_latest_photo(user_id)
    name = update.message.text
    success1 = set_photo_attr(f"{user_id}@{name}", 'name', name)
    success2 = set_photo_attr(f"{user_id}@{name}", 'photo_id', photo_id)
    if success1 & success2:
        update.message.reply_text(
            "Set name successfully!"
            "Welcome next upload~"
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "Oops! Something bad happened, see u next time~"
        )
        return ConversationHandler.END

def handle_video_name(update, context):
    user_id = update.message.from_user.id
    video_id = pop_latest_video(user_id)
    name = update.message.text
    success1 = set_video_attr(f"video@{user_id}@{name}", 'name', name)
    success2 = set_video_attr(f"video@{user_id}@{name}", 'video_id', video_id)
    if success1 & success2:
        update.message.reply_text(
            "Set name successfully!"
            "Welcome next upload~"
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "Oops! Something bad happened, see u next time~"
        )
        return ConversationHandler.END
    
def cancel(update, context):
    update.message.reply_text(
        "Welcome next upload! Bye~"
    )    
    return ConversationHandler.END

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
        
    #tv show功能
def save_review(update, context):
    try:
        tv_show = context.args[0]
        review = ' '.join(context.args[1:])
        
        write_review(tv_show, review)
        
        update.message.reply_text('Review saved successfully.')
    except IndexError:
        update.message.reply_text('Usage: /save_review <tv_show> <review>')

def get_review(update, context):
    try:
        tv_show = context.args[0]
        
        review = read_review(tv_show)
        
        if review:
            update.message.reply_text(f"Review for {tv_show}: {review}")
        else:
            update.message.reply_text(f"No review found for {tv_show}.")
    except IndexError:
        update.message.reply_text('Usage: /get_review <tv_show>')
    
        
if __name__ == '__main__':
    main()
