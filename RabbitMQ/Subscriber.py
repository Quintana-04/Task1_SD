import pika

def create_connection():
    """Establece una conexión con RabbitMQ."""
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    """Crea un canal de comunicación con RabbitMQ."""
    return connection.channel()

def declare_exchange(channel, exchange_name='logs', exchange_type='fanout'):
    """Declara un exchange de tipo fanout en RabbitMQ."""
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

def create_temporary_queue(channel):
    """Crea una cola temporal (nombre aleatorio, auto-eliminada cuando el consumidor se desconecta)."""
    result = channel.queue_declare(queue='', exclusive=True)
    return result.method.queue

def bind_queue_to_exchange(channel, queue_name, exchange_name='logs'):
    """Vincula la cola al exchange especificado."""
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

def callback(ch, method, properties, body):
    """Función que maneja los mensajes recibidos."""
    print(f" [x] Received {body.decode()}")

def consume_messages(channel, queue_name):
    """Consume mensajes de la cola en RabbitMQ."""
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()

# Establece la conexión
connection = create_connection()

# Crea el canal
channel = create_channel(connection)

# Declara el exchange
declare_exchange(channel)

# Crea una cola temporal
queue_name = create_temporary_queue(channel)

# Vincula la cola al exchange
bind_queue_to_exchange(channel, queue_name)

# Consume los mensajes de la cola
consume_messages(channel, queue_name)

