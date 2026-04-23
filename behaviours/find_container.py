#
# Comportamiento 3: FindContainer (prioridad 3)
# Gira el robot con el objeto buscando el QR correcto.
#

from .behaviour import Behaviour
from robobopy.utils.IR import IR

IMAGE_CENTER_X = 160
CENTER_THRESH  = 25
PAN_SPEED      = 15
ALIGN_SPEED    = 3
IR_LOST        = 400

OBJECT_TO_QR = {
    "cup":    "PAPER",
    "bottle": "PLASTIC",
    "apple":  "ORGANIC",
}

class FindContainer(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        if self.supress:
            return False
        if self.params.get("detected_object") is None:
            return False
        if self.params.get("qr_centered", False):
            return False
        return True

    def _object_lost(self):
        """Comprueba si el objeto se ha alejado del pusher."""
        ir_front_c = self.robot.readIRSensor(IR.FrontC)
        ir_front_l = self.robot.readIRSensor(IR.FrontL)
        ir_front_r = self.robot.readIRSensor(IR.FrontR)
        ir_value = max(ir_front_c or 0, ir_front_l or 0, ir_front_r or 0)
        return ir_value < IR_LOST

    def action(self):
        print("----> control: FindContainer")
        self.supress = False

        for bh in self.supress_list:
            bh.supress = True

        self.robot.movePanTo(0, PAN_SPEED, wait=True)

        label     = self.params["detected_object"].label.lower()
        target_qr = OBJECT_TO_QR.get(label)
        print(f"      Buscando QR '{target_qr}' para '{label}'")

        while not self.stopped():

            # Comprobar que el objeto sigue cerca
            if self._object_lost():
                print("      Objeto perdido, volviendo a DetectObject.")
                self.robot.stopMotors()
                self.params["objeto_cerca"]    = False
                self.params["detected_object"] = None
                for bh in self.supress_list:
                    bh.supress = False
                return

            qr = self.robot.readQR()

            if qr is not None and qr.distance > 0 and str(qr.id) == target_qr:
                error = qr.x - IMAGE_CENTER_X
                print(f"      QR x={qr.x} error={error:.0f}")

                if abs(error) < CENTER_THRESH:
                    self.robot.stopMotors()
                    self.params["qr_centered"] = True
                    print("      Listo, cuerpo alineado con QR.")
                    for bh in self.supress_list:
                        bh.supress = False
                    return

                if error > 0:
                    self.robot.moveWheels(ALIGN_SPEED, -ALIGN_SPEED)
                else:
                    self.robot.moveWheels(-ALIGN_SPEED, ALIGN_SPEED)

            else:
                # QR no visible, barrer izquierda y derecha
                for _ in range(180):
                    if self._object_lost():
                        break
                    self.robot.moveWheels(-ALIGN_SPEED, ALIGN_SPEED)
                    self.robot.wait(0.1)
                    qr = self.robot.readQR()
                    if qr is not None and qr.distance > 0 and str(qr.id) == target_qr:
                        break
                for _ in range(180):
                    if self._object_lost():
                        break
                    self.robot.moveWheels(ALIGN_SPEED, -ALIGN_SPEED)
                    self.robot.wait(0.1)
                    qr = self.robot.readQR()
                    if qr is not None and qr.distance > 0 and str(qr.id) == target_qr:
                        break

            self.robot.wait(0.1)

        for bh in self.supress_list:
            bh.supress = False