# Making a Redis Stream Client Example in Python

## Introduction

Microservice architecture has become a popular approach to developing software applications that are scalable, maintainable, and flexible. One of the challenges of microservice architecture is managing the flow of data between services, which can become complex as the number of services and interactions between them grows.

One solution to this challenge is to use message queues to decouple services, allowing them to communicate asynchronously and reducing the risk of service failures and downtime. Redis streams are a type of message queue that are particularly well-suited for microservice architecture.

Redis streams allow multiple producers to write messages to a stream, which can then be read by multiple consumers. This allows services to communicate in a scalable and efficient way, with messages being delivered in the order they are received. Redis streams also support message acknowledgment and automatic message retention, making it easy to implement reliable message processing in microservices.

In this article, we'll explore how to use Python and the redis module to connect to a Redis stream and write to a defined queue. We'll demonstrate how to encapsulate this functionality in a Python class, and how to make it into a CLI application with command-line arguments. By the end of this article, you'll have a better understanding of how to use Redis streams in your own microservice architecture projects.

## Redis Streams

Redis streams are a data structure that allows for the storage and processing of multiple time-series events. It's a log-like structure that can be used to represent events as they occur in real-time, such as user activity on a website, sensor data from IoT devices, or messages in a chat system.

Each event in a Redis stream is represented by a unique ID, which is generated automatically by Redis. The ID is a sequential number that starts at 0 and increments by 1 for each new event added to the stream.

Redis streams are append-only, meaning that once an event is added to a stream, it cannot be modified or deleted. This makes Redis streams ideal for capturing and storing data that needs to be tracked over time.

One of the key features of Redis streams is the ability to consume events in real-time. Consumers can read events from a stream by specifying a start point, such as the ID of the last event that was processed. As new events are added to the stream, they can be consumed by the consumer in real-time, allowing for real-time data processing and analysis.

Redis streams also support consumer groups, which allow multiple consumers to read from the same stream. Each consumer group maintains its own position in the stream, allowing for load balancing and fault tolerance.

## Redis Stream Client Example

For the creation of the example project we are going to use poetry, but you can follow the example code with any tool capable of creating a Python virtual environment.

