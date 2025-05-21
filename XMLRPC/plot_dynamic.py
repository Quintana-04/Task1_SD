import re
import matplotlib.pyplot as plt
from datetime import datetime

def parse_dynamic_scaling_log(filename):
    timestamps = []
    lambda_insult = []
    lambda_filter = []
    nodos_activos_insult = []
    nodos_activos_filter = []

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Patrón para bloques de InsultService o InsultFilter con lambda y nodos requeridos
    pattern_lambda = re.compile(
        r"\[(\d{2}:\d{2}:\d{2})\] (InsultService|InsultFilter):\n"
        r"  - Carga medida \(lambda\): ([\d\.]+) pet/s\n"
        r"  - Fórmula usada: .*\n"
        r"  - Nodos actuales: (\d+)\n"
        r"  - Nodos requeridos: \d+ => Se decide (aumentar|disminuir|mantener) nodos"
    )

    # Patrón para estado post-escalado
    pattern_estado = re.compile(
        r"\[(\d{2}:\d{2}:\d{2})\] Estado post-escalado:\n"
        r"  - InsultService nodos activos: (\d+)\n"
        r"  - InsultFilter nodos activos: (\d+)"
    )

    # Diccionarios temporales para guardar lambda por timestamp
    lambdas_tmp = {}
    nodos_tmp = {}

    for match in pattern_lambda.finditer(content):
        ts_str, servicio, lam, nodos_actuales, decision = match.groups()
        lam = float(lam)
        nodos_actuales = int(nodos_actuales)
        key = (ts_str)

        if key not in lambdas_tmp:
            lambdas_tmp[key] = {}
        lambdas_tmp[key][servicio] = lam

    for match in pattern_estado.finditer(content):
        ts_str, nodos_insult, nodos_filter = match.groups()
        nodos_insult = int(nodos_insult)
        nodos_filter = int(nodos_filter)

        timestamps.append(datetime.strptime(ts_str, "%H:%M:%S"))
        nodos_activos_insult.append(nodos_insult)
        nodos_activos_filter.append(nodos_filter)

        # Añadir lambda al mismo timestamp si existe, sino None
        lam_insult = lambdas_tmp.get(ts_str, {}).get('InsultService', None)
        lam_filter = lambdas_tmp.get(ts_str, {}).get('InsultFilter', None)
        lambda_insult.append(lam_insult)
        lambda_filter.append(lam_filter)

    return timestamps, lambda_insult, lambda_filter, nodos_activos_insult, nodos_activos_filter

def plot_dynamic_scaling(timestamps, lambda_insult, lambda_filter, nodos_insult, nodos_filter):
    plt.figure(figsize=(12,6))
    plt.plot(timestamps, lambda_insult, 'o-', label='Lambda InsultService (pet/s)')
    plt.plot(timestamps, lambda_filter, 's-', label='Lambda InsultFilter (pet/s)')
    plt.title("Carga (lambda) dinámica medida durante test XMLRPC")
    plt.xlabel("Tiempo")
    plt.ylabel("Carga (peticiones por segundo)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("dynamic_lambda_plot.png")
    plt.close()

    plt.figure(figsize=(12,6))
    plt.plot(timestamps, nodos_insult, 'o-', label='Nodos activos InsultService')
    plt.plot(timestamps, nodos_filter, 's-', label='Nodos activos InsultFilter')
    plt.title("Número de nodos activos durante test XMLRPC")
    plt.xlabel("Tiempo")
    plt.ylabel("Número de nodos")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("dynamic_nodes_plot.png")
    plt.close()

if __name__ == "__main__":
    filename = "XMLRPC/Dynamic/test_results_d.txt"
    timestamps, lam_insult, lam_filter, nodos_insult, nodos_filter = parse_dynamic_scaling_log(filename)
    plot_dynamic_scaling(timestamps, lam_insult, lam_filter, nodos_insult, nodos_filter)
