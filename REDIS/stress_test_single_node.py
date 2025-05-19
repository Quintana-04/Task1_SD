import redis
import time
import subprocess
import os

def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

def send_insults(client, queue_name, num_tasks, insults, file):
    """Envía insultos solo a la cola 'INSULTS' para InsultService."""
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        client.rpush(queue_name, insult)
    # write_to_both(f"Enviados {num_tasks} insultos a InsultService en la cola {queue_name}", file)

def send_texts(client, queue_name, num_tasks, insults, file):
    """Envía textos para filtrar a la cola 'TEXT' para InsultFilter."""
    texts = [
        "Eres un tonto",
        "Que bobo eres",
        "Eres una puta",
        "Eres un idiota",
        "Que cabron eres"
    ]
    for _ in range(num_tasks):
        for text in texts:
            client.rpush(queue_name, text)
    # write_to_both(f"Enviados {num_tasks} textos a InsultFilter en la cola {queue_name}", file)

def start_insult_service():
    return subprocess.Popen(['python3', 'REDIS/InsultService.py'])

def start_insult_filter():
    return subprocess.Popen(['python3', 'REDIS/InsultFilter.py'])

def test_insult_service(client, num_tasks_list, insults, file):
    results = []
    for n in num_tasks_list:
        start_time = time.time()
        send_insults(client, "INSULTS", n, insults, file)
        end_time = time.time()
        elapsed_time = end_time - start_time
        msg = f"Enviados {n} insultos en {elapsed_time:.5f} segundos."
        write_to_both(msg, file)
        results.append(msg)
    return results

def test_insult_filter(client, num_tasks_list, insults, file):
    results = []
    for n in num_tasks_list:
        start_time = time.time()
        send_texts(client, "TEXT", n, insults, file)
        end_time = time.time()
        elapsed_time = end_time - start_time
        msg = f"Enviados {n} textos en {elapsed_time:.5f} segundos."
        write_to_both(msg, file)
        results.append(msg)
    return results

def execute_tests(client, num_tasks_list, insults):
    if not os.path.exists("REDIS"):
        os.makedirs("REDIS")

    with open("REDIS/test_results_s.txt", "w") as file:
        file.write("Resultados de las pruebas single-node Redis:\n")

        insult_service_process = start_insult_service()
        insult_filter_process = start_insult_filter()

        time.sleep(5)  # Esperar que los servicios inicien

        file.write("\n** Resultados de InsultService **\n")
        test_insult_service(client, num_tasks_list, insults, file)
        file.write("\n** Resultados de InsultFilter **\n")
        test_insult_filter(client, num_tasks_list, insults, file)

        insult_service_process.terminate()
        insult_filter_process.terminate()
        print("Servicios de Redis terminados.")

if __name__ == "__main__":
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks_list = [1000, 5000, 10000, 20000]

    execute_tests(client, num_tasks_list, insults)
