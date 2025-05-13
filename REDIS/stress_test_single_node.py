import redis
import time
import subprocess
import os

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def write_to_both(message, file):
    """Escribe el mensaje tanto en la terminal como en el archivo."""
    print(message)  # Imprime en la terminal
    file.write(message + "\n")  # Guarda en el archivo

def send_insults(client, queue_name, num_tasks, insults, file):
    """Envia tasques d'insults a la cua."""
    for i in range(num_tasks):
        insult = insults[i % len(insults)]  # Ciclo entre los insultos disponibles
        client.rpush(queue_name, insult)

def filter_insults(client, queue_name, result_queue_name, insults, file):
    """Consumeix les tasques de la cua, censura els insults i les envia a la cua de resultats."""
    tasks_processed = 0
    while tasks_processed < 100:  # Asumimos 100 tareas para este test
        task = client.blpop(queue_name, timeout=0)  # Bloqueja fins que una tasca estigui disponible
        text = task[1]
        
        # Reemplaza los insultos por 'CENSORED'
        for insult in insults:
            text = text.replace(insult, "CENSORED")
        
        # Guarda el texto filtrado en otra cola
        client.rpush(result_queue_name, text)
        tasks_processed += 1

def start_insult_service():
    """Inicia el proceso del InsultService usando subprocess (con python3)."""
    return subprocess.Popen(['python3', 'REDIS/InsultService.py'])

def start_insult_filter():
    """Inicia el proceso del InsultFilter usando subprocess (con python3)."""
    return subprocess.Popen(['python3', 'REDIS/InsultFilter.py'])

def test_insult_service(client, num_tasks, insults, file):
    """Test de rendimiento para InsultService (enviar insultos a la cola)."""
    results = []
    for n in num_tasks:
        start_time = time.time()
        send_insults(client, "INSULTS", n, insults, file)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result_message = f"Enviados {n} insultos en {elapsed_time:.5f} segundos."
        results.append(result_message)
        write_to_both(result_message, file)  # Se imprime en terminal y se guarda en archivo
    return results

def test_insult_filter(client, num_tasks, insults, file):
    """Test de rendimiento para InsultFilter (censurar frases)."""
    results = []
    for n in num_tasks:
        for _ in range(n):  # Simula enviar las frases con insultos
            client.rpush("TEXTS", "Eres un tonto")
            client.rpush("TEXTS", "Que bobo eres")
            client.rpush("TEXTS", "Eres una puta")
            client.rpush("TEXTS", "Eres un idiota")
            client.rpush("TEXTS", "Que cabron eres")
        
        start_time = time.time()
        filter_insults(client, "TEXTS", "RESULTS", insults, file)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result_message = f"Censurados {n} textos en {elapsed_time:.5f} segundos."
        results.append(result_message)
        write_to_both(result_message, file)  # Se imprime en terminal y se guarda en archivo
    return results

def execute_tests(client, num_tasks, insults):
    """Ejecuta todos los tests de InsultService y InsultFilter y guarda los resultados en un archivo."""
    # Crear directorio 'REDIS' si no existe
    if not os.path.exists("REDIS"):
        os.makedirs("REDIS")

    # Abrir el archivo para escribir los resultados
    with open("REDIS/test_results_s.txt", "w") as file:
        file.write("Resultados de las pruebas:\n")
        file.write("\n** Resultados de InsultService **\n")
        service_results = test_insult_service(client, num_tasks, insults, file)
        file.write("\n** Resultados de InsultFilter **\n")
        filter_results = test_insult_filter(client, num_tasks, insults, file)

def terminate_services(insult_service_process, insult_filter_process):
    """Termina los procesos de los servicios."""
    insult_service_process.terminate()
    insult_filter_process.terminate()
    print("Procesos de InsultService y InsultFilter terminados.")

if __name__ == "__main__":
    client = connect_to_redis()
    
    # Insultos a usar en las pruebas
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks = [1000, 5000, 10000, 20000]  # Diferentes tamaños de carga
    
    # Inicia los procesos del InsultService y el InsultFilter
    insult_service_process = start_insult_service()
    insult_filter_process = start_insult_filter()
    
    # Espera un momento para que los servicios se inicien correctamente
    time.sleep(5)
    
    # Ejecuta los tests y guarda los resultados en un archivo
    execute_tests(client, num_tasks, insults)

    # Finaliza los procesos
    terminate_services(insult_service_process, insult_filter_process)
