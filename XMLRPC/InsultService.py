import argparse
from xmlrpc.server import SimpleXMLRPCServer

insultos = []

def recibir_insulto(insulto):
    if insulto not in insultos:
        insultos.append(insulto)
        return f"Insulto '{insulto}' añadido."
    else:
        return f"El insulto '{insulto}' ya está en la lista."


def obtener_insultos():
    return insultos

def run_server(port):
    server = SimpleXMLRPCServer(('localhost', port))
    server.register_function(recibir_insulto, 'recibir_insulto')
    server.register_function(obtener_insultos, 'obtener_insultos')

    print(f"InsultService corriendo en http://localhost:{port}/")
    server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Iniciar el servicio InsultService en el puerto especificado.")
    parser.add_argument('port', type=int, help="Número de puerto en el que el servidor escuchará.")
    args = parser.parse_args()

    run_server(args.port)