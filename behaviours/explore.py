#
# Comportamiento: Explore (prioridad más baja)
#

from .behaviour import Behaviour
import random

SPEED = 10  # Velocidad de exploración

class Explore(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        """Siempre toma el control si no está suprimido (comportamiento base)."""
        return not self.supress

    def action(self):
        print("----> control: Explore")
        self.supress = False

        # Suprimir comportamientos de menor prioridad (ninguno en este caso)
        for bh in self.supress_list:
            bh.supress = True

        # Avanzar recto
        self.robot.moveWheels(SPEED, SPEED)
        self.robot.wait(1.5)

        # Giro aleatorio para explorar nuevas direcciones
        direccion = random.choice(["izquierda", "derecha"])
        if direccion == "izquierda":
            self.robot.moveWheels(-SPEED, SPEED)
        else:
            self.robot.moveWheels(SPEED, -SPEED)

        self.robot.wait(random.uniform(0.5, 1.2))

        self.robot.stopMotors()

        # Liberar supresión
        for bh in self.supress_list:
            bh.supress = False