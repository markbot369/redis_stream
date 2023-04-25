import pytest
from redis_stream.redis_client import RedisClient


stream_name = 'mystream'
consumer_group = 'group1'
consumer_name = 'consumer1'


@pytest.fixture
def redis_client():
    return RedisClient(stream_name, group_name=consumer_group, 
                       consumer_name=consumer_name, 
                       host='localhost', port=6379)


def test_publish_message(redis_client):
    # Clear all the data in the  test stream
    # Use XTRIM to remove all messages from the stream
    redis_client.redis_client.xtrim(stream_name, maxlen=0)

    message = {'name': 'Bob', 'age': '25'}
    redis_client.publish_message(message)
    result = redis_client.redis_client.xread({redis_client.stream_key: 0},
                                             count=1)
    res_msg = {key.decode('utf-8'): value.decode('utf-8')
               for key, value in result[0][1][0][1].items()}
    assert res_msg == message


def test_consume_messages(redis_client):
    # consumer_group = 'group1'
    # consumer_name = 'consumer1'
    last_id = '>'
    count = 3

    redis_client.redis_client.xtrim(stream_name, maxlen=0)
    # publish some messages to the stream
    messages = [
        {'name': 'Charlie', 'age': '35'},
        {'name': 'David', 'age': '40'},
        {'name': 'Eve', 'age': '45'}
    ]
    for message in messages:
        redis_client.publish_message(message)

    # consume messages from the stream
    result = redis_client.consume_messages(
        # consumer_group,
        # consumer_name,
        last_id=last_id,
        count=count)

    res_message = {key.decode('utf-8'): value.decode('utf-8')
                   for key, value in result[0][1][0][1].items()}
    assert len(result) == 1
    assert len(result[0][1]) == count
    assert res_message == messages[0]
