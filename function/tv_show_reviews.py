import redis
import os

global redis1
redis1 = redis.Redis(host=(os.environ['REDIS_HOST']),
    password=(os.environ['REDIS_PASSWORD']),
    port=(os.environ['REDIS_REDISPORT']))

def write_review(tv_show, review):
    # 将评论存储到Redis中
    redis1.set(tv_show, review)

def read_review(tv_show):
    # 从Redis中获取评论内容
    review = redis1.get(tv_show)
    return review.decode('UTF-8') if review else None