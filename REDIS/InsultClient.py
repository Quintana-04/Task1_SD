import redis
import time

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def get_insults():
    """Retorna la llista de insults a enviar a la cua."""
    return ["perro", "payaso", "bujarra", "puto"]

def get_text():
    """Retorna els textos a enviar a la cua"""
    return ["Bon dia perro puto jan", "Pasando del puto nixs", "Genis bujarra si", "Raul payaso"]

def send_insults_to_queue(client, queue_name1, tasks, delay=3):
    """Envia múltiples tasques a la cua especificada amb un retard entre elles."""
    for task in tasks:
        client.rpush(queue_name1, task)
        print(f"Produced: {task}")
        #time.sleep(delay)

def send_tasks_to_queue(client, queue_name2, texts, delay=5):
    time.sleep(delay)
    for text in texts:
        client.rpush(queue_name2, text)
        print(f"Produced: {text}")
        time.sleep(delay)

# Codi principal
client = connect_to_redis()
queue_name1 = "INSULTS"
queue_name2 = "TEXT"
tasks = get_insults()
send_insults_to_queue(client, queue_name1, tasks)
texts = get_text()
send_tasks_to_queue(client, queue_name2, texts)