import pika
import subprocess
import time
import os

def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

def send_insults(num_tasks, insults, file):
    """Envía insultos SOLO a la cola 'insults_to_censor' para InsultService."""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    queue_name = 'insults_to_censor'
    channel.queue_declare(queue=queue_name)

    start_time = time.time()
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        channel.basic_publish(exchange='', routing_key=queue_name, body=insult)
    end_time = time.time()

    elapsed_time = end_time - start_time
    write_to_both(f"Enviados {num_tasks} insultos a InsultService en {elapsed_time:.5f} segundos.", file)
    connection.close()
    return elapsed_time

def send_texts(num_tasks, insults, file):
    """Envía textos para filtrar a la cola 'texts_to_filter' para InsultFilter."""
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

    elapsed_time = end_time - start_time
    write_to_both(f"Enviados {num_tasks} textos a InsultFilter en {elapsed_time:.5f} segundos.", file)
    connection.close()
    return elapsed_time

def start_insult_service():
    return subprocess.Popen(['python3', 'RabbitMQ/InsultService.py'])

def start_insult_filter():
    return subprocess.Popen(['python3', 'RabbitMQ/InsultFilter.py'])

def test_insult_service(num_tasks_list, insults, file):
    results = []
    for num_tasks in num_tasks_list:
        elapsed_time = send_insults(num_tasks, insults, file)
        msg = f"Enviados {num_tasks} insultos a InsultService en {elapsed_time:.5f} segundos."
        #write_to_both(msg, file)
        results.append(msg)
    return results

def test_insult_filter(num_tasks_list, insults, file):
    results = []
    for num_tasks in num_tasks_list:
        elapsed_time = send_texts(num_tasks, insults, file)
        msg = f"Enviados {num_tasks} textos a InsultFilter en {elapsed_time:.5f} segundos."
        #write_to_both(msg, file)
        results.append(msg)
    return results

def execute_tests(num_tasks_list, insults):
    if not os.path.exists("RabbitMQ"):
        os.makedirs("RabbitMQ")

    with open("RabbitMQ/test_results_s.txt", "w") as file:
        file.write("Resultados de las pruebas single-node RabbitMQ:\n")

        insult_service_process = start_insult_service()
        insult_filter_process = start_insult_filter()

        time.sleep(2)  # Esperar que los servicios inicien

        file.write("\n** Resultados de InsultService **\n")
        test_insult_service(num_tasks_list, insults, file)
        file.write("\n** Resultados de InsultFilter **\n")
        test_insult_filter(num_tasks_list, insults, file)

        insult_service_process.terminate()
        insult_filter_process.terminate()
        print("Servicios de RabbitMQ terminados.")

if __name__ == "__main__":
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks_list = [1000, 5000, 10000, 20000]

    execute_tests(num_tasks_list, insults)
