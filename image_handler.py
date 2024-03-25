import redis

# 创建Redis连接
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 保存图片到Redis
def save_photo(file_id):
    redis_client.set('photo', file_id)

# 获取保存的图片的file_id
def get_saved_photo():
    return redis_client.get('photo')