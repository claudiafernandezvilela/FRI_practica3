from .behaviour import Behaviour
from robobopy.utils.IR import IR

class AvoidWall(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)
        self.front_distance = 100  # IR para activarse
        self.goal = 75             # IR para parar

    def take_control(self):
        if self.supress:
            return False
        if self.robot.readIRSensor(IR.FrontC) < self.front_distance:
            return False

        # IR alto — comprobar si es el contenedor o una pared
        qr = self.robot.readQR()
        if qr is not None and qr.distance > 0:
            # Hay QR visible → es el contenedor, no esquivar
            return False

        return True

    def action(self):
        print("----> control: AvoidWall")
        self.supress = False

        for bh in self.supress_list:
            bh.supress = True

        speed = 5
        if self.robot.readIRSensor(IR.FrontR) >= self.goal:
            self.robot.moveWheels(speed, -speed)
        else:
            self.robot.moveWheels(-speed, speed)

        self.robot.wait(1.0)
        self.robot.stopMotors()

        for bh in self.supress_list:
            bh.supress = False