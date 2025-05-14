import redis
import re
import time
import threading

def connect_to_redis(host='localhost', port=6379, db=0):
    """Estableix una connexió amb el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def get_all_insults(client, queue_name_insults, insults):
    """Obtén tots els insults de la cua Redis abans de començar a processar els textos."""
    while True:
        insult = client.blpop(queue_name_insults, timeout=0)  # Bloqueja fins que un insult estigui disponible
        time.sleep(0.5)
        if insult:
            insults.append(insult[1])  # Afegim l'insult a la llista
        if len(insults) > 0 and not client.llen(queue_name_insults):  # Aturar el bucle quan no hi hagi més insults
            break

def process_text(client, queue_name_text, insults):
    """Consumeix els textos i els censura si es troben insults, utilitzant una llista d'insults prèviament obtinguda."""
    #print("Consumer is waiting for tasks...")

    while True:
        task = client.blpop(queue_name_text, timeout=0)  # Blocatge fins que hi hagi un text
        if task:
            text = task[1]
            #print(f"Consumed Text: {text}")
            
            # Substituïm els insults per 'CENSORED' utilitzant expressions regulars
            for insult in insults:
                text = re.sub(r'\b' + re.escape(insult) + r'\b', "CENSORED", text)
            
            #print(f"Processed Text: {text}")
            # Aquí es podria afegir l'enviament del text censurat a una altra cua si fos necessari
            # client.rpush("PROCESSED_TEXT", text)

def main():
    client = connect_to_redis()
    queue_name_text = "TEXT"
    queue_name_insults = "INSULTS"

    # Llista compartida per als insults
    insults = []

    # Crear dos fils: un per obtenir els insults i un altre per processar els textos
    insult_thread = threading.Thread(target=get_all_insults, args=(client, queue_name_insults, insults))
    text_thread = threading.Thread(target=process_text, args=(client, queue_name_text, insults))

    # Iniciar els fils
    insult_thread.start()
    text_thread.start()

    # Esperar que els dos fils acabin
    insult_thread.join()
    text_thread.join()

if __name__ == "__main__":
    main()


