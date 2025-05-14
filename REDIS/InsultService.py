import redis

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def consume_tasks_from_queue(client, queue_name):
    """Consumeix tasques de la cua de Redis i les imprimeix."""
    #print("Consumer is waiting for tasks...")
    tasks_list = []
    
    while True:
        task = client.blpop(queue_name, timeout=0)  # Bloqueja fins que una tasca estigui disponible
        #if task and task not in tasks_list:
        tasks_list.append(task)
        #print(f"Consumed: {task[1]}")

#Codi principal
client = connect_to_redis()
queue_name = "INSULTS"
consume_tasks_from_queue(client, queue_name)