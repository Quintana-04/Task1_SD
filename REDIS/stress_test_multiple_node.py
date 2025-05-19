import redis
import time
import subprocess
import os

def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

def send_insults(client, queue_name, num_tasks, insults):
    """Envía insultos solo a la cola 'INSULTS' para InsultService."""
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        client.rpush(queue_name, insult)

def send_texts(client, queue_name, num_tasks, insults):
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

def start_insult_service():
    return subprocess.Popen(['python3', 'REDIS/InsultService.py'])

def start_insult_filter():
    return subprocess.Popen(['python3', 'REDIS/InsultFilter.py'])

def calculate_speedup(time_single, time_multi):
    if time_multi > 0:
        return time_single / time_multi
    return 0

def test_insult_service(client, num_tasks, insults):
    start_time = time.time()
    send_insults(client, "INSULTS", num_tasks, insults)
    end_time = time.time()
    return end_time - start_time

def test_insult_filter(client, num_tasks, insults):
    start_time = time.time()
    send_texts(client, "TEXT", num_tasks, insults)
    end_time = time.time()
    return end_time - start_time

def terminate_services(insult_service_processes, insult_filter_processes):
    for p in insult_service_processes:
        p.terminate()
    for p in insult_filter_processes:
        p.terminate()
    print("Procesos de InsultService y InsultFilter terminados.")

def execute_multiple_nodes_test(client, num_tasks_list, insults):
    if not os.path.exists("REDIS"):
        os.makedirs("REDIS")

    with open("REDIS/test_results_m.txt", "w") as file:
        file.write("Resultados de las pruebas - Múltiples Nodos Redis:\n")

        times_service_1node = {}
        times_filter_1node = {}

        for num_nodes in [1, 2, 3]:
            file.write(f"\n** Test con {num_nodes} Nodo(s) **\n")
            for num_tasks in num_tasks_list:
                file.write(f"\n--- Test con {num_nodes} Nodo(s) y {num_tasks} datos ---\n")

                if num_nodes == 1:
                    insult_service_process = [start_insult_service()]
                    insult_filter_process = [start_insult_filter()]
                    time.sleep(5)

                    service_time = test_insult_service(client, num_tasks, insults)
                    filter_time = test_insult_filter(client, num_tasks, insults)

                    times_service_1node[num_tasks] = service_time
                    times_filter_1node[num_tasks] = filter_time

                    terminate_services(insult_service_process, insult_filter_process)

                    write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time:.5f} segundos", file)
                    write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time:.5f} segundos", file)

                else:
                    insult_service_process = [start_insult_service() for _ in range(num_nodes)]
                    insult_filter_process = [start_insult_filter() for _ in range(num_nodes)]
                    time.sleep(5)

                    service_time = test_insult_service(client, num_tasks, insults)
                    filter_time = test_insult_filter(client, num_tasks, insults)

                    speedup_service = calculate_speedup(times_service_1node[num_tasks], service_time)
                    speedup_filter = calculate_speedup(times_filter_1node[num_tasks], filter_time)

                    terminate_services(insult_service_process, insult_filter_process)

                    write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time:.5f} segundos", file)
                    write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time:.5f} segundos", file)
                    file.write(f"Speedup de InsultService con {num_nodes} nodos: {speedup_service:.5f}\n")
                    file.write(f"Speedup de InsultFilter con {num_nodes} nodos: {speedup_filter:.5f}\n")

if __name__ == "__main__":
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks_list = [1000, 5000, 10000, 20000]

    execute_multiple_nodes_test(client, num_tasks_list, insults)
