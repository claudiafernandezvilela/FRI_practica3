from .behaviour import Behaviour
from robobopy.utils.IR import IR
import time

class GoToObject(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

        self.goal = 80   # distancia IR objetivo (como en tu ejercicio)

    def take_control(self):
        if self.supress:
            return False

        return self.params.get("objeto_detectado", False)

    def action(self):
        print("----> control: Go To Object")

        self.supress = False

        for bh in self.supress_list:
            bh.supress = True

        obj = self.robot.readObject()

        if not obj:
            # objeto perdido
            self.params["objeto_detectado"] = False
            for bh in self.supress_list:
                bh.supress = False
            return

        # 🔴 1. CONTROL DE DISTANCIA (IR)
        distance = self.robot.readIRSensor(IR.FrontC)

        if distance >= self.goal:
            self.robot.stopMotors()
            print("      Cerca del objeto")
            self.params["listo_para_empujar"] = True

        else:
            error = 50 - obj.posx   # centro = 50

            if error > 10:
                # objeto a la izquierda
                self.robot.moveWheels(-5, 5)

            elif error < -10:
                # objeto a la derecha
                self.robot.moveWheels(5, -5)

            else:
                # centrado → avanzar
                self.robot.moveWheels(10, 10)

        time.sleep(0.1)
        self.robot.stopMotors()

        for bh in self.supress_list:
            bh.supress = False