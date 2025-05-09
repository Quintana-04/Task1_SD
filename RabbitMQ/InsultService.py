import pika

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    return connection.channel()

def declare_queue(channel, queue_name='insults_to_censor'):
    channel.queue_declare(queue=queue_name)

def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")

def consume_messages(channel, queue_name='insults_to_censor'):
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()

# Establece la conexión
connection = create_connection()
channel = create_channel(connection)

# Declara la cola
declare_queue(channel)

# Consume los mensajes
consume_messages(channel)

