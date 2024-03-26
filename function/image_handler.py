import redis

# 创建Redis连接
redis_client = redis.Redis(host='localhost', port=12345, db=0)

# 保存图片到Redis
def save_photo(file_id):
    try:
        redis_client.set('last_photo_id', file_id)
        print("Photo ID saved successfully.")
    except Exception as e:
        print(f"Error saving photo ID to redis: {e}")


# 获取保存的图片的file_id
def get_saved_photo():
    try:
        # 尝试从Redis获取保存的file_id
        file_id = redis_client.get('last_photo_id')
        if file_id:
            return file_id.decode('utf-8')  # decode bytes to str
        else:
            print("No photo ID found in Redis.")
            return None
    except Exception as e:
        print(f"Error retrieving photo ID from redis: {e}")
        return None
