from .behaviour import Behaviour
import random

SPEED      = 3
TURN_SPEED = 2
TURN_TIME  = 7

class Explore(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        return not self.supress

    def action(self):
        print("----> control: Explore")
        self.supress = False

        self.robot.moveTiltTo(100, 60)

        # Girar derecha
        self.robot.moveWheels(TURN_SPEED, -TURN_SPEED)
        self.robot.wait(TURN_TIME)
        self.robot.stopMotors()

        # Volver al centro
        self.robot.moveWheels(-TURN_SPEED, TURN_SPEED)
        self.robot.wait(TURN_TIME)
        self.robot.stopMotors()

        # Izquierda
        self.robot.moveWheels(-TURN_SPEED, TURN_SPEED)
        self.robot.wait(TURN_TIME)
        self.robot.stopMotors()

        # Volver al centro
        self.robot.moveWheels(TURN_SPEED, -TURN_SPEED)
        self.robot.wait(TURN_TIME)
        self.robot.stopMotors()

        # Avanzar con giro aleatorio para cambiar de posición
        turn_time = random.uniform(0.5, 8.0)  # giro aleatorio entre 0.5 y 2 segundos
        if random.choice([True, False]):
            self.robot.moveWheels(TURN_SPEED, -TURN_SPEED)  # girar derecha
        else:
            self.robot.moveWheels(-TURN_SPEED, TURN_SPEED)  # girar izquierda
        self.robot.wait(turn_time)
        self.robot.stopMotors()

        # Avanzar recto
        self.robot.moveWheels(SPEED, SPEED)
        self.robot.wait(4)
        self.robot.stopMotors()