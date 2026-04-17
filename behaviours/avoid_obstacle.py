#
# Comportamiento: Evitar Obstáculos (prioridad MÁS ALTA)
# Usa los sensores IR para detectar paredes u obstáculos cercanos.
# Cuando detecta un obstáculo, suprime TODOS los demás comportamientos
# y maniobra para alejarse.
#

from .behaviour import Behaviour
import time
from robobopy.utils.IR import IR

# Umbral IR a partir del cual se considera que hay un obstáculo cercano
IR_THRESHOLD = 80

# Velocidad de maniobra de escape
ESCAPE_SPEED = 12

class AvoidObstacle(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def _read_front_ir(self):
        """Lee los sensores IR frontales (centro-izquierda y centro-derecha)."""
        front_left  = self.robot.readIRSensor(IR.FrontL)
        front_right = self.robot.readIRSensor(IR.FrontR)
        front_c     = self.robot.readIRSensor(IR.FrontC)
        return front_left, front_right, front_c

    def take_control(self):
        """Toma control si algún sensor IR frontal supera el umbral."""
        fl, fr, fc = self._read_front_ir()
        return fl > IR_THRESHOLD or fr > IR_THRESHOLD or fc > IR_THRESHOLD

    def action(self):
        print("----> control: Evitar Obstáculo")

        # Suprimir TODOS los comportamientos de menor prioridad
        for bh in self.supress_list:
            bh.supress = True

        fl, fr, fc = self._read_front_ir()
        print(f"      IR: FL={fl:.0f}, FC={fc:.0f}, FR={fr:.0f}")

        # Retroceder un poco
        self.robot.moveWheels(-ESCAPE_SPEED, -ESCAPE_SPEED)
        time.sleep(0.4)
        self.robot.stopMotors()

        # Girar en la dirección contraria al obstáculo
        if fl >= fr:
            # Obstáculo más a la izquierda → girar a la derecha
            self.robot.moveWheels(ESCAPE_SPEED, -ESCAPE_SPEED)
        else:
            # Obstáculo más a la derecha → girar a la izquierda
            self.robot.moveWheels(-ESCAPE_SPEED, ESCAPE_SPEED)

        time.sleep(0.5)
        self.robot.stopMotors()

        # Liberar supresión de todos
        for bh in self.supress_list:
            bh.supress = False