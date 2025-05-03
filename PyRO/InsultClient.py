import Pyro4
import random
from Subscriber import Subscriber  # Importamos la clase Subscriber

# Conectar al servicio InsultService
ns = Pyro4.locateNS()
insult_service_uri = ns.lookup("insult.service")
insult_service = Pyro4.Proxy(insult_service_uri)

# Enviar insultos
print(insult_service.recibir_insulto("maldito"))
print(insult_service.recibir_insulto("estúpido"))

# Obtener la lista de insultos
insultos = insult_service.obtener_insultos()
print("Lista de insultos:", insultos)

# Conectar al servicio InsultFilter
insult_filter_uri = ns.lookup("insult.filter")
insult_filter = Pyro4.Proxy(insult_filter_uri)

# Enviar frases para filtrar
frase_1 = "Eres un maldito estúpido."
frase_2 = "Eres un idiota."
print(insult_filter.agregar_frase_a_cola(frase_1))
print(insult_filter.agregar_frase_a_cola(frase_2))

# Obtener los resultados filtrados
resultados = insult_filter.obtener_resultados()
print("Resultados filtrados:", resultados)

# Conectar al servicio InsultBroadcaster
insult_broadcaster_uri = ns.lookup("insult.broadcaster")
insult_broadcaster = Pyro4.Proxy(insult_broadcaster_uri)

# Suscribir a los usuarios al broadcaster
insult_broadcaster.add_subscriber("Suscriptor 1")
insult_broadcaster.add_subscriber("Suscriptor 2")
