#
# Comportamiento 2: DetectObject (prioridad 2)
#

from .behaviour import Behaviour
from robobopy.utils.IR import IR

MIN_CONFIDENCE = 0.5
IMAGE_CENTER_X = 160   # Centro horizontal de la imagen (320px / 2)
IR_GOAL        = 20   # Valor IR que indica que el objeto está muy cerca

# Parámetros PD (mismos que Ejercicio 2)
KP = 0.05
KD = 0.1

# Límites de velocidad
speed = 8

def speed_limits(speed, min_speed=2, max_speed=10):
    if speed > max_speed:
        return max_speed
    elif speed < min_speed:
        return min_speed
    else:
        return speed

class DetectObject(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)
        self.last_error = 0

    def _read_object(self):
        obj = self.robot.readDetectedObject()
        if obj is not None and obj.label is not None and obj.confidence >= MIN_CONFIDENCE:
            return obj
        return None

    def take_control(self):
        if self.supress:
            return False
        obj = self._read_object()
        if obj is None:
            return False
        self.params["obj"] = obj
        return True

    def action(self):
        print(f"----> control: DetectObject ({self.params['obj'].label})")
        self.supress = False
        self.last_error = 0  # Resetear derivativo al tomar el control

        for bh in self.supress_list:
            bh.supress = True

        # ── Bucle continuo (igual que approach_blob_PD del Ejercicio 2) ──
        while not self.stopped():

            obj = self._read_object()

            # Si pierde el objeto, ceder a Explore
            if obj is None:
                print("      Objeto perdido, cediendo control.")
                self.robot.stopMotors()
                break

            self.params["obj"] = obj

            ir_central = self.robot.readIRSensor(IR.FrontC)

            # Si está muy cerca → parar y ceder control
            if ir_central is not None and ir_central >= IR_GOAL:
                self.robot.stopMotors()
                print(f"      Objeto alcanzado (IR={ir_central})")
                break

            # ── Control PD lateral: centra el objeto en la imagen ──
            error      = IMAGE_CENTER_X - obj.x      # + = objeto a la izq
            derivative = error - self.last_error
            correction = (error * KP) + (derivative * KD)
            correction = max(-8, min(correction, 8))
            self.last_error = error

            # ── Velocidad base ──
            speed = error * KP
            limited_speed = speed_limits(speed)

            left_speed  = limited_speed - correction
            right_speed = limited_speed + correction

            print(f"      '{obj.label}' x={obj.x} IR={ir_central} "
                  f"err={error:.1f} corr={correction:.2f}")

            self.robot.moveWheels(int(right_speed), int(left_speed))
            self.robot.wait(0.1)

        for bh in self.supress_list:
            bh.supress = False