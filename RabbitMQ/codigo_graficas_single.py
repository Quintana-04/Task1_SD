import matplotlib.pyplot as plt
import re

def parse_single_node_results(filename):
    num_tasks_list = []
    service_times = []
    filter_times = []

    with open(filename, 'r') as f:
        content = f.read()

    # Extraer líneas con tiempos InsultService
    service_matches = re.findall(
        r"Enviados (\d+) insultos a InsultService en ([\d\.]+) segundos",
        content)

    # Extraer líneas con tiempos InsultFilter
    filter_matches = re.findall(
        r"Enviados (\d+) textos a InsultFilter en ([\d\.]+) segundos",
        content)

    # Asumimos que el orden es consistente y las cantidades coinciden
    for num_tasks, t in service_matches:
        num_tasks_list.append(int(num_tasks))
        service_times.append(float(t))

    for _, t in filter_matches:
        filter_times.append(float(t))

    return num_tasks_list, service_times, filter_times

def plot_single_node_times(num_tasks_list, service_times, filter_times):
    plt.figure()
    plt.plot(num_tasks_list, service_times, marker='o', label='InsultService', color='blue')
    plt.plot(num_tasks_list, filter_times, marker='o', label='InsultFilter', color='orange')
    plt.title('Tiempo vs Cantidad de datos (RabbitMQ)')
    plt.xlabel('Cantidad de datos')
    plt.ylabel('Tiempo (segundos)')
    plt.grid(True)
    plt.legend()
    plt.savefig('RabbitMQ/single_node_times.png')
    plt.close()

if __name__ == "__main__":
    filename = 'RabbitMQ/test_results_s.txt'
    num_tasks_list, service_times, filter_times = parse_single_node_results(filename)
    plot_single_node_times(num_tasks_list, service_times, filter_times)
