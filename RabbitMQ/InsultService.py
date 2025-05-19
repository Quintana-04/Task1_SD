import pika

# Lista local para almacenar insultos
lista_insultos = []

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    return connection.channel()

def declare_queue(channel, queue_name='insults_to_censor'):
    channel.queue_declare(queue=queue_name)

def declare_queue_filter(channel, queue_name='insults_to_filter'):
    channel.queue_declare(queue=queue_name)

def send_insults_to_filter(channel, insults):
    """Envía insultos almacenados a la cola de insultos para el filtro."""
    if insults:
        # Enviamos insultos separados por comas en un solo mensaje
        message = ",".join(insults)
        channel.basic_publish(exchange='', routing_key='insults_to_filter', body=message)
        # print(f" [x] Enviados insultos a InsultFilter: {message}")

def callback(ch, method, properties, body):
    insulto = body.decode()
    if insulto not in lista_insultos:
        lista_insultos.append(insulto)
        # print(f" [x] Insulto recibido y almacenado: {insulto}")
        # Enviar insultos actualizados a InsultFilter, pasando directamente ch (que es el canal)
        send_insults_to_filter(ch, lista_insultos)

def consume_messages(channel, queue_name='insults_to_censor'):
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    # print(' [*] Esperando insultos en InsultService. Para salir, CTRL+C')
    channel.start_consuming()

def main():
    connection = create_connection()
    channel = create_channel(connection)

    declare_queue(channel, 'insults_to_censor')
    declare_queue_filter(channel, 'insults_to_filter')

    consume_messages(channel, 'insults_to_censor')

if __name__ == '__main__':
    main()
