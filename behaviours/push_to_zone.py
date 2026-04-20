#
# Comportamiento 4: PushToZone (prioridad más alta)
#
# CAMBIOS respecto a la versión anterior:
#   - IR_NEAR_OBJ bajado de 200 → 20 (consistente con el resto)
#   - Añadido reset de detected_object label para forzar nueva búsqueda
#

from .behaviour import Behaviour
from robobopy.utils.IR import IR

PUSH_SPEED  = 18
BACK_SPEED  = 15
PUSH_TIME   = 2.0
BACK_TIME   = 0.8
IR_NEAR_OBJ = 20    # ← AJUSTADO

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

        # Empujar hacia el contenedor
        self.robot.moveWheels(PUSH_SPEED, PUSH_SPEED)
        self.robot.wait(PUSH_TIME)

        # Retroceder
        self.robot.moveWheels(-BACK_SPEED, -BACK_SPEED)
        self.robot.wait(BACK_TIME)
        self.robot.stopMotors()

        # Resetear estado para buscar el siguiente objeto
        self.params["detected_object"] = None
        self.params["qr_centered"]     = False
        print("      ✓ Objeto depositado. Buscando siguiente...")

        for bh in self.supress_list:
            bh.supress = False