Also you can follow the code explanation cloning the code in the [Github repository](https://github.com/markbot369/redis_stream)

The following code defines a class called `RedisStreamReader`, which is responsible for consuming messages from a Redis stream using a consumer group:

```python
import redis


class RedisStreamReader:
    def __init__(self, stream_key, group_name, consumer_name,
                 server='localhost', port=6379):
        self.redis_client = redis.Redis.from_url(f"redis://{server}:{port}")
        self.stream_key = stream_key
        self.group_name = group_name
        self.consumer_name = consumer_name
        # self.redis_client.xgroup_create(self.stream_key, self.group_name, mkstream=True)
        self.consumer = self.redis_client.xreadgroup(
            self.group_name,
            self.consumer_name,
            {self.stream_key: ">"})

    def publish_message(self, message):
        self.redis_client.xadd(self.stream_key, message)

    def consume_messages(self, consumer_group, consumer_name,
                         last_id='>', count=1):
        messages = self.redis_client.xreadgroup(
            groupname=consumer_group,
            consumername=consumer_name,
            streams={self.stream_key: last_id},
            count=count,
            block=0
        )
        return messages

```

First, the code imports the Redis Python library using `import redis`.

Next, a class called `RedisStreamReader` is defined. The purpose of this class is to provide a way to read and write to a Redis stream using a specified consumer group and consumer name.

The `__init__` method is used to create a connection to the Redis server, specify the stream key, group name, and consumer name, and initialize the consumer. The method takes the following parameters:

stream_key: The name of the Redis stream to read from.
group_name: The name of the consumer group to read from.
consumer_name: The name of the consumer within the consumer group.
server: The Redis server hostname or IP address. Default is 'localhost'.
port: The Redis server port number. Default is 6379.

Within the `__init__` method, the Redis client is initialized using the `redis.Redis.from_url` method, which takes a Redis server URL as its parameter. The stream key, group name, and consumer name are also set as instance variables.

Finally, the `xreadgroup` method is called on the Redis client object to initialize the consumer. This method takes the following parameters:

group_name: The name of the consumer group to read from.
consumer_name: The name of the consumer within the consumer group.
{self.stream_key: ">"}: A dictionary specifying the stream key to read from and the position to start reading from (in this case, ">" means to start reading from the latest message).

The `publish_message` method is used to add a new message to the Redis stream. It takes a message parameter, which is a dictionary containing the message data. The method calls the xadd method on the Redis client object to add the message to the stream.

The `consume_messages` method is used to read messages from the Redis stream. It takes the following parameters:

consumer_group: The name of the consumer group to read from.
consumer_name: The name of the consumer within the consumer group.
last_id: The ID of the last message that was read. Default is '>', meaning to start reading from the latest message.
count: The maximum number of messages to read. Default is 1.
block: The maximum amount of time to wait for new messages to arrive, in milliseconds. Default is 0, meaning to wait indefinitely.

The method calls the `xreadgroup` method on the Redis client object to read messages from the stream. The `xreadgroup` method takes the following parameters:

groupname: The name of the consumer group to read from.
consumername: The name of the consumer within the consumer group.
streams: A dictionary specifying the stream key to read from and the ID of the last message that was read.
count: The maximum number of messages to read.
block: The maximum amount of time to wait for new messages to arrive, in milliseconds.

The method returns a list of tuples, where each tuple contains the stream key and a list of messages. Each message is represented as a tuple containing the message ID and a dictionary of message data.

To call the above code in a CLI application, you can create an instance of the `RedisStreamReader` class with the appropriate parameters(we provide some example), and then use its methods to read and acknowledge messages from the stream. For example:

```python
import argparse
from redis_stream.simple_redisclient import RedisStreamReader


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('stream_key', help='Redis stream key to read from')
    parser.add_argument('group_name', help='Consumer group name')
    parser.add_argument('consumer_name', help='Consumer name')
    parser.add_argument('--server', default='localhost', help='Redis server host')
    parser.add_argument('--port', default=6379, type=int, help='Redis server port')
    return parser.parse_args()


def main():
    args = parse_args()
    reader = RedisStreamReader(args.stream_key, args.group_name, args.consumer_name,
                                server=args.server, port=args.port)
    if reader.is_connected():
        for message in reader.read():
            # process the message
            reader.ack(message['id'])
    else:
        print('Error: Redis client is not connected')


if __name__ == '__main__':
    main()
```

In this example, we define a `main()` function that parses the command line arguments using the argparse module, creates an instance of `RedisStreamReader`, and then loops through the messages returned by the `read()` method, processing each message and acknowledging it using the `ack()` method. If the Redis client is not connected, an error message is printed.

To run the CLI application, you can execute the Python script with the appropriate command line arguments. For example:

TODO: Change the code below to a real project script name
```bash
python myapp.py mystream mygroup myconsumer --server redis.mycompany.com --port 6379
```

## Create a Redis client and run a Redis server for testing our code

Now we are going to create a more real Redis stream consumer and test it with a Redis server running into a Docker container.

For this task we are create a Redis client with some more functionality to connect to a Redis server and  then use the "Pytest" library to test the new Redis stream consumer.

The code for the new class is this:

```python
import redis


class RedisClient:
    def __init__(self, host, port, password, stream_key):
        self.host = host
        self.port = port
        self.password = password
        self.stream_key = stream_key
        self.redis_client = redis.Redis(host=self.host,
                                        port=self.port,
                                        password=self.password)

    def is_connected(self):
        return self.redis_client.ping()

    def publish_message(self, message):
        self.redis_client.xadd(self.stream_key, message)

    def consume_messages(self, consumer_group, consumer_name,
                         last_id='>', count=1):
        messages = self.redis_client.xreadgroup(
            groupname=consumer_group,
            consumername=consumer_name,
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

```

This new Python code defines a class called `RedisClient`. This class uses Redis streams as a message broker, to delivery(produce) some messasges to a stream and consume(reads) the messages that arrives to the same stream.

The `__init__` method initializes the Redis client with the given host, port, password, and stream_key.
The `is_connected` method is used to check if the client is connected to the Redis server. It does this by sending a ping request to the server and returning the response.
The `publish_message` method is used to publish a message to a Redis stream identified by the `stream_key` attribute of the class. The message is added to the stream using the `xadd` command.
The `consume_messages` method is used to consume messages from a Redis stream. This method takes the `consumer_group`, `consumer_name`, `last_id`, and `count` parameters, which are used to identify the group and consumer that will consume the messages. The `xreadgroup` command is used to read messages from the stream based on these parameters. The messages are returned by the method.
The `ack` method is used to acknowledge a message that has been consumed by a consumer in a consumer group. The `xack` command is used to acknowledge the message, and the method takes the `message_id` parameter, which is used to identify the message.
The `nack` method is used to negative acknowledge a message that has been consumed by a consumer in a consumer group. The `xack` command is used with the force=False parameter to negative acknowledge the message, and the method takes the `message_id` parameter, which is used to identify the message.

## Create some tests to see how this Redis service works

We are now to test the functionality of this new defined class and for this task a running Redis server is needed. The Redis server can be installed localy in your PC but in this aricle we are going to use a Docker container running a Redis instance.

### Running a Redis instance with a Docker image

We download the Docker official image in this way:

```bash
docker pull redis
```

After that, a Redis image is ready to use in our PC. For running the Redis server run a new  container:

```bash
docker run --name redis-server -p 6379:6379 -d redis
```

This command creates a container named my-redis using the Redis image, forwards the Redis port 6379 from the container to the host's 6379 port, and runs the container in detached mode (-d option).

You can now connect to the Redis server running in the Docker container from your PC by using the Redis client and connecting to localhost:6379. We recomend the use of RedisInsight a Redis graphical user client, but you can use the same Docker image for conecting to the running container server with the following command:

```bash
docker run -it --network some-network --rm redis redis-cli -h redis-server
```

## Testing the client code

These tests cover the basic functionality of the Redis client, ensuring that messages can be published to the stream and consumed by a consumer group.
The following provided code is a set of unit tests written using the pytest testing framework. The tests are designed to test the functionality of the `RedisClient` class, which is defined in the `simple_redisclient.py` module.

```python
import pytest
from redis_stream.simple_redisclient import RedisClient


stream_name = 'mystream'

@pytest.fixture
def redis_client():
    return RedisClient('localhost', 6379, None, stream_name)


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
    consumer_group = 'group1'
    consumer_name = 'consumer1'
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
        consumer_group,
        consumer_name,
        last_id=last_id,
        count=count)

    res_message = {key.decode('utf-8'): value.decode('utf-8')
                   for key, value in result[0][1][0][1].items()}
    assert len(result) == 1
    assert len(result[0][1]) == count
    assert res_message == messages[0]

```

The first test, test_publish_message(), tests the publish_message() method of the RedisClient class. This method is used to publish a message to a Redis stream. In the test, the stream is first cleared using the xtrim() method, and then a message is published using the publish_message() method. The test then reads the message from the stream using the xread() method and checks that the message is the same as the one that was published.

The second test, test_consume_messages(), tests the consume_messages() method of the RedisClient class. This method is used to consume messages from a Redis stream using a consumer group. In the test, the stream is first cleared using the xtrim() method, and then three messages are published to the stream using the publish_message() method. The test then consumes the messages from the stream using the consume_messages() method and checks that the messages are the same as the ones that were published.

Both tests use the assert statement to check that the expected results are returned. If the expected results are not returned, the tests will fail and an error message will be displayed. This allows the developer to identify and fix any issues with the code.

The test then is invocated with the calling the PyTest command bellow:

```bash
pytest -v tests/test_redis_stream_client.py
```
