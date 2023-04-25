import redis


class RedisClient:
    def __init__(self, stream_key, group_name, consumer_name,
                 host='localhost', port=6379):
        self.host = host
        self.port = port
        self.stream_key = stream_key
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.redis_client = redis.Redis(host=self.host,
                                        port=self.port)

    def is_connected(self):
        return self.redis_client.ping()

    def publish_message(self, message):
        self.redis_client.xadd(self.stream_key, message)

    def consume_messages(self, last_id='>', count=1):
        messages = self.redis_client.xreadgroup(
            groupname=self.group_name,
            consumername=self.consumer_name,
            streams={self.stream_key: last_id},
            count=count,
            block=0
        )
        return messages

    def ack(self, message_id):
        self.redis_client.xack(self.stream_key, self.group_name, message_id)

    def nack(self, message_id):
        self.redis_client.xack(self.stream_key,
                               self.group_name,
                               message_id,
                               False)

    def close(self):
        self.redis_client.close()
