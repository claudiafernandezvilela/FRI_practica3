from .behaviour import Behaviour
import random

SPEED = 5

class Explore(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        return not self.supress

    def action(self):
        print("----> control: Explore")
        self.supress = False

        # Avanzar recto
        self.robot.moveWheels(SPEED, SPEED)
        self.robot.wait(0.3)   # ← robot.wait en lugar de time.sleep

        # Giro aleatorio
        if random.choice([True, False]):
            self.robot.moveWheels(-SPEED, SPEED)
        else:
            self.robot.moveWheels(SPEED, -SPEED)

        self.robot.wait(0.2)   # ← robot.wait en lugar de time.sleep
        self.robot.stopMotors()