import redis
import re
import time

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def get_all_insults(client, queue_name_insults):
    """Obtén tots els insults de la cua Redis abans de començar a processar els textos."""
    insults = []
    while True:
        insult = client.blpop(queue_name_insults, timeout=0)  # Bloqueja fins que un insult estigui disponible
        time.sleep(0.5)
        if insult:
            insults.append(insult[1])  # Afegim l'insult a la llista
        # Aturem el bucle només quan no hi hagi més insults a la cua (quan es buida)
        if len(insults) > 0 and not client.llen(queue_name_insults):  # Es comprova si la cua està buida
            break
    return insults

def process_text(client, queue_name_text, queue_name_insults):
    """Consumeix els textos i els censura si es troben insults, utilitzant una llista d'insults prèviament obtinguda."""
    print("Consumer is waiting for tasks...")
    
    # Primer obtenim tots els insults de la cua
    insults = get_all_insults(client, queue_name_insults)
    print(f"Insults obtained: {insults}")

    while True:
        task = client.blpop(queue_name_text, timeout=0)  # Blocatge fins que hi hagi un text
        if task:
            text = task[1]
            print(f"Consumed Text: {text}")
            
            # Substituïm els insults per 'CENSORED' utilitzant expressions regulars
            for insult in insults:
                # Fem servir re.sub per substituir la paraula insult, independentment de les altres paraules
                text = re.sub(r'\b' + re.escape(insult) + r'\b', "CENSORED", text)
            
            print(f"Processed Text: {text}")
            # Aquí es podria afegir l'enviament del text censurat a una altra cua si fos necessari
            # client.rpush("PROCESSED_TEXT", text)

# Codi principal
client = connect_to_redis()
queue_name_text = "TEXT"
queue_name_insults = "INSULTS"
process_text(client, queue_name_text, queue_name_insults)


