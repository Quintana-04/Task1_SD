import time
import subprocess
import signal
import math
import sys
import threading
from xmlrpc.client import ServerProxy
import random

# Parámetros de test y carga para XMLRPC
T_INSULT = 2      # Tiempo de servicio (segundos) por nodo InsultService
C_INSULT = 0.5    # Capacidad por nodo (peticiones/segundo) InsultService

T_FILTER = 2      # Tiempo de servicio (segundos) por nodo InsultFilter
C_FILTER = 0.5    # Capacidad por nodo (peticiones/segundo) InsultFilter

TEST_DURATION = 40        # Duración total test (segundos)
MEASURE_INTERVAL = 3       # Medir lambda cada MEASURE INTERVAL segundos

# Carga objetivo total (Peticiones/segundo)
RATE_INSULTS = 5        # Peticiones/segundo totales a InsultService
RATE_TEXTS = 2          # Peticiones/segundo totales a InsultFilter

# Número inicial de procesos generadores de carga
LOAD_GEN_INSULT_PROCS = 1
LOAD_GEN_FILTER_PROCS = 1

# Rutas scripts de los servidores XMLRPC
INSULT_SERVICE_SCRIPT = "XMLRPC/InsultService.py"
INSULT_FILTER_SCRIPT = "XMLRPC/InsultFilter.py"

# Puertos base para nodos
INSULT_SERVICE_BASE_PORT = 8000
INSULT_FILTER_BASE_PORT = 8001

# Procesos nodos servidores
insult_nodes = []  # Lista de tuplas (process, port)
filter_nodes = []  # Lista de tuplas (process, port)

# Noleanos de control
running = True
load_generators_running = True

# Contadores para peticiones enviadas (para medir tasa real)
insult_requests_count = 0
filter_requests_count = 0

# Lock para proteger contadores
count_lock = threading.Lock()

def signal_handler(sig, frame):
    global running, load_generators_running
    print("\n[INFO] Control+C detectado, terminando procesos y carga...")
    running = False
    load_generators_running = False
    cleanup_processes()
    sys.exit(0)

# Vacia las listas de procesos activos, insult_nodes y filter_nodes, y los termina
def cleanup_processes():
    print("[INFO] Terminando procesos nodos...")
    for p, _ in insult_nodes + filter_nodes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception as e:
            print(f"[WARN] Error terminando proceso: {e}")
    insult_nodes.clear()
    filter_nodes.clear()
    print("[INFO] Todos los procesos nodos terminados.")

# Ejecuta un proceso por un puerto determinado
def start_node(script_path, port):
    proc = subprocess.Popen([sys.executable, script_path, str(port)])
    time.sleep(5)
    print(f"[INFO] Nodo lanzado: {script_path} en puerto {port}, PID={proc.pid}")
    return proc

# Detiene un solo proceso, el
def stop_node(process_tuple):
    proc, port = process_tuple
    if proc.poll() is None:
        print(f"[INFO] Terminando nodo PID={proc.pid} puerto={port}")
        proc.terminate()
        try:
            proc.wait(timeout=5)
            print(f"[INFO] Nodo PID={proc.pid} puerto={port} terminado.")
        except subprocess.TimeoutExpired:
            print(f"[WARN] Nodo PID={proc.pid} puerto={port} no respondió, matándolo.")
            proc.kill()

# Ejecuta más nodos, o termina algunos, dependiendo de la necesidad en ese momento
def scale_nodes(current_nodes, target_count, script_path, base_port):
    current_count = len(current_nodes)
    if target_count > current_count:
        for i in range(current_count, target_count):
            port = base_port + 2 * i  # Utilizamos puertos alternos
            proc = start_node(script_path, port)
            current_nodes.append((proc, port))
    elif target_count < current_count:
        for _ in range(current_count - target_count):
            proc_tuple = current_nodes.pop()
            stop_node(proc_tuple)

# Envia carga de trabajo al InsultService variando esta aleatoriamente a lo largo del tiempo
def load_generator_insult(rate_per_sec):
    global load_generators_running, insult_requests_count

    insults_sample = ["idiota", "tonto", "burro", "payaso", "torpe"]
    base_interval = 1.0 / rate_per_sec if rate_per_sec > 0 else 1

    while load_generators_running:
        with count_lock:
            if not insult_nodes:
                time.sleep(0.5)
                continue
            node_index = insult_requests_count % len(insult_nodes)
            _, port = insult_nodes[node_index]

        insult = random.choice(insults_sample)
        client = ServerProxy(f"http://localhost:{port}")
        try:
            client.recibir_insulto(insult)
            with count_lock:
                insult_requests_count += 1
        except Exception as e:
            print(f"[ERROR] InsultService XMLRPC puerto {port}: {e}")

        jitter = random.uniform(1, 3)
        time.sleep(base_interval * jitter)

# Envia carga de trabajo al InsultFilter variando esta aleatoriamente a lo largo del tiempo
def load_generator_text(rate_per_sec):
    global load_generators_running, filter_requests_count

    texts_sample = [
        "Hola, este es un texto sin insultos.",
        "Eres un idiota y un payaso.",
        "Vamos a censurar a ese tonto.",
        "Esto es un texto limpio.",
        "Qué burro eres."
    ]
    base_interval = 1.0 / rate_per_sec if rate_per_sec > 0 else 1

    while load_generators_running:
        with count_lock:
            if not filter_nodes:
                time.sleep(0.5)
                continue
            node_index = filter_requests_count % len(filter_nodes)
            _, port = filter_nodes[node_index]

        text = random.choice(texts_sample)
        client = ServerProxy(f"http://localhost:{port}")
        try:
            client.agregar_frase_a_cola(text)
            with count_lock:
                filter_requests_count += 1
        except Exception as e:
            print(f"[ERROR] InsultFilter XMLRPC puerto {port}: {e}")

        jitter = random.uniform(1, 3)
        time.sleep(base_interval * jitter)

