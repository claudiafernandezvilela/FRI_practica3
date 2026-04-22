from .behaviour import Behaviour

SPEED      = 5
TURN_SPEED = 5
TURN_TIME  = 2  # ajustar según pruebas

class Explore(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        return not self.supress

    def action(self):
        print("----> control: Explore")
        self.supress = False

        # Girar derecha, centro, izquierda, centro
        # Derecha
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

        # Avanzar un poco para cambiar de posición
        self.robot.moveWheels(SPEED, SPEED)
        self.robot.wait(0.5)
        self.robot.stopMotors()