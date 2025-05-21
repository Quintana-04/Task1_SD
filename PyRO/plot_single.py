import matplotlib.pyplot as plt
import re
import os

def parse_results(filename):
    insults_tasks = []
    insults_times = []
    filter_tasks = []
    filter_times = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            m_insult = re.match(r"Enviados (\d+) insultos en ([\d\.]+) segundos.", line)
            m_filter = re.match(r"Censurados (\d+) textos en ([\d\.]+) segundos.", line)
            if m_insult:
                insults_tasks.append(int(m_insult.group(1)))
                insults_times.append(float(m_insult.group(2)))
            elif m_filter:
                filter_tasks.append(int(m_filter.group(1)))
                filter_times.append(float(m_filter.group(2)))

    return insults_tasks, insults_times, filter_tasks, filter_times

def plot_times(insults_tasks, insults_times, filter_tasks, filter_times):
    output_dir = "PYRO/Plots"
    os.makedirs(output_dir, exist_ok=True)

    plt.figure()
    plt.plot(insults_tasks, insults_times, label="InsultService", color='blue', marker='o')
    plt.plot(filter_tasks, filter_times, label="InsultFilter", color='orange', marker='o')
    plt.xlabel("Cantidad de peticiones")
    plt.ylabel("Tiempo (segundos)")
    plt.title("Tiempo vs Cantidad de datos (PyRO)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/tiempos_insultservice_insultfilter.png")
    plt.show()

if __name__ == "__main__":
    filename = "PYRO/test_results_s.txt"
    insults_tasks, insults_times, filter_tasks, filter_times = parse_results(filename)
    plot_times(insults_tasks, insults_times, filter_tasks, filter_times)
