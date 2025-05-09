import pika
import time

def create_connection():
    """Establece una conexión con RabbitMQ."""
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    """Crea un canal de comunicación con RabbitMQ."""
    return connection.channel()

def get_messages():
    return [
        'Buenas tardes',
        'Tonto el que lo lea',
        'Espavila un poco chaval'
    ]


def declare_exchange(channel, exchange_name='logs', exchange_type='fanout'):
    """Declara un exchange de tipo fanout en RabbitMQ."""
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

def publish_message(channel, exchange_name, messages):
    """Publica un mensaje en un exchange."""
    for message in messages:
        channel.basic_publish(exchange=exchange_name, routing_key='', body=message)
        print(f" [x] Sent: '{message}'")
        time.sleep(5)

def close_connection(connection):
    """Cierra la conexión con RabbitMQ."""
    connection.close()

# Establece la conexión
connection = create_connection()

# Crea el canal
channel = create_channel(connection)

# Declara el exchange
declare_exchange(channel)

# Publica el mensaje
exchange_name = 'logs'
message = get_messages()
publish_message(channel, exchange_name, message)

# Cierra la conexión
close_connection(connection)

