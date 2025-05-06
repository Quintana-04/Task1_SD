import redis

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def subscribe_to_channel(client, channel_name):
    """Subscriu-se a un canal de Redis i retorna el pubsub."""
    pubsub = client.pubsub()
    pubsub.subscribe(channel_name)
    return pubsub

def listen_for_messages(pubsub):
    """Escolta contínuament els missatges d'un canal Redis."""
    print(f"Subscribed to {pubsub.channels}, waiting for messages...")
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received: {message['data']}")

#Codi principal
client = connect_to_redis()
channel_name = "INSULT"
pubsub = subscribe_to_channel(client, channel_name)
listen_for_messages(pubsub)