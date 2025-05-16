# main_performance.py
import multiprocessing
import time
import subprocess
import random

# Función para generar frases de prueba
def generar_frases(n):
    frases = []
    for _ in range(n):
        frase = "Eres un " + random.choice(["maldito", "idiota", "estúpido", "imbécil"]) + " tipo."
        frases.append(frase)
    return frases

# Función para ejecutar el servicio InsultService
def run_insult_service():
    subprocess.run(["python", "XMLRPC/InsultService.py"])

# Función para ejecutar el servicio InsultFilter
def run_insult_filter():
    subprocess.run(["python", "XMLRPC/InsultFilter.py"])

# Función para medir el rendimiento con un número específico de nodos
def medir_rendimiento(num_nodos):
    print(f"Ejecutando el sistema con {num_nodos} nodos...")
    
    # Crear y lanzar los procesos
    if num_nodos == 1:
        # 1 nodo: 1 InsultService y 1 InsultFilter
        process_insult_service = multiprocessing.Process(target=run_insult_service)
        process_insult_filter = multiprocessing.Process(target=run_insult_filter)
        process_insult_service.start()
        process_insult_filter.start()

        process_insult_service.join()
        process_insult_filter.join()

    elif num_nodos == 2:
        # 2 nodos: 1 InsultService y 2 InsultFilters
        process_insult_service = multiprocessing.Process(target=run_insult_service)
        process_insult_filter1 = multiprocessing.Process(target=run_insult_filter)
        process_insult_filter2 = multiprocessing.Process(target=run_insult_filter)

        process_insult_service.start()
        process_insult_filter1.start()
        process_insult_filter2.start()

        process_insult_service.join()
        process_insult_filter1.join()
        process_insult_filter2.join()

    elif num_nodos == 3:
        # 3 nodos: 1 InsultService y 3 InsultFilters
        process_insult_service = multiprocessing.Process(target=run_insult_service)

        process_insult_filter1 = multiprocessing.Process(target=run_insult_filter)
        process_insult_filter2 = multiprocessing.Process(target=run_insult_filter)
        process_insult_filter3 = multiprocessing.Process(target=run_insult_filter)

        process_insult_service.start()

        process_insult_filter1.start()
        process_insult_filter2.start()
        process_insult_filter3.start()

        process_insult_service.join()

        process_insult_filter1.join()
        process_insult_filter2.join()
        process_insult_filter3.join()

# Función para realizar el stress test y calcular el speedup
def stress_test(num_nodos, num_frases=100):
    frases = generar_frases(num_frases)

    # Medir el tiempo de ejecución con el número de nodos
    start_time = time.time()
    medir_rendimiento(num_nodos)
    end_time = time.time()

    # Calcular el tiempo de ejecución
    tiempo_ejecucion = end_time - start_time
    print(f"Tiempo de ejecución con {num_nodos} nodos: {tiempo_ejecucion:.2f} segundos")
    return tiempo_ejecucion

def calcular_speedup(tiempos):
    # Calcular el speedup con el número de nodos
    speedups = []
    for i in range(1, len(tiempos)):
        speedup = tiempos[0] / tiempos[i]
        speedups.append(speedup)
    return speedups

if __name__ == "__main__":
    tiempos = []
    
    # Realizar stress test para 1, 2 y 3 nodos
    for nodos in [1, 2, 3]:
        tiempo = stress_test(3)
        tiempos.append(tiempo)

    # Calcular speedups
    speedups = calcular_speedup(tiempos)
    
    # Imprimir los resultados
    print("\nSpeedups:")
    for i, speedup in enumerate(speedups):
        print(f"Speedup con {i+2} nodos: {speedup:.2f}")
