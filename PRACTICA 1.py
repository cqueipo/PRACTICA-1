"""
Implementar un merge concurrente:
- Tenemos NPROD procesos que producen números no negativos de forma
creciente. Cuando un proceso acaba de producir, produce un -1
- Hay un proceso merge que debe tomar los números y almacenarlos de
forma creciente en una única lista (o array). El proceso debe esperar a que
los productores tengan listo un elemento e introducir el menor de
ellos.
- Se debe crear listas de semáforos. Cada productor solo maneja los
sus semáforos para sus datos. El proceso merge debe manejar todos los
semáforos.
- OPCIONAL: se puede hacer un búffer de tamaño fijo de forma que
los productores ponen valores en el búffer.
"""

import random
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import Value, Array
from multiprocessing import current_process
from multiprocessing import Process


NPROD = 4 #nº productores, en este caso, 4
NCONS = 1 #nº consumidores, en este caso, 1
N = 5 #capacidad de cada productor


def menor(lista):  #función que devuelve el menor de una lista exceptuando el número -1 y su índice en la lista
    minimo = max(lista) + 1
    for k in range(len(lista)):
        if lista[k] < minimo and lista[k] != -1:
            minimo = lista[k]
            indice = k    
    return minimo, indice
    

def productor(lista, buffer, index):
     prod = 0
     for i in range(N):
         prod += random.randint(0,5)
         print (f"Productor nº{index} produciendo {prod} en iteración {i}")  
         lista[2*index].acquire() # wait empty
         buffer[index] = prod
         print('Buffer: ' +str(list(buffer)))
         lista[2*index+1].release() # signal nonEmpty
         print (f"Productor nº{index} ha almacenado {prod}")
     prod = -1
     print (f"Productor nº{index} está produciendo {prod}")        
     lista[2*index].acquire() # wait empty
     buffer[index] = prod
     lista[2*index+1].release() # signal nonEmpty
     

def consumidor(lista, buffer):  
    aux = []
    for i in range(NPROD):
        lista[2*i+1].acquire() # wait nonEmpty
    while [-1]*NPROD != list(buffer):
        prod, indice = menor(buffer)
        print('Añade', prod, ', productor nº', indice)
        aux.append(prod)
        lista[2*indice].release() # signal empty
        print (f"Consumidor consumiendo {prod}")

        lista[2*indice + 1].acquire() # wait nonEmpty
    print(aux)
    
    
def main():
     buffer = Array('i', NPROD)
     #A continuación se crea una lista de semáforos. Tenemos 2 semáforos para cada par PRODUCTOR-CONSUMIDOR 
     #lista_semaforos[2*pid] equivale al semáforo empty del productor pid
     #lista_semaforos[2*pid +1] equivale al semáforo nonEmpty del productor pid
     lista_semaforos = []
     
     for i in range(NPROD):
         lista_semaforos.append(BoundedSemaphore(1))
         lista_semaforos.append(Semaphore(0)) 
     
     lista_procesos = []
      
     for pid in range(NPROD):
         lista_procesos.append(Process(target=productor, args=(lista_semaforos, buffer, pid)))
     lista_procesos.append(Process(target=consumidor, args=(lista_semaforos, buffer)))    
     
     for p in lista_procesos:
         p.start()
     for p in lista_procesos:
         p.join()



if __name__ == "__main__":
 main()    