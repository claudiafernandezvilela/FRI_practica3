#
# Comportamiento 2: DetectObject (prioridad 2)
#

from .behaviour import Behaviour
from robobopy.utils.IR import IR

MIN_CONFIDENCE = 0.5
IMAGE_CENTER_X = 250
IR_GOAL        = 20
IR_CONTACT     = 800

# Parámetros PD
KP = 0.04
KD = 0.9

# Velocidad base de avance
BASE_SPEED = 6

TARGET_LABELS = { "bottle", "cup", "orange"}

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

class DetectObject(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)
        self.last_error = 0

    def _read_object(self):
        obj = self.robot.readDetectedObject()
        if obj is not None and obj.label is not None \
                and obj.confidence >= MIN_CONFIDENCE \
                and obj.label.lower() in TARGET_LABELS \
                and obj.label.lower() not in self.params.get("depositados", set()):
            return obj
        return None

    def _center_on_object(self):
        """Gira el robot hasta centrar el objeto en imagen con control PD."""
        print("      Centrando objeto...")
        CENTER_X  = 250
        DEAD_ZONE = 15
        MAX_SPEED = 3
        MIN_SPEED = 1
        KP        = 0.08
        KD        = 0.5
        last_err  = 0

        while not self.stopped():
            obj = self._read_object()
            if obj is None or obj.x == 0:
                break

            error      = obj.x - CENTER_X
            derivative = error - last_err
            last_err   = error

            if abs(error) < DEAD_ZONE:
                self.robot.stopMotors()
                print(f"      Objeto centrado (x={obj.x})")
                break

            correction = (error * KP) + (derivative * KD)
            speed = max(MIN_SPEED, min(MAX_SPEED, int(abs(correction))))

            if correction > 0:
                self.robot.moveWheels(speed, -speed)  # girar derecha
            else:
                self.robot.moveWheels(-speed, speed)  # girar izquierda

            self.robot.wait(0.15)

    def _approach_final(self):
        """Avanza despacio hasta contacto real con el objeto."""
        print("      Modo approach final...")
        while not self.stopped():
            ir_front_c = self.robot.readIRSensor(IR.FrontC)
            ir_front_l = self.robot.readIRSensor(IR.FrontL)
            ir_front_r = self.robot.readIRSensor(IR.FrontR)
            ir_value = max(ir_front_c or 0, ir_front_l or 0, ir_front_r or 0)

            print(f"      approach_final IR={ir_value}")

            if ir_value >= IR_CONTACT:
                self.robot.stopMotors()
                self.params["objeto_cerca"] = True
                self.params["detected_object"] = self.params["obj"]
                print(f"      Contacto con objeto (IR={ir_value})")
                break

            self.robot.moveWheels(5, 5)
            self.robot.wait(0.1)

    def take_control(self):
        if self.supress:
            return False
        if self.params.get("objeto_cerca"):
            return False
        obj = self._read_object()
        if obj is None:
            return False
        self.params["obj"] = obj
        return True

    def action(self):
        if self.params.get("objeto_cerca"):
            return

        print(f"----> control: DetectObject ({self.params['obj'].label})")
        self.supress = False
        self.last_error = 0

        for bh in self.supress_list:
            bh.supress = True

        # Centrar robot sobre el objeto antes de avanzar
        self._center_on_object()

        while not self.stopped():

            obj = self._read_object()

            if obj is None:
                print("      Objeto perdido, cediendo control.")
                self.robot.stopMotors()
                break

            self.params["obj"] = obj
            ir_central = self.robot.readIRSensor(IR.FrontC)

            if ir_central is not None and ir_central >= IR_GOAL:
                self.robot.stopMotors()
                self._approach_final()
                break

            if obj.x == 0:
                self.robot.moveWheels(BASE_SPEED, -BASE_SPEED)
                self.robot.wait(0.1)
                continue

            error      = IMAGE_CENTER_X - obj.x
            derivative = error - self.last_error
            correction = clamp((error * KP) + (derivative * KD), -BASE_SPEED, BASE_SPEED)
            self.last_error = error

            left_speed  = clamp(BASE_SPEED + correction, -BASE_SPEED, BASE_SPEED)
            right_speed = clamp(BASE_SPEED - correction, -BASE_SPEED, BASE_SPEED)

            print(f"      '{obj.label}' x={obj.x} IR={ir_central} "
                  f"err={error:.1f} corr={correction:.2f} "
                  f"L={left_speed:.1f} R={right_speed:.1f}")

            self.robot.moveWheels(int(right_speed), int(left_speed))
            self.robot.wait(0.1)

        for bh in self.supress_list:
            bh.supress = False