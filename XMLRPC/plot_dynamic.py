import re
import matplotlib.pyplot as plt
from datetime import datetime

def parse_dynamic_log(filename):
    timestamps = []
    lambda_insult = []
    lambda_filter = []
    nodos_insult = []
    nodos_filter = []

    with open(filename, 'r', encoding='latin-1') as f:
        content = f.read()

    # Patrón para bloques con lambda y nodos requeridos
    patron_lambda = re.compile(
        r"\[(\d{2}:\d{2}:\d{2})\] (InsultService|InsultFilter):\n"
        r"  - Carga medida \(lambda\): ([\d\.]+) pet/s\n"
        r"  - Fórmula usada: .*\n"
        r"  - Nodos actuales: (\d+)\n"
        r"  - Nodos requeridos: \d+ => Se decide (aumentar|disminuir|mantener) nodos"
    )

    # Patrón para estado post-escalado
    patron_estado = re.compile(
        r"\[(\d{2}:\d{2}:\d{2})\] Estado post-escalado:\n"
        r"  - InsultService nodos activos: (\d+)\n"
        r"  - InsultFilter nodos activos: (\d+)"
    )

    # Diccionarios temporales para lambda con timestamp como clave
    lambda_tmp = {}

    for m in patron_lambda.finditer(content):
        ts_str, servicio, lam, nodos_actuales, decision = m.groups()
        lam = float(lam)
        lambda_tmp.setdefault(ts_str, {})[servicio] = lam

    for m in patron_estado.finditer(content):
        ts_str, nodos_i, nodos_f = m.groups()
        timestamps.append(datetime.strptime(ts_str, "%H:%M:%S"))
        nodos_insult.append(int(nodos_i))
        nodos_filter.append(int(nodos_f))
        lambda_insult.append(lambda_tmp.get(ts_str, {}).get('InsultService', None))
        lambda_filter.append(lambda_tmp.get(ts_str, {}).get('InsultFilter', None))

    return timestamps, lambda_insult, lambda_filter, nodos_insult, nodos_filter

def plot_results(timestamps, lambda_i, lambda_f, nodos_i, nodos_f):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, lambda_i, 'o-', label='Lambda InsultService (pet/s)')
    plt.plot(timestamps, lambda_f, 's-', label='Lambda InsultFilter (pet/s)')
    plt.title("Carga (lambda) medida durante test de escalado dinámico XMLRPC")
    plt.xlabel("Tiempo")
    plt.ylabel("Carga (peticiones/segundo)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("dynamic_lambda_xmlrpc.png")
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, nodos_i, 'o-', label='Nodos activos InsultService')
    plt.plot(timestamps, nodos_f, 's-', label='Nodos activos InsultFilter')
    plt.title("Número de nodos activos durante test de escalado dinámico XMLRPC")
    plt.xlabel("Tiempo")
    plt.ylabel("Nodos activos")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("dynamic_nodos_xmlrpc.png")
    plt.close()

if __name__ == "__main__":
    archivo = "XMLRPC/Dynamic/test_results_d.txt"
    ts, lam_i, lam_f, nodos_i, nodos_f = parse_dynamic_log(archivo)
    plot_results(ts, lam_i, lam_f, nodos_i, nodos_f)
