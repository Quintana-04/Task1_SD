import Pyro4

# Lista de insultos
insultos = []

@Pyro4.expose
class InsultService:
    def recibir_insulto(self, insulto):
        if insulto not in insultos:
            insultos.append(insulto)
            return f"Insulto '{insulto}' añadido."
        else:
            return f"El insulto '{insulto}' ya está en la lista."
    
    def obtener_insultos(self):
        return insultos


# Configuración del servidor Pyro
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()

# Crear y registrar el objeto
insult_service = InsultService()
uri = daemon.register(insult_service)
ns.register("insult.service", uri)

print("InsultService corriendo...")
daemon.requestLoop()
