from xmlrpc.server import SimpleXMLRPCServer

# Lista de insultos
insultos = []

def recibir_insulto(insulto):
    if insulto not in insultos:
        insultos.append(insulto)
        return f"Insulto '{insulto}' añadido."
    else:
        return f"El insulto '{insulto}' ya está en la lista."


def obtener_insultos():
    return insultos

# Crear el servidor
server = SimpleXMLRPCServer(('localhost', 0))
server.register_function(recibir_insulto, 'recibir_insulto')
server.register_function(obtener_insultos, 'obtener_insultos')

print("InsultService corriendo en http://localhost:8000/")
server.serve_forever()