# Calcula la lambda (peticiones enviadas) en tiempo real para el calculo de nodos
def measure_lambda_real():
    global insult_requests_count, filter_requests_count
    with count_lock:
        insult_count = insult_requests_count
        filter_count = filter_requests_count
        insult_requests_count = 0
        filter_requests_count = 0
    lam_insult = insult_count / MEASURE_INTERVAL
    lam_filter = filter_count / MEASURE_INTERVAL
    return lam_insult, lam_filter

# Ejecuta los tests con el numero de threads que le correspinde a cada uno, guarda resultados, y monitoriza el numero de nodos necesarios
def test_scaling():
    global running, load_generators_running

    insult_rate_per_proc = RATE_INSULTS / LOAD_GEN_INSULT_PROCS if LOAD_GEN_INSULT_PROCS > 0 else 0
    filter_rate_per_proc = RATE_TEXTS / LOAD_GEN_FILTER_PROCS if LOAD_GEN_FILTER_PROCS > 0 else 0

    insult_threads = []
    for _ in range(LOAD_GEN_INSULT_PROCS):
        t = threading.Thread(target=load_generator_insult, args=(insult_rate_per_proc,), daemon=True)
        insult_threads.append(t)
        t.start()

    filter_threads = []
    for _ in range(LOAD_GEN_FILTER_PROCS):
        t = threading.Thread(target=load_generator_text, args=(filter_rate_per_proc,), daemon=True)
        filter_threads.append(t)
        t.start()

    start_time = time.time()

    with open("XMLRPC/Dynamic/test_results_d.txt", "w") as log_file:
        log_file.write("=== Test de escalado dinámico XMLRPC iniciado ===\n\n")
        log_file.flush()

        while running and (time.time() - start_time < TEST_DURATION):
            time.sleep(MEASURE_INTERVAL)

            lam_insult, lam_filter = measure_lambda_real()

            # Cálculo nodos necesarios con la fórmula que nos dan
            nodos_insult = math.ceil(lam_insult * T_INSULT / C_INSULT)
            nodos_filter = math.ceil(lam_filter * T_FILTER / C_FILTER)
            nodos_insult = max(1, nodos_insult)
            nodos_filter = max(1, nodos_filter)

            timestamp = time.strftime('%H:%M:%S')

            # Construcción del mensaje detallado para InsultService
            formula_insult = f"nodos = ceil(lambda * T / C) = ceil({lam_insult:.2f} * {T_INSULT} / {C_INSULT}) = {nodos_insult}"
            decision_insult = "aumentar" if nodos_insult > len(insult_nodes) else ("disminuir" if nodos_insult < len(insult_nodes) else "mantener")
            detalle_insult = (
                f"[{timestamp}] InsultService:\n"
                f"  - Carga medida (lambda): {lam_insult:.2f} pet/s\n"
                f"  - Fórmula usada: {formula_insult}\n"
                f"  - Nodos actuales: {len(insult_nodes)}\n"
                f"  - Nodos requeridos: {nodos_insult} => Se decide {decision_insult} nodos\n"
            )

            # Construcción del mensaje detallado para InsultFilter
            formula_filter = f"nodos = ceil(lambda * T / C) = ceil({lam_filter:.2f} * {T_FILTER} / {C_FILTER}) = {nodos_filter}"
            decision_filter = "aumentar" if nodos_filter > len(filter_nodes) else ("disminuir" if nodos_filter < len(filter_nodes) else "mantener")
            detalle_filter = (
                f"[{timestamp}] InsultFilter:\n"
                f"  - Carga medida (lambda): {lam_filter:.2f} pet/s\n"
                f"  - Fórmula usada: {formula_filter}\n"
                f"  - Nodos actuales: {len(filter_nodes)}\n"
                f"  - Nodos requeridos: {nodos_filter} => Se decide {decision_filter} nodos\n"
            )

            print(detalle_insult.strip())
            print(detalle_filter.strip())
            log_file.write(detalle_insult + "\n" + detalle_filter + "\n")

            scale_nodes(insult_nodes, nodos_insult, INSULT_SERVICE_SCRIPT, INSULT_SERVICE_BASE_PORT)
            scale_nodes(filter_nodes, nodos_filter, INSULT_FILTER_SCRIPT, INSULT_FILTER_BASE_PORT)

            estado_post = (
                f"[{timestamp}] Estado post-escalado:\n"
                f"  - InsultService nodos activos: {len(insult_nodes)}\n"
                f"  - InsultFilter nodos activos: {len(filter_nodes)}\n\n"
            )
            print(estado_post.strip())
            log_file.write(estado_post)
            log_file.flush()

        print("[INFO] Duración del test alcanzada o detenido por usuario.")
        log_file.write("=== Test finalizado ===\n")

    load_generators_running = False
    for t in insult_threads + filter_threads:
        t.join()
    cleanup_processes()

# Programa principal
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("[INFO] Iniciando test de escalado dinámico XMLRPC con múltiples procesos generadores de carga.")
    print("Pulsa Ctrl+C para terminar.")
    test_scaling()
