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
    start_time = time.time()
    send_insults(client, "INSULTS", num_tasks, insults, file)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def test_insult_filter(client, num_tasks, insults, file):
    """Test de rendimiento para InsultFilter (censurar frases)."""
    start_time = time.time()
    filter_insults(client, "TEXTS", "RESULTS", insults, file)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def calculate_speedup(single_node_time, multi_node_time):
    """Calcula el speedup."""
    if multi_node_time > 0:
        return single_node_time / multi_node_time
    return 0

def execute_multiple_nodes_test(client, num_tasks, insults):
    """Ejecuta los tests de múltiples nodos (1, 2, 3 nodos) y guarda los resultados en un archivo."""
    # Abrir el archivo para escribir los resultados
    with open("REDIS/test_results_m.txt", "w") as file:
        file.write("Resultados de las pruebas - Múltiples Nodos:\n")
        
        # Realizar pruebas con diferentes números de nodos y datos
        for num_nodes in [1, 2, 3]:
            for n in num_tasks:
                file.write(f"\n** Test con {num_nodes} Nodo(s) y {n} datos **\n")
                
                # Test con 1, 2 o 3 nodos
                if num_nodes == 1:
                    service_time_1 = test_insult_service(client, n, insults, file)
                    filter_time_1 = test_insult_filter(client, n, insults, file)
                    speedup_service_1 = 1  # No hay speedup con 1 nodo
                    speedup_filter_1 = 1  # No hay speedup con 1 nodo
                else:
                    # Inicia los procesos para múltiples nodos
                    insult_service_process = [start_insult_service() for _ in range(num_nodes)]
                    insult_filter_process = [start_insult_filter() for _ in range(num_nodes)]
                    time.sleep(5)  # Espera para que los servicios estén listos
                    service_time_multi = test_insult_service(client, n, insults, file)
                    filter_time_multi = test_insult_filter(client, n, insults, file)
                    speedup_service_multi = calculate_speedup(service_time_1, service_time_multi)
                    speedup_filter_multi = calculate_speedup(filter_time_1, filter_time_multi)
                    file.write(f"Speedup de InsultService con {num_nodes} nodos: {speedup_service_multi:.5f}\n")
                    file.write(f"Speedup de InsultFilter con {num_nodes} nodos: {speedup_filter_multi:.5f}\n")
                    
                # Escribe los resultados finales en el archivo y terminal
                write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time_1:.5f} segundos", file)
                write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time_1:.5f} segundos", file)

        # Terminamos los procesos después de las pruebas
        terminate_services(insult_service_process, insult_filter_process)

def terminate_services(insult_service_process, insult_filter_process):
    """Termina los procesos de los servicios."""
    for p in insult_service_process:
        p.terminate()
    for p in insult_filter_process:
        p.terminate()
    print("Procesos de InsultService y InsultFilter terminados.")

if __name__ == "__main__":
    client = connect_to_redis()
    
    # Insultos a usar en las pruebas
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks = [1000, 5000, 10000, 20000]  # Diferentes tamaños de carga
    
    # Ejecuta los tests de múltiples nodos (1, 2, 3 nodos)
    execute_multiple_nodes_test(client, num_tasks, insults)
