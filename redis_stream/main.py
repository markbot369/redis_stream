import argparse
from redis_stream.redis_client import RedisClient


default_data = {
    'stream_key': 'mystream',
    'group_name': 'group1',
    'consumer_name': 'consumer1'
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stream', default=default_data['stream_key'], 
                        help='Redis stream key to read from')
    parser.add_argument('--group', default=default_data['group_name'], 
                        help='Consumer group name')
    parser.add_argument('--consumer', default=default_data['consumer_name'], 
                        help='Consumer name')
    parser.add_argument('--server', default='localhost', 
                        help='Redis server host')
    parser.add_argument('--port', default=6379, type=int, 
                        help='Redis server port')
    return parser.parse_args()


def main():
    args = parse_args()
    redis_client = RedisClient(args.stream, args.group, args.consumer,
                               host=args.server, port=args.port)
    try:
        if redis_client.is_connected():
            print('Connected to Redis Server')
            while True:
                for message in redis_client.consume_messages(last_id='>'):
                    # process the message
                    print(f'Recived message: {message}')
        else:
            print('Error: Redis client is not connected')
    except KeyboardInterrupt:
        print('\nKeyboard Interrupt: Exiting...')
        redis_client.close()
        exit()


if __name__ == '__main__':
    main()
