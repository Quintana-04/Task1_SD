import matplotlib.pyplot as plt
import re

def parse_xmlrpc_results(filename):
    times_service = {1: [], 2: [], 3: []}
    times_filter = {1: [], 2: [], 3: []}
    speedup_service = {2: [], 3: []}
    speedup_filter = {2: [], 3: []}
    num_tasks_list = []

    with open(filename, 'r') as f:
        content = f.read()

    # Separamos por los bloques "--- Test con X Nodo(s) y Y datos ---"
    bloques = re.split(r"--- Test con (\d+) Nodo\(s\) y (\d+) datos ---", content)

    # En el split, bloques[i] es texto, i+1 es nodo, i+2 tareas, i+3 bloque datos
    for i in range(1, len(bloques), 3):
        nodo = int(bloques[i])
        tareas = int(bloques[i+1])
        bloque = bloques[i+2]

        ts_match = re.search(r"Tiempo InsultService con \d+ nodos: ([\d\.]+) segundos", bloque)
        tf_match = re.search(r"Tiempo InsultFilter con \d+ nodos: ([\d\.]+) segundos", bloque)
        su_s_match = re.search(r"Speedup de InsultService con \d+ nodos: ([\d\.]+)", bloque)
        su_f_match = re.search(r"Speedup de InsultFilter con \d+ nodos: ([\d\.]+)", bloque)

        if ts_match and tf_match:
            ts = float(ts_match.group(1))
            tf = float(tf_match.group(1))
            su_s = float(su_s_match.group(1)) if su_s_match else None
            su_f = float(su_f_match.group(1)) if su_f_match else None

            if nodo == 1:
                num_tasks_list.append(tareas)

            times_service[nodo].append(ts)
            times_filter[nodo].append(tf)

            if nodo in [2,3]:
                speedup_service[nodo].append(su_s)
                speedup_filter[nodo].append(su_f)

    return num_tasks_list, times_service, times_filter, speedup_service, speedup_filter

def plot_xmlrpc_times(num_tasks_list, times_service, times_filter):
    green_shades = ['#2ca02c', '#98df8a', '#c7e9c0']
    red_shades = ['#d62728', '#ff9896', '#f7c6c5']

    plt.figure(figsize=(10,6))
    for i, nodo in enumerate([1,2,3]):
        plt.plot(num_tasks_list, times_service[nodo], marker='o', color=green_shades[i], label=f'InsultService {nodo} nodo(s)')
        plt.plot(num_tasks_list, times_filter[nodo], marker='o', linestyle='--', color=red_shades[i], label=f'InsultFilter {nodo} nodo(s)')
    plt.title('Tiempos de procesamiento vs cantidad de datos (XMLRPC Múltiples Nodos)')
    plt.xlabel('Cantidad de datos')
    plt.ylabel('Tiempo (segundos)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('xmlrpc_multiple_nodes_times.png')
    plt.close()

def plot_xmlrpc_speedups(num_tasks_list, speedup_service, speedup_filter):
    green_shades = ['#98df8a', '#c7e9c0']  # para 2 y 3 nodos
    red_shades = ['#ff9896', '#f7c6c5']

    plt.figure(figsize=(10,6))
    for i, nodo in enumerate([2,3]):
        plt.plot(num_tasks_list, speedup_service[nodo], marker='o', color=green_shades[i], label=f'Speedup InsultService {nodo} nodos')
        plt.plot(num_tasks_list, speedup_filter[nodo], marker='o', linestyle='--', color=red_shades[i], label=f'Speedup InsultFilter {nodo} nodos')
    plt.title('Speedup vs Cantidad de datos (XMLRPC)')
    plt.xlabel('Cantidad de datos')
    plt.ylabel('Speedup')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('xmlrpc_multiple_nodes_speedup.png')
    plt.close()

if __name__ == "__main__":
    filename = 'XMLRPC/test_results_m.txt'
    num_tasks_list, times_service, times_filter, speedup_service, speedup_filter = parse_xmlrpc_results(filename)

    plot_xmlrpc_times(num_tasks_list, times_service, times_filter)
    plot_xmlrpc_speedups(num_tasks_list, speedup_service, speedup_filter)
