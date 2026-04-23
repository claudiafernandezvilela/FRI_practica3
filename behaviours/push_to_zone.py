#
# Comportamiento 4: PushToZone (prioridad más alta)
# Empuja el objeto hacia el contenedor hasta que el QR esté muy cerca.
# Si pierde el QR, cede el control a FindContainer.
#

from .behaviour import Behaviour
from robobopy.utils.IR import IR

PUSH_SPEED   = 15
BACK_SPEED   = 6
BACK_TIME    = 2
IR_NEAR_OBJ  = 5
QR_DISTANCE  = 100

class PushToZone(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        if self.supress:
            return False
        front_ir = self.robot.readIRSensor(IR.FrontC)
        return (self.params.get("qr_centered", False)
                and front_ir is not None
                and front_ir > IR_NEAR_OBJ)

    def action(self):
        print("----> control: PushToZone → empujando")
        self.supress = False

        for bh in self.supress_list:
            bh.supress = True

        while not self.stopped():
            qr = self.robot.readQR()
            if qr is not None and qr.distance > 0:
                print(f"      push QR distance={qr.distance:.1f} x={qr.x}")
                if qr.distance > QR_DISTANCE:
                    self.robot.stopMotors()
                    print("      Llegado al contenedor.")
                    break

                error = qr.x - 200
                if error > 20:
                    self.robot.moveWheels(PUSH_SPEED, PUSH_SPEED - 5)
                elif error < -20:
                    self.robot.moveWheels(PUSH_SPEED - 5, PUSH_SPEED)
                else:
                    self.robot.moveWheels(PUSH_SPEED, PUSH_SPEED)
            else:
                self.robot.stopMotors()
                print("      QR perdido, volviendo a FindContainer.")
                self.params["qr_centered"] = False
                for bh in self.supress_list:
                    bh.supress = False
                return

            self.robot.wait(0.1)

        # Retroceder del contenedor
        self.robot.moveWheels(-BACK_SPEED, -BACK_SPEED)
        self.robot.wait(BACK_TIME)
        self.robot.stopMotors()

        # Girar 180° para mirar hacia los objetos
        self.robot.moveWheels(BACK_SPEED, -BACK_SPEED)
        self.robot.wait(4)  # ajustar según pruebas
        self.robot.stopMotors()

        # Añadir a depositados
        label = self.params["detected_object"].label.lower()
        self.params["depositados"].add(label)
        print(f"      Objeto '{label}' depositado. Total: {self.params['depositados']}")

        # Resetear estado
        self.params["detected_object"] = None
        self.params["qr_centered"]     = False
        self.params["objeto_cerca"]    = False
        self.params["obj"]             = None

        # Parar si ya están todos
        if self.params["depositados"] >= {"cup", "bottle", "apple"}:
            print("      Todos los objetos depositados.")
            self.params["stop"] = True
        else:
            print("      Buscando siguiente objeto...")

        for bh in self.supress_list:
            bh.supress = False