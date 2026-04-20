from .behaviour import Behaviour
from robobopy.utils.IR import IR

MIN_CONFIDENCE  = 0.5
IMAGE_CENTER_X  = 160
CENTER_THRESH   = 25        # Margen en px para considerar QR centrado en imagen
IR_NEAR_OBJ     = 20

PAN_SPEED       = 15        # Velocidad de movimiento del pan
PAN_STEP        = 15        # Grados que avanza el pan en cada paso de búsqueda
PAN_MAX         = 150       # Límite máximo del pan (no llegar al tope)
ALIGN_SPEED     = 5         # Velocidad de giro de ruedas para alinear cuerpo
PAN_CENTER_TOL  = 10        # Grados: tolerancia para considerar pan centrado

# px → grados pan: factor empírico (imagen 320px, pan ±160°)
# Corrección proporcional: si el QR está a 'error' px del centro,
# mover el pan 'error * PX_TO_DEG' grados
PX_TO_DEG = 0.3

# qr.id es string en Recycling Simple
OBJECT_TO_QR = {
    "apple":     "ORGANIC",
    "orange":    "ORGANIC",
    "cup":       "PAPER",
    "cardboard": "PAPER",
    "bottle":    "PLASTIC",
    "can":       "PLASTIC",
}

class FindContainer(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)
        self._pan_target   = 0    # Posición pan actual de búsqueda
        self._search_dir   = 1    # +1 derecha, -1 izquierda
        self._search_steps = 0

    def take_control(self):
        if self.supress:
            return False
        obj = self.params.get("detected_object")
        if obj is None:
            return False
        front_ir = self.robot.readIRSensor(IR.FrontC)
        if front_ir is None or front_ir <= IR_NEAR_OBJ:
            return False
        if self.params.get("qr_centered", False):
            return False
        return True

    def action(self):
        print("----> control: FindContainer")
        self.supress = False

        for bh in self.supress_list:
            bh.supress = True

        obj = self.params.get("detected_object")
        if obj is None:
            for bh in self.supress_list:
                bh.supress = False
            return

        label        = obj.label.lower()
        target_qr_id = OBJECT_TO_QR.get(label)
        print(f"      Buscando QR '{target_qr_id}' para '{label}'")

        if target_qr_id is None:
            print(f"      Etiqueta '{label}' no reconocida.")
            for bh in self.supress_list:
                bh.supress = False
            return

        MAX_STEPS_PER_DIR = 10

        while not self.stopped() and not self.supress:

            # Comprobar que el objeto sigue cerca
            front_ir = self.robot.readIRSensor(IR.FrontC)
            if front_ir is None or front_ir <= IR_NEAR_OBJ:
                print("      Objeto se alejó, cediendo.")
                self.robot.movePanTo(0, PAN_SPEED, wait=False)
                self.robot.stopMotors()
                break

            qr = self.robot.readQR()
            qr_id_str = str(qr.id) if (qr is not None and qr.distance > 0) else "ninguno"

            if qr is not None and qr.distance > 0 and qr_id_str == target_qr_id:
                # QR correcto visible: mover pan para centrarlo
                error_px  = qr.x - IMAGE_CENTER_X   # + = QR a la derecha
                error_deg = error_px * PX_TO_DEG
                current_pan = self.robot.readPanPosition()
                new_pan = current_pan + error_deg
                new_pan = max(-PAN_MAX, min(PAN_MAX, new_pan))

                print(f"      QR '{qr_id_str}' x={qr.x:.0f} err={error_px:.0f}px "
                      f"pan={current_pan:.0f}→{new_pan:.0f}°")

                if abs(error_px) < CENTER_THRESH:
                    # QR centrado en imagen
                    # Ahora alinear el cuerpo girando ruedas hasta que el pan vuelva a ~0
                    print("      QR centrado en cámara. Alineando cuerpo...")
                    self._align_body_to_pan()
                    self.params["qr_centered"] = True
                    print("      ✓ Cuerpo alineado con QR.")
                    break
                else:
                    # Mover el pan hacia el QR
                    self.robot.movePanTo(int(new_pan), PAN_SPEED, wait=True)
                    self._search_steps = 0

            else:
                # QR no visible: mover el pan en la dirección de búsqueda
                current_pan = self.robot.readPanPosition()
                next_pan    = current_pan + self._search_dir * PAN_STEP
                next_pan    = max(-PAN_MAX, min(PAN_MAX, next_pan))

                print(f"      QR: '{qr_id_str}' (buscando '{target_qr_id}'), "
                      f"pan {current_pan:.0f}→{next_pan:.0f}° "
                      f"dir={'→' if self._search_dir > 0 else '←'}")

                self.robot.movePanTo(int(next_pan), PAN_SPEED, wait=True)

                self._search_steps += 1
                # Si llegamos al límite o superamos los pasos, invertir dirección
                if self._search_steps >= MAX_STEPS_PER_DIR or abs(next_pan) >= PAN_MAX:
                    self._search_dir   *= -1
                    self._search_steps  = 0
                    print("      Cambiando dirección de búsqueda.")

            self.robot.wait(0.1)

        self.robot.stopMotors()

        for bh in self.supress_list:
            bh.supress = False

    def _align_body_to_pan(self):
        """
        Gira las ruedas hasta que el pan vuelve a estar cerca de 0°,
        lo que significa que el cuerpo ahora apunta al QR.
        """
        MAX_ALIGN_STEPS = 20

        for _ in range(MAX_ALIGN_STEPS):
            pan = self.robot.readPanPosition()
            print(f"      Alineando... pan={pan:.0f}°")

            if abs(pan) < PAN_CENTER_TOL:
                break

            # Girar ruedas en la dirección del pan — moveWheels(rSpeed, lSpeed)
            if pan > 0:   # pan girado a la derecha → girar robot a la derecha
                self.robot.moveWheels(-ALIGN_SPEED, ALIGN_SPEED)
            else:         # pan girado a la izquierda → girar robot a la izquierda
                self.robot.moveWheels(ALIGN_SPEED, -ALIGN_SPEED)

            self.robot.wait(0.15)

        self.robot.stopMotors()
        # Centrar el pan para que PushToZone avance recto
        self.robot.movePanTo(0, PAN_SPEED, wait=True)