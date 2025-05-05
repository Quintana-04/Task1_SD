import redis
import time

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def get_messages():
    """Retorna la llista de missatges a publicar."""
    return [
        "Breaking News: El genis es imbecil",
        "Weather Update: El raul es un fraude",
        "Sports: El Marc la tiene muerta"
    ]

def publish_messages(client, channel_name, messages, delay=5):
    """Publica una llista de missatges al canal especificat, amb un retard entre ells."""
    for message in messages:
        client.publish(channel_name, message)
        print(f"Published: {message}")
        time.sleep(delay)

# Codi principal
client = connect_to_redis()
channel_name = "INSULT"
messages = get_messages()
publish_messages(client, channel_name, messages)
