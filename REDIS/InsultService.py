import redis
import time

def connect_to_redis(host='localhost', port=6379, db=0):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def consume_tasks_from_queue(client, queue_name, queue_name_filter):
    insults_list = []
    while True:
        task = client.blpop(queue_name, timeout=0)  # Espera insultos en la cola INSULTS
        insult = task[1]
        if insult not in insults_list:
            insults_list.append(insult)
            # print(f"Insulto almacenado en InsultService: {insult}")
            # Enviar insulto almacenado a cola INSULTS_FILTER para el filtro
            client.rpush(queue_name_filter, insult)
            # print(f"Enviado insulto a InsultFilter: {insult}")
        # Aquí puedes agregar alguna condición para salir si quieres

def main():
    client = connect_to_redis()
    queue_name = "INSULTS"           # Cola donde recibe insultos del cliente
    queue_name_filter = "INSULTS_FILTER"  # Cola donde manda insultos para InsultFilter

    consume_tasks_from_queue(client, queue_name, queue_name_filter)

if __name__ == "__main__":
    main()
