import pika
import subprocess
import time
import os

def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

def send_insults(num_tasks, insults):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    queue_name = 'insults_to_censor'  # Solo enviamos aquí los insultos
    channel.queue_declare(queue=queue_name)

    start_time = time.time()
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        channel.basic_publish(exchange='', routing_key=queue_name, body=insult)
    end_time = time.time()

    connection.close()
    return end_time - start_time

def send_texts(num_tasks, insults):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    queue_name = 'texts_to_filter'
    channel.queue_declare(queue=queue_name)

    texts = [
        "Eres un tonto",
        "Que bobo eres",
        "Eres una puta",
        "Eres un idiota",
        "Que cabron eres"
    ]

    start_time = time.time()
    for _ in range(num_tasks):
        for text in texts:
            channel.basic_publish(exchange='', routing_key=queue_name, body=text)
    end_time = time.time()

    connection.close()
    return end_time - start_time

def start_insult_service():
    return subprocess.Popen(['python3', 'RabbitMQ/InsultService.py'])

def start_insult_filter():
    return subprocess.Popen(['python3', 'RabbitMQ/InsultFilter.py'])

def calculate_speedup(time_single, time_multi):
    if time_multi > 0:
        return time_single / time_multi
    return 0

def test_insult_service(num_tasks, insults):
    return send_insults(num_tasks, insults)

def test_insult_filter(num_tasks, insults):
    return send_texts(num_tasks, insults)

def terminate_services(processes):
    for p in processes:
        p.terminate()

def execute_multiple_nodes_test(num_tasks_list, insults):
    if not os.path.exists("RabbitMQ"):
        os.makedirs("RabbitMQ")

    with open("RabbitMQ/test_results_m.txt", "w") as file:
        file.write("Resultados de las pruebas - Múltiples Nodos:\n")

        times_service_1node = {}
        times_filter_1node = {}

        for num_nodes in [1, 2, 3]:
            file.write(f"\n** Test con {num_nodes} Nodo(s) **\n")
            for num_tasks in num_tasks_list:
                file.write(f"\n--- Test con {num_nodes} Nodo(s) y {num_tasks} datos ---\n")

                if num_nodes == 1:
                    service_proc = [start_insult_service()]
                    filter_proc = [start_insult_filter()]
                    time.sleep(5)

                    service_time = test_insult_service(num_tasks, insults)
                    filter_time = test_insult_filter(num_tasks, insults)

                    times_service_1node[num_tasks] = service_time
                    times_filter_1node[num_tasks] = filter_time

                    terminate_services(service_proc)
                    terminate_services(filter_proc)

                    write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time:.5f} segundos", file)
                    write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time:.5f} segundos", file)

                else:
                    service_proc = [start_insult_service() for _ in range(num_nodes)]
                    filter_proc = [start_insult_filter() for _ in range(num_nodes)]
                    time.sleep(5)

                    service_time = test_insult_service(num_tasks, insults)
                    filter_time = test_insult_filter(num_tasks, insults)

                    speedup_service = calculate_speedup(times_service_1node[num_tasks], service_time)
                    speedup_filter = calculate_speedup(times_filter_1node[num_tasks], filter_time)

                    terminate_services(service_proc)
                    terminate_services(filter_proc)

                    write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time:.5f} segundos", file)
                    write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time:.5f} segundos", file)
                    file.write(f"Speedup de InsultService con {num_nodes} nodos: {speedup_service:.5f}\n")
                    file.write(f"Speedup de InsultFilter con {num_nodes} nodos: {speedup_filter:.5f}\n")

if __name__ == "__main__":
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks_list = [1000, 5000, 10000, 20000]

    execute_multiple_nodes_test(num_tasks_list, insults)
