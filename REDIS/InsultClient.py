import redis

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "INSULTS"

print("Consumer is waiting for tasks...")

llista = list()
while True:
    task = client.blpop(queue_name, timeout=0) # Blocks indefinitely until a task is available
    if task and task not in llista:
        llista.append(task)   
        print(f"Consumed: {task[1]}")