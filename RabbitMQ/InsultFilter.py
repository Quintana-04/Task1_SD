import pika
import threading

insults_list = []

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    return connection.channel()

def declare_queue(channel, queue_name='hello'):
    channel.queue_declare(queue=queue_name)

def store_insults(insults):
    for insult in insults:
        if insult not in insults_list:
            insults_list.append(insult)
            # print(f" [x] Insulto almacenado en InsultFilter: {insult}")

def filter_text(text, insults_list):
    filtered_text = text
    for insult in insults_list:
        filtered_text = filtered_text.replace(insult, "CENSORED")
    return filtered_text

def callback_insults(ch, method, properties, body):
    insults = body.decode().split(',')
    store_insults(insults)

def callback_texts(ch, method, properties, body):
    original_text = body.decode()
    # print(f" [x] Texto recibido para filtrar: {original_text}")
    filtered = filter_text(original_text, insults_list)
    # print(f" [x] Texto filtrado: {filtered}")

def consume_messages(queue_name, callback):
    connection = create_connection()
    channel = create_channel(connection)
    declare_queue(channel, queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    # print(f" [*] Esperando mensajes en {queue_name}")
    channel.start_consuming()

def consume_messages_in_threads():
    insults_thread = threading.Thread(target=consume_messages, args=('insults_to_filter', callback_insults))
    texts_thread = threading.Thread(target=consume_messages, args=('texts_to_filter', callback_texts))

    insults_thread.start()
    texts_thread.start()

    insults_thread.join()
    texts_thread.join()

if __name__ == '__main__':
    consume_messages_in_threads()
