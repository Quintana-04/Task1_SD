import matplotlib.pyplot as plt
import re

def parse_results(filename):
    times_service = {1: [], 2: [], 3: []}
    times_filter = {1: [], 2: [], 3: []}
    speedup_service = {2: [], 3: []}
    speedup_filter = {2: [], 3: []}
    num_tasks_list = []

    with open(filename, 'r') as f:
        content = f.read()

    node_blocks = re.split(r"\*\* Test con (\d+) Nodo\(s\) \*\*", content)

    for i in range(1, len(node_blocks), 2):
        node_num = int(node_blocks[i])
        block = node_blocks[i+1]

        matches = re.findall(
            r"--- Test con \d+ Nodo\(s\) y (\d+) datos ---\s+"
            r"Tiempo InsultService con \d+ nodos: ([\d\.]+) segundos\s+"
            r"Tiempo InsultFilter con \d+ nodos: ([\d\.]+) segundos"
            r"(?:\s+Speedup de InsultService con \d+ nodos: ([\d\.]+))?"
            r"(?:\s+Speedup de InsultFilter con \d+ nodos: ([\d\.]+))?", block)

        for m in matches:
            num_tasks = int(m[0])
            ts = float(m[1])
            tf = float(m[2])
            su_s = float(m[3]) if m[3] else None
            su_f = float(m[4]) if m[4] else None

            if node_num == 1:
                num_tasks_list.append(num_tasks)
            times_service[node_num].append(ts)
            times_filter[node_num].append(tf)
            if node_num in [2, 3]:
                speedup_service[node_num].append(su_s)
                speedup_filter[node_num].append(su_f)

    return num_tasks_list, times_service, times_filter, speedup_service, speedup_filter

def plot_times(num_tasks_list, times_service, times_filter):
    green_shades = ['#2ca02c', '#98df8a', '#c7e9c0']
    red_shades = ['#d62728', '#ff9896', '#f7c6c5']

    plt.figure(figsize=(10,6))
    for i, node in enumerate([1,2,3]):
        plt.plot(num_tasks_list, times_service[node], marker='o', color=green_shades[i], label=f'InsultService {node} nodo(s)')
        plt.plot(num_tasks_list, times_filter[node], marker='o', linestyle='--', color=red_shades[i], label=f'InsultFilter {node} nodo(s)')
    plt.title('Tiempos de procesamiento vs cantidad de datos (REDIS)')
    plt.xlabel('Cantidad de datos')
    plt.ylabel('Tiempo (segundos)')
    plt.grid(True)
    plt.legend()
    plt.savefig('REDIS/multiple_nodes_times.png')
    plt.close()

def plot_speedups(num_tasks_list, speedup_service, speedup_filter):
    green_shades = ['#98df8a', '#c7e9c0']  # para 2 y 3 nodos
    red_shades = ['#ff9896', '#f7c6c5']

    plt.figure(figsize=(10,6))
    for i, node in enumerate([2,3]):
        plt.plot(num_tasks_list, speedup_service[node], marker='o', color=green_shades[i], label=f'Speedup InsultService {node} nodos')
        plt.plot(num_tasks_list, speedup_filter[node], marker='o', linestyle='--', color=red_shades[i], label=f'Speedup InsultFilter {node} nodos')
    plt.title('Speedup vs cantidad de datos (REDIS)')
    plt.xlabel('Cantidad de datos')
    plt.ylabel('Speedup')
    plt.grid(True)
    plt.legend()
    plt.savefig('REDIS/multiple_nodes_speedup.png')
    plt.close()

if __name__ == "__main__":
    filename = 'REDIS/test_results_m.txt'
    num_tasks_list, times_service, times_filter, speedup_service, speedup_filter = parse_results(filename)

    plot_times(num_tasks_list, times_service, times_filter)
    plot_speedups(num_tasks_list, speedup_service, speedup_filter)
