# find_container.py

from .behaviour import Behaviour
from robobopy.utils.IR import IR

IMAGE_CENTER_X = 250
CENTER_THRESH  = 50
ALIGN_SPEED    = 2

OBJECT_TO_QR = {
    "cup":    "Paper",
    "bottle": "Plastic",
    "apple":  "Organic",
    "dog": "Paper",
    "orange": "Organic"
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

        self.robot.moveTiltTo(80, 60)
        self.robot.movePanTo(0, 15, wait=True)
        self.robot.wait(1)

        label     = self.params["detected_object"].label.lower()
        target_qr = OBJECT_TO_QR.get(label)
        print(f"      Buscando QR '{target_qr}' para '{label}'")

        while not self.stopped():
            qr = self.robot.readQR()

            if qr is not None and qr.distance > 0 and str(qr.id) == target_qr:
                error = qr.x - IMAGE_CENTER_X
                print(f"      QR encontrado x={qr.x} error={error:.0f}")

                if abs(error) < CENTER_THRESH:
                    self.robot.stopMotors()
                    self.params["qr_centered"] = True
                    print("      Cuerpo alineado con QR.")
                    for bh in self.supress_list:
                        bh.supress = False
                    return

                # Girar hacia el QR
                if error > 0:
                    self.robot.moveWheels(ALIGN_SPEED, -ALIGN_SPEED)
                else:
                    self.robot.moveWheels(-ALIGN_SPEED, ALIGN_SPEED)

                self.robot.wait(0.1)

            else:
                # QR no visible: barrer lentamente, 0.1s por paso
                print(f"      QR no visible, barriendo...")
                found = False

                # Barrer izquierda (máx 3 segundos)
                for _ in range(60):
                    if self.stopped():
                        break
                    self.robot.moveWheels(-ALIGN_SPEED, ALIGN_SPEED)
                    self.robot.wait(0.1)
                    qr = self.robot.readQR()
                    if qr is not None and qr.distance > 0 and str(qr.id) == target_qr:
                        found = True
                        break

                if not found:
                    # Barrer derecha (máx 6 segundos para cubrir ambos lados)
                    for _ in range(60):
                        if self.stopped():
                            break
                        self.robot.moveWheels(ALIGN_SPEED, -ALIGN_SPEED)
                        self.robot.wait(0.1)
                        qr = self.robot.readQR()
                        if qr is not None and qr.distance > 0 and str(qr.id) == target_qr:
                            found = True
                            break

                if not found:
                    # Volver al centro y repetir
                    self.robot.moveWheels(-ALIGN_SPEED, ALIGN_SPEED)
                    self.robot.wait(1.5)
                    self.robot.stopMotors()

            self.robot.wait(0.1)

        for bh in self.supress_list:
            bh.supress = False