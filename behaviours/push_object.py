#
# Comportamiento: Empujar Objeto (prioridad 5)
#

from .behaviour import Behaviour
from robobopy.utils.BlobColor import BlobColor
import time

PUSH_SPEED = 12             # Velocidad de empuje
CONTAINER_SIZE_GOAL = 50    # Tamaño del blob del contenedor que indica "llegamos"
CENTER = 50
CENTER_MARGIN = 10
KP_CONTAINER = 0.3

class PushObject(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        """Toma control cuando estamos listos para empujar y no suprimido."""
        if self.supress:
            return False
        return self.params.get("listo_para_empujar", False)

    def action(self):
        print("----> control: Empujar Objeto")
        self.supress = False

        # Suprimir comportamientos de menor prioridad
        for bh in self.supress_list:
            bh.supress = True

        contenedor_color = self.params.get("contenedor_color")

        # Avanzar empujando el objeto
        self.robot.moveWheels(PUSH_SPEED, PUSH_SPEED)
        time.sleep(0.3)
        self.robot.stopMotors()

        # Comprobar si hemos llegado al contenedor
        if contenedor_color is not None:
            blob_cont = self.robot.readColorBlob(contenedor_color)
            if blob_cont is not None and blob_cont.size >= CONTAINER_SIZE_GOAL:
                print("      ¡OBJETO DEPOSITADO EN EL CONTENEDOR! Misión cumplida.")
                self.robot.stopMotors()
                # Resetear estado para buscar el siguiente objeto
                self.params["objeto_detectado"] = False
                self.params["contenedor_decidido"] = False
                self.params["listo_para_empujar"] = False
                self.params["objeto_color"] = None
                # Si quieres parar completamente: self.set_stop()
            else:
                # Corregir dirección hacia el contenedor si se ve
                if blob_cont is not None and blob_cont.size > 5:
                    error = blob_cont.posx - CENTER
                    if abs(error) > CENTER_MARGIN:
                        turn = KP_CONTAINER * error
                        self.robot.moveWheels(PUSH_SPEED + turn, PUSH_SPEED - turn)
                        time.sleep(0.15)
                        self.robot.stopMotors()

        time.sleep(0.05)

        # Liberar supresión
        for bh in self.supress_list:
            bh.supress = False