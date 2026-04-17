#
# Comportamiento: Orientarse al Objeto (prioridad 4)
#

from .behaviour import Behaviour
from robobopy.utils.BlobColor import BlobColor
import time

# Centro de la imagen (la posición X del blob va de 0 a 100)
CENTER = 50
# Margen de error aceptable (en unidades de posición del blob)
CENTER_MARGIN = 8
# Ganancia proporcional para el giro
KP = 0.3
# Velocidad base de giro
TURN_SPEED_BASE = 5
# Tamaño mínimo del blob para considerar que estamos suficientemente cerca
PUSH_SIZE_THRESHOLD = 40

class OrientToObject(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        if self.supress:
            return False
        return (self.params.get("objeto_detectado", False) and
                self.params.get("contenedor_decidido", False) and
                not self.params.get("listo_para_empujar", False))

    def action(self):
        print("----> control: Orientarse al Objeto")
        self.supress = False

        # Suprimir comportamientos de menor prioridad
        for bh in self.supress_list:
            bh.supress = True

        color = self.params.get("objeto_color")
        if color is None:
            for bh in self.supress_list:
                bh.supress = False
            return

        blob = self.robot.readColorBlob(color)

        if blob is None or blob.size <= 0:
            # Objeto perdido, resetear
            self.params["objeto_detectado"] = False
            self.params["contenedor_decidido"] = False
            print("      Objeto perdido durante orientación.")
        else:
            error = blob.posx - CENTER
            print(f"      Orientando... posX={blob.posx}, error={error}, size={blob.size}")

            if abs(error) <= CENTER_MARGIN:
                # Objeto centrado
                self.robot.stopMotors()
                if blob.size >= PUSH_SIZE_THRESHOLD:
                    # Estamos cerca y centrados: listos para empujar
                    self.params["listo_para_empujar"] = True
                    print("      ¡Objeto centrado y cerca! Listo para empujar.")
                else:
                    # Centrado pero lejos: avanzar hacia él
                    self.robot.moveWheels(12, 12)
                    time.sleep(0.2)
                    self.robot.stopMotors()
            else:
                # Girar proporcionalmente hacia el objeto
                turn = KP * error
                left_speed  = TURN_SPEED_BASE + turn
                right_speed = TURN_SPEED_BASE - turn
                self.robot.moveWheels(left_speed, right_speed)
                time.sleep(0.1)
                self.robot.stopMotors()

        time.sleep(0.05)

        # Liberar supresión
        for bh in self.supress_list:
            bh.supress = False