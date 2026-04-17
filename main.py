#
#  Ejemplo de uso de threads para el desarrollo de arquitecturas reactivas (subsumida)
#

from robobopy.Robobo import Robobo

from behaviours.behaviour import Behaviour

from behaviours.orient_to_object import OrientToObject
from behaviours.push_object import PushObject
from behaviours.detect_object import DetectObject
from behaviours.explore import Explore
from behaviours.avoid_obstacle import AvoidObstacle
from behaviours.decide_container import DecideContainer

import time

def main():
    robobo = Robobo("localhost")
    robobo.connect()

    # Diccionario que se pasará a los comportamientos
    # para que lo activen cuando se finalice la misión
    params = {
        "stop":               False,   # Poner a True para detener todos los hilos
        "objeto_detectado":   False,   # Se activa cuando DetectObject ve un blob
        "objeto_color":       None,    # BlobColor del objeto detectado
        "objeto_color_str":   "",      # Nombre legible del color
        "objeto_posx":        50,      # Posición X del blob (0-100)
        "contenedor_decidido":False,   # Se activa cuando DecideContainer decide
        "contenedor_color":   None,    # BlobColor del contenedor destino
        "listo_para_empujar": False,   # Se activa cuando OrientToObject centra el objeto
    }

    # Creación de los comportamientos
    explore = Explore(robobo, [], params)
    detect = DetectObject(robobo, [explore], params)
    decide = DecideContainer(robobo, [explore, detect], params)
    orient = OrientToObject(robobo, [explore, detect, decide], params)
    push = PushObject(robobo, [explore, detect, decide, orient], params)
    #avoid = AvoidObstacle(robobo, [explore, detect, decide, orient, push], params)
 
    
    threads = [explore, detect, decide, orient, push]

    # Se inician todos los comportamientos
    for t in threads:
        t.start()
 
    print("Arquitectura subsumida iniciada. Esperando fin de misión...")

    # Se mantiene el hilo principal en espera
    # hasta que algún comportamiento marca
    # el objetivo como terminado
    while not params["stop"]:
        time.sleep(0.1)

    # Espera a que terminen todos los hilos
    for thread in threads:
        thread.join()

    robobo.disconnect()

if __name__ == "__main__":
    main()
