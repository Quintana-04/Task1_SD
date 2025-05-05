import redis
import time

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def get_tasks():
    """Retorna la llista de tasques a enviar a la cua."""
    return ["Perro", "Genimos payaso", "Jan bujarra", "Perro", "Puto nix"]

def send_tasks_to_queue(client, queue_name, tasks, delay=5):
    """Envia múltiples tasques a la cua especificada amb un retard entre elles."""
    for task in tasks:
        client.rpush(queue_name, task)
        print(f"Produced: {task}")
        time.sleep(delay)

# Codi principal
client = connect_to_redis()
queue_name = "INSULTS"
tasks = get_tasks()
send_tasks_to_queue(client, queue_name, tasks)
