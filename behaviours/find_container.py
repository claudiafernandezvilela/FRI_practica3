#
# Comportamiento 3: FindContainer (prioridad 3)
# Gira el pan buscando el QR correcto y luego alinea el robot.
#

from .behaviour import Behaviour

IMAGE_CENTER_X = 160
CENTER_THRESH  = 25
PAN_SPEED      = 15
PAN_STEP       = 15
PAN_MAX        = 150
ALIGN_SPEED    = 3    # suave para no pasarse
PAN_CENTER_TOL = 20   # para antes

OBJECT_TO_QR = {
    "cup":       "PAPER",
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

    def action(self):
        print("----> control: FindContainer")
        self.supress = False

        for bh in self.supress_list:
            bh.supress = True

        label      = self.params["detected_object"].label.lower()
        target_qr  = OBJECT_TO_QR.get(label)
        print(f"      Buscando QR '{target_qr}' para '{label}'")

        # Girar el pan barriendo izquierda a derecha buscando el QR
        while not self.stopped():
            for pan_pos in list(range(0, PAN_MAX, PAN_STEP)) + list(range(PAN_MAX, -PAN_MAX, -PAN_STEP)) + list(range(-PAN_MAX, 0, PAN_STEP)):
                self.robot.movePanTo(pan_pos, PAN_SPEED, wait=True)

                qr = self.robot.readQR()
                if qr is not None and qr.distance > 0 and str(qr.id) == target_qr:
                    print(f"      QR '{target_qr}' encontrado, centrando...")

                    # Centrar el pan sobre el QR
                    error_px = qr.x - IMAGE_CENTER_X
                    new_pan  = pan_pos + error_px * 0.3
                    new_pan  = max(-PAN_MAX, min(PAN_MAX, new_pan))
                    self.robot.movePanTo(int(new_pan), PAN_SPEED, wait=True)

                    # Alinear el cuerpo girando ruedas hasta que pan ≈ 0
                    for _ in range(30):
                        pan = self.robot.readPanPosition()
                        print(f"      Alineando pan={pan:.0f}°")
                        if abs(pan) < PAN_CENTER_TOL:
                            break
                        if pan > 0:
                            self.robot.moveWheels(-ALIGN_SPEED, ALIGN_SPEED)
                        else:
                            self.robot.moveWheels(ALIGN_SPEED, -ALIGN_SPEED)
                        self.robot.wait(0.1)

                    self.robot.stopMotors()
                    self.robot.movePanTo(0, PAN_SPEED, wait=True)
                    self.params["qr_centered"] = True
                    print("      Listo, cuerpo alineado con QR.")

                    for bh in self.supress_list:
                        bh.supress = False
                    return

        for bh in self.supress_list:
            bh.supress = False