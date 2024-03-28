import redis

# 创建Redis连接
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 保存图片到Redis
def save_photo(user_id, file_id):
    try:
        redis_client.rpush(user_id, file_id)
        print("Photo ID saved successfully.")
    except Exception as e:
        print(f"Error saving photo ID to redis: {e}")

# 保存视频到Redis
def save_video(user_id, file_id):
    try:
        redis_client.rpush(f"video@{user_id}", file_id)
        print("Video ID saved successfully.")
    except Exception as e:
        print(f"Error saving video ID to redis: {e}")


# 获取保存的图片的file_id
def get_saved_photo(id):
    try:
        # 尝试从Redis获取保存的file_id
        file_id = redis_client.hget(id, 'photo_id')
        if file_id:
            return file_id.decode('utf-8')  # decode bytes to str
        else:
            print("No photo ID found in Redis.")
            return None
    except Exception as e:
        print(f"Error retrieving photo ID from redis: {e}")
        return None
    
def get_saved_video(id):
    try:
        # 尝试从Redis获取保存的file_id
        file_id = redis_client.hget(id, 'video_id')
        if file_id:
            return file_id.decode('utf-8')  # decode bytes to str
        else:
            print("No video ID found in Redis.")
            return None
    except Exception as e:
        print(f"Error retrieving video ID from redis: {e}")
        return None

def get_latest_photo(user_id):
    try:
        # 尝试从Redis读取当前用户最新的file_id
        file_id = redis_client.lrange(user_id, -1, -1)
        if file_id:
            return file_id.decode('utf-8')  # decode bytes to str
        else:
            print("No photo ID found in Redis.")
            return None
    except Exception as e:
        print(f"Error retrieving photo ID from redis: {e}")
        return None

def pop_latest_photo(user_id):
    try:
        # 尝试从Redis获取当前用户最新的file_id
        file_id = redis_client.rpop(user_id)
        if file_id:
            return file_id.decode('utf-8')  # decode bytes to str
        else:
            print("No photo ID found in Redis.")
            return None
    except Exception as e:
        print(f"Error popping photo ID from redis: {e}")
        return None
    
def pop_latest_video(user_id):
    try:
        # 尝试从Redis获取当前用户最新的file_id
        file_id = redis_client.rpop(f"video@{user_id}")
        if file_id:
            return file_id.decode('utf-8')  # decode bytes to str
        else:
            print("No video ID found in Redis.")
            return None
    except Exception as e:
        print(f"Error popping photo ID from redis: {e}")
        return None
    
def set_photo_attr(id, field, value):
    try:
        # 尝试从Redis设置图片的名字或描述
        success = redis_client.hset(id, field, value)
        if success:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error setting photo field from redis: {e}")
        return False
    
def set_video_attr(id, field, value):
    try:
        # 尝试从Redis设置图片的名字或描述
        success = redis_client.hset(id, field, value)
        if success:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error setting video field from redis: {e}")
        return False