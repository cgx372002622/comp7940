import redis
import os

global redis1
redis1 = redis.Redis(host=(os.environ['REDIS_HOST']),
    password=(os.environ['REDIS_PASSWORD']),
    port=(os.environ['REDIS_REDISPORT']))

def save_hiking_route_description(update, context):
    if context.args:
        route_name = context.args[0]
        # 保存路线名称到Redis
        redis_key = f"route:{update.effective_user.id}"
        redis1.set(redis_key, route_name)
        
        reply_message = f"保存了名为 {route_name} 的徒步路线描述到Redis"
    else:
        reply_message = "请提供徒步路线名称作为参数"
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def share_hiking_route(update, context):
    redis_key = f"route:{update.effective_user.id}"
    route_name = redis1.get(redis_key)
    
    if route_name:
        reply_message = f"分享名为 {route_name} 的徒步路线描述"
    else:
        reply_message = "未找到已保存的徒步路线描述"
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